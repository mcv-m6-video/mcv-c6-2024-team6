import sys
import os
import json
os.environ["KERAS_BACKEND"] = "torch"  # Or "jax" or "torch"!
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from utils import *

import numpy as np
import tqdm
import glob
import pickle
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
from pathlib import Path

import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from pycocotools import mask
from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.data import build_detection_test_loader
from detectron2.structures import BoxMode
from detectron2.engine import DefaultTrainer

from pycocotools.mask import toBbox

import torch

from pathlib import Path
import random 


if __name__ == "__main__":


    CLASS_NAMES = {
        0: 'person',
        1: 'bicycle',
        2: 'car',
    }

    NAME_TO_CLASS = {
        'person': 0,
        'bicycle': 1,
        'car': 2
    }

    N_FRAMES = 2141
    FRAME_SET_PATH = "/ghome/group07/test/W2/frame_dataset"
    COLOR_FRAME_SET_PATH = os.path.join(FRAME_SET_PATH, "color")
    GRAY_FRAME_SET_PATH = os.path.join(FRAME_SET_PATH, "gray")


    cfg = get_cfg()
    # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library

    # MASK RCNN
    #model = "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"

    with open('./configs/configs_task2_1.json') as config:
        task_configs = json.load(config)
    detection_threshold = task_configs["detection_threshold"]
    min_iou = task_configs["min_iou"]
    max_frames_skip = task_configs["max_frames_skip"]
    

    # FASTER RCNN
    model = "COCO-Detection/faster_rcnn_R_50_C4_1x.yaml"

    cfg.merge_from_file(model_zoo.get_config_file(model))
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(model)
    # SET THRESHOLD FOR SCORING
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = detection_threshold  # set threshold for this model

    predictor = DefaultPredictor(cfg)

    # EXAMPLE
    #----------------------------------------------------------------------
    #try_img_path = "/ghome/group07/test/W2/frame_dataset/color/0.png"
    #try_img = cv2.imread(try_img_path)
    #output = predictor(try_img)

    #print("Ouput of pred_classes:\n", output["instances"].pred_classes)
    #print("\n\n\nOutput of instances: \n", output["instances"].pred_boxes)
    #print("\n\n\nWhole output:\n", output)

    #save_img(try_img, output, "predicted_img_example.png", cfg)
    #----------------------------------------------------------------------


    with tqdm.tqdm(total=N_FRAMES) as pbar:
        for i in range(N_FRAMES):

            img_path = os.path.join(COLOR_FRAME_SET_PATH, str(i)+".png")
            img = cv2.imread(img_path)
            preds = predictor(img)

            # Keep only car predictions
            keep_cars_mask = preds["instances"].pred_classes == NAME_TO_CLASS["car"]
            bboxes, scores = preds["instances"].pred_boxes[keep_cars_mask], preds["instances"].scores[keep_cars_mask]

            # MAYBE WE SHOULD REMOVE SOME BB USING A THRESHOLD,
            # BUT I THINK THAT THIS IS DONE IN LINE 82 ALREADY USING THAT THRESHOLD
            # OTHERWISE WE SHOULD JUST APPLY A THRESHOLD

            










    

