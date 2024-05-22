from roboflow import Roboflow

rf = Roboflow(api_key="wcDKxxCya6kJIpda6sK2")

project = rf.workspace("fariha").project("alzheimer-detection")
version = project.version(5)
dataset = version.download("yolov8")

