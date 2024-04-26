#python Version 3.9.7

# Evaltuation LM
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/detection/rcvpose/datasets/LINEMOD" --mode=test --demo_mode=True --using_ckpts=True
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/datasets/ownBuchRCV" --mode=test --demo_mode=True --using_ckpts=True

#Train LM
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/detection/rcvpose/datasets/LINEMOD" --kpt_num='1' --mode=train --batch_size=1 --optim='Adam' --initial_lr=1e-4 --resume=False --demo_mode=True

#Train Custom
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/datasets/ownBuchRCV" --kpt_num='1' --mode=train --batch_size=1 --optim='Adam' --initial_lr=1e-4 --resume=False
python main.py --root_dataset="/home/thws_robotik/Documents/Leyh/6dpose/datasets/apeRCV" --kpt_num='1' --mode=train --batch_size=1 --optim='Adam' --initial_lr=1e-4 --resume=False 

python main.py --root_dataset="/media/irobot/grass/Leyh/datasets/ownBuchRCVBig" --out="/media/irobot/grass/Leyh/outputs/rcvpose/ownBuchRCVBig" --kpt_num='1' --mode=train --batch_size=12 --epochs=200 --optim='Adam' --initial_lr=1e-4 --resume=False
python main.py --root_dataset="/media/irobot/grass/Leyh/datasets/ownBuch480" --out="/media/irobot/grass/Leyh/outputs/rcvpose/ownBuch480" --kpt_num='2' --mode=train --batch_size=40 --epochs=50 --optim='Adam' --initial_lr=1e-4 --resume_train=True
python main.py --root_dataset="/home/tomle/Documents/datasets/ownBuch480" --out="/home/tomle/Documents/outputs/rcvpose/ownBuch480" --kpt_num='2' --mode=train --batch_size=15 --epochs=50 --optim='Adam' --initial_lr=1e-4 --resume_train=True

python main.py --root_dataset="/media/irobot/grass/Leyh/datasets/ownBuchRCVBig" --out="/media/irobot/grass/Leyh/outputs/rcvpose/ownBuchRCVBig" --kpt_num='2' --mode=train --batch_size=12 --epochs=25 --optim='Adam' --initial_lr=1e-4 --resume=False; python main.py --root_dataset="/media/irobot/grass/Leyh/datasets/ownBuchRCVBig" --out="/media/irobot/grass/Leyh/outputs/rcvpose/ownBuchRCVBig" --kpt_num='3' --mode=train --batch_size=12 --epochs=25 --optim='Adam' --initial_lr=1e-4 --resume=False

tensorboard --logdir "/media/irobot/grass/Leyh/outputs/rcvpose/ownBuchRCVBig/kpt_2/tbLog"
tensorboard --bind_all --port 6006 --logdir "/media/irobot/grass/Leyh/outputs/rcvpose/ownBuch480/kpt_1/tbLog"
tensorboard --bind_all --port 6007 --logdir "/media/irobot/grass/Leyh/outputs/rcvpose/ownBuch480/kpt_3/tbLog"
tensorboard --bind_all --port 6008 --logdir "/home/tomle/Documents/outputs/rcvpose/ownBuch480/kpt_2/tbLog/"
#Save model as ply in mm (* 1000) with binary encoding