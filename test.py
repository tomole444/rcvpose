import numpy as np
import tempfile

with open("/home/thws_robotik/Documents/Leyh/6dpose/datasets/ownBuchRCV/depth/depth0.dpt") as f:
            h,w = np.fromfile(f,dtype=np.uint32,count=2)
            data = np.fromfile(f,dtype=np.uint16,count=w*h)
            depth = data.reshape((h,w))

pose = np.load("/home/thws_robotik/Documents/Leyh/6dpose/detection/rcvpose/datasets/LINEMOD/ape/Outside9.npy")
print(pose)