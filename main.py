import torch
from utils import get_config, get_log_dir, str2bool
from data_loader import get_loader
from train import Trainer
import warnings
import os
from tensorboardX import SummaryWriter
warnings.filterwarnings('ignore')

#from visualizer import Visualizer

resume = ''

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    # Parameters to set
    parser.add_argument('--mode',
                        type=str,
                        default='train',
                        choices=['train', 'test'])
    parser.add_argument("--gpu_id", type=int, default=-1)
    parser.add_argument('--dname',
                        type=str,
                        default='lm',
                        choices=['lm', 'ycb'])
    parser.add_argument("--root_dataset",
                        type=str,
                        default='./datasets/LINEMOD')
    parser.add_argument("--resume_train", type=str2bool, default=False)
    parser.add_argument("--optim",
                        type=str,
                        default='Adam',
                        choices=['Adam', 'SGD'])
    parser.add_argument("--batch_size",
                        type=str,
                        default='4')
    parser.add_argument("--epochs",
                        type=str,
                        default='100')
    parser.add_argument("--class_name",
                        type=str,
                        default='ape')
    parser.add_argument("--initial_lr",
                        type=float,
                        default=1e-4)
    parser.add_argument("--kpt_num",
                        type=str,
                        default='1')                        
    parser.add_argument('--model_dir',
                    type=str,
                    default='ckpts/')  
    parser.add_argument('--out',
                    type=str,
                    default='logs/')   
    parser.add_argument('--demo_mode',
                    type=str2bool,
                    default=False) 
    parser.add_argument('--test_occ',
                    type=bool,
                    default=False)
    parser.add_argument('--using_ckpts',
                    type=str2bool,
                    default=False) 
    opts = parser.parse_args()

    cfg = get_config()[1]
    opts.cfg = cfg

    if opts.mode in ['train']:
        #opts.out = get_log_dir(opts.dname+'/'+opts.class_name+'Kp'+opts.kpt_num, cfg)
        out_path = os.path.join(opts.out, "kpt_" + opts.kpt_num)
        os.makedirs(out_path,exist_ok=True)
        print('Output logs: ', out_path)
        vis = SummaryWriter(logdir=os.path.join(out_path,'tbLog'))
    else:
        vis = []

    data = get_loader(opts)
    
    trainer = Trainer(data, opts, vis)
    if opts.mode == 'test':
        trainer.Test()
    else:
        trainer.Train()
