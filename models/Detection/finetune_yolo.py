from ultralytics import YOLO
from roboflow import Roboflow
from PIL import Image
import matplotlib.pyplot as plt
import torch


#import dataset from roboflow
rf = Roboflow(api_key="YtW3yuBHl5lMVk2sxzLv")
project = rf.workspace("carplates-yrrpx").project("car-plates-l8eqg")
version = project.version(1)
dataset = version.download("yolov8")


yaml=dataset.location + '/data.yaml'

model = YOLO('yolov8s.pt')

model.train(data=yaml, epochs=20)
model.val()
