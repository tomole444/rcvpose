import os
import numpy as np
import cv2


class Converter:
    def __init__(self, pathPvNet, pathRcv):
        self.pathPvNet = pathPvNet
        self.pathRcv = pathRcv
    def transferData (self):

        diameter = None
        fps = None
        with open(os.path.join(self.pathPvNet, "diameter.txt")) as f:
            diameter = float(f.readline())
        fps = np.loadtxt(os.path.join(self.pathPvNet, "fps.txt"))

        #diameter *= 1000
        #fps *= 1000

        # with open(os.path.join(pathRcv, "diameter.txt"), "w") as f:
        #     f.write(str(diameter))
        #np.savetxt(os.path.join(pathRcv, "fps.txt"), fps)
        fps2 = np.append(fps, fps[0]).reshape(-1,3)
        np.save(os.path.join(self.pathRcv,"Outside9.npy"), fps2)
        #print(fps)

    def createSplit(self, train_percentage):
        os.makedirs(os.path.join(self.pathRcv, "Split"), exist_ok= True)

        img_ids = os.listdir(os.path.join(self.pathRcv, "JPEGImages"))
        img_ids = np.array(img_ids)
        np.random.shuffle(img_ids)
        count = len(img_ids)
        train_ids = img_ids[:int(count * train_percentage)]
        val_ids = img_ids[int(count * train_percentage):]

        train_ids = [train_id.split(".")[0] + "\n" for train_id in train_ids]
        val_ids = [val_id.split(".")[0] + "\n" for val_id in val_ids]

        with open(os.path.join(self.pathRcv, "Split", "train.txt"), "w") as f:
            f.writelines(train_ids)
        with open(os.path.join(self.pathRcv, "Split", "val.txt"), "w") as f:
            f.writelines(val_ids)





if __name__ == "__main__":
    con = Converter("/home/thws_robotik/Documents/Leyh/6dpose/datasets/ownBuchBig",
        "/home/thws_robotik/Documents/Leyh/6dpose/datasets/ownBuchRCV")
    con.createSplit(0.8)
