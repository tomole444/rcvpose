#python Version 3.9.7

# Evaltuation LM
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/detection/rcvpose/datasets/LINEMOD" --mode=test --demo_mode=True --using_ckpts=True

#Train LM
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/detection/rcvpose/datasets/LINEMOD" --kpt_num='1' --mode=train --batch_size=1 --optim='Adam' --initial_lr=1e-4 --resume=False --demo_mode=True

#Train Custom
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/datasets/ownBuchRCV" --kpt_num='1' --mode=train --batch_size=1 --optim='Adam' --initial_lr=1e-4 --resume=False
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/datasets/apeRCV" --kpt_num='1' --mode=train --batch_size=1 --optim='Adam' --initial_lr=1e-4 --resume=False 

python main.py --root_dataset="/media/irobot/grass/Leyh/datasets/ownBuchRCVBig" --out="/media/irobot/grass/Leyh/outputs/rcvpose/ownBuchRCVBig" --kpt_num='1' --mode=train --batch_size=12 --epochs=200 --optim='Adam' --initial_lr=1e-4 --resume=False

tensorboard --logdir "/media/irobot/grass/Leyh/outputs/rcvpose/ownBuchRCVBig/kpt_2/tbLog"
#Save model as ply in mm (* 1000) with binary encoding