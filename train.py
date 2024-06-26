import datetime
import os.path as osp
import torch
import numpy as np
import tqdm
import math
import utils
import os
import shutil
import matplotlib.pyplot as plt
from models.fcnresnet import DenseFCNResNet152,ResFCNResNet152
from AccumulatorSpace import estimate_6d_pose_lm, estimate_6d_pose_lmo, test_ckpt




class Trainer():
    def __init__(self, data_loader, opts, vis = None):
        self.opts = opts
        self.train_loader = data_loader[0]
        self.val_loader = data_loader[1]
        self.scheduler = []

        self.out = os.path.join(opts.out, "kpt_" + opts.kpt_num)
        self.epoch = 0
        self.iteration = 0

        if opts.mode in ['test', 'demo']:
            self.Test()
            return
        
        use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda" if use_cuda else "cpu")
        self.model = DenseFCNResNet152(3,2)
        if torch.cuda.device_count() > 1:
            print("Using", torch.cuda.device_count(), "GPUs!")
            self.model = torch.nn.DataParallel(self.model)
            self.model.to(self.device)
        else:
            print("Using", torch.cuda.device_count(), "GPU")
            self.model.to(self.device)

        if opts.mode == 'train':
            if opts.optim == 'Adam':
                self.optim = torch.optim.Adam(self.model.parameters(), lr=opts.initial_lr)
            else:
                self.optim = torch.optim.SGD(self.model.parameters(), lr=opts.initial_lr, momentum=0.9)
        print(self.optim)

        if(opts.resume_train):
            parallel_model = True if torch.cuda.device_count() > 1 else False
            if os.path.isfile(os.path.join(self.out,"model_best.pth.tar")):
                self.model, self.epoch,self.optim, self.loss_func = utils.load_checkpoint(self.model, self.optim, os.path.join(self.out,"model_best.pth.tar"), parallel_model= parallel_model)
                ckpt = torch.load(os.path.join(self.out,"model_best.pth.tar"))
                self.iteration = ckpt["iteration"]
                self.epoch += 1
            for param_group in self.optim.param_groups:
                param_group['lr'] = opts.initial_lr
            
        self.loss_radial = torch.nn.L1Loss(reduction='sum')
        self.loss_sem = torch.nn.L1Loss()
        self.iter_val = 0
        self.max_iter = opts.cfg['max_iteration']
        self.best_acc_mean = math.inf
        #visualizer
        self.vis = vis



        
        if not osp.exists(self.out):
            os.makedirs(self.out)


    def compute_r_loss(self,pred,gt):
        loss = self.loss_radial(pred[torch.where(gt!=0)],
                gt[torch.where(gt!=0)]) / float(len(torch.nonzero(gt)))
        return loss


    def validate(self):
        self.model.eval()

        val_loss = 0
        with torch.no_grad():
            for batch_idx, (data, target, sem_target) in tqdm.tqdm(
                    enumerate(self.val_loader),
                    total=len(self.val_loader),
                    desc='Valid iteration=%d' % self.iter_val,
                    ncols=80,
                    leave=False):
                    
                data, target, sem_target= data.to(self.device), target.to(self.device), sem_target.to(self.device)
                score, score_rad = self.model(data)

                if (data.size()[2] != score.size()[2]):
                    score = score[:, :, :data.size()[2], :]
                    score_rad = score_rad[:, :, :data.size()[2], :]

                
                loss_s = self.loss_sem(score, sem_target)
                loss_r = self.compute_r_loss(score_rad,target)
                loss = loss_r+loss_s
                
                if np.isnan(float(loss.item())):
                    raise ValueError('loss is nan while validating')
                val_loss += float(loss.item())


                if self.vis is not None:
                    self.vis.add_scalar('Val_r_s', 
                                        float(loss.detach().cpu().numpy()), 
                                        self.iter_val)
                    self.vis.add_scalar('Val_MAE', 
                                        float(torch.sum(torch.abs(score_rad-target)) / float(len(torch.nonzero(target)))), 
                                        self.iter_val)
                    self.vis.add_scalar('Val_r',float(loss_r.detach().cpu().numpy()),self.iter_val)
                    self.vis.add_scalar('Val_s',float(loss_s.detach().cpu().numpy()),self.iter_val)
                    self.vis.add_scalar('Val_ACC', 
                                        float(torch.sum(torch.where(torch.abs(score_rad-target)[torch.where(target!=0)]<=0.05,1,0)) / float(len(torch.nonzero(target))))
                                        , self.iter_val)
                    if self.iter_val%10==0:#%50==0:
                        self.vis.add_image('Val_sem',torch.where(score[0].cpu()>=.5,1,0),self.iter_val)
                self.iter_val = self.iter_val + 1
        val_loss /= len(self.val_loader)
        mean_acc = val_loss
        #self.scheduler.step(mean_acc)

        is_best = mean_acc < self.best_acc_mean
        if is_best:
            self.best_acc_mean = mean_acc
        save_name = "ckpt.pth.tar"
        torch.save(
            {
                'epoch': self.epoch,
                'iteration': self.iteration,
                'arch': self.model.__class__.__name__,
                'optim_state_dict': self.optim.state_dict(),
                'model_state_dict': self.model.state_dict(),
                'best_acc_mean': self.best_acc_mean,
                'loss': loss,
            }, osp.join(self.out, save_name))
        if is_best:
            shutil.copy(osp.join(self.out, save_name),
                        osp.join(self.out, 'model_best.pth.tar'))

    def train_epoch(self):
        self.model.train()
        for batch_idx, (data, target, sem_target) in tqdm.tqdm(
                enumerate(self.train_loader),
                total=len(self.train_loader),
                desc='Train epoch=%d' % self.epoch,
                ncols=80,
                leave=True):

            #iteration = batch_idx + self.epoch * len(self.train_loader)
            #if self.iteration != 0 and (iteration - 1) != self.iteration:
            #    continue  
            self.iteration = batch_idx + self.epoch * len(self.train_loader)

            data, target, sem_target= data.to(self.device), target.to(self.device), sem_target.to(self.device)

            target_test = target.detach().cpu().numpy()
            sem_target_test = sem_target.detach().cpu().numpy()

            self.optim.zero_grad()
            score,score_rad = self.model(data)

            if (data.size()[2] != score.size()[2]):
                score = score[:, :, :data.size()[2], :]
                score_rad = score_rad[:, :, :data.size()[2], :]

            score_rad = score_rad.permute(1,0,2,3) * sem_target.permute(1,0,2,3)
            score_rad = score_rad.permute(1,0,2,3)
            
            loss_s = self.loss_sem(score, sem_target)
            loss_r = self.compute_r_loss(score_rad,target)

            loss = loss_r+loss_s
            loss.backward()
            self.optim.step()

            np_loss, np_loss_r, np_loss_s = loss.detach().cpu().numpy(), loss_r.detach().cpu().numpy(), loss_s.detach().cpu().numpy()

            if np.isnan(np_loss):
                raise ValueError('loss is nan while training')

            #visulalization
            if self.vis is not None:
                self.vis.add_scalar('Train_r_s', np_loss, self.iteration)
                self.vis.add_scalar('Train_r', np_loss_r, self.iteration)
                self.vis.add_scalar('Train_s', np_loss_s, self.iteration)
                self.vis.add_scalar('Train_ACC', 
                                    float(torch.sum(torch.where(torch.abs(score_rad-target)[torch.where(target!=0)]<=0.05,1,0)) / float(len(torch.nonzero(target)))), 
                                    self.iteration)

            if self.iteration >= self.max_iter:
                break

    def Train(self):
        max_epoch = int(self.opts.epochs)#int(math.ceil(1. * self.max_iter / len(self.train_loader)))
        #self.scheduler  = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optim, verbose=True)
        for epoch in tqdm.trange(self.epoch, max_epoch, desc='Train',
                                 ncols=80):
            self.epoch = epoch
            self.train_epoch()
            if(self.epoch % 15 == 0):
                self.validate()
            if self.epoch % 70 == 0 and self.epoch != 0:
                for g in self.optim.param_groups:
                    g['lr'] /= 10
            if self.iteration >= self.max_iter:
                break

    def Test(self):
        if self.opts.test_occ:
            estimate_6d_pose_lmo(self.opts)
        else:
            test_ckpt()
            estimate_6d_pose_lm(self.opts)
