#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import cv2
import glob
import time

import torch
import torchvision
import albumentations as A
from torchvision import transforms # 이미지 데이터 augmentation
from torch.utils.data import Dataset, DataLoader
from albumentations.pytorch.transforms import ToTensorV2 # albumentations 텐서화 함수



class CustomDataset(Dataset):
    def __init__(self, root_path, mode):
        self.root_path = root_path
        self.mode = mode
        self.all_data = sorted(glob.glob(os.path.join(root_path, mode, '*', '*'))) # 전체 경로
        self.class_names = os.listdir(f'./{self.mode}') # 이미지가 있는 디렉토리 리스트

        
    def __getitem__(self, index):
        # 인덱스가 tensor형태일 수 있는 것을 방지
        if torch.is_tensor(index):
            index = index.tolist()

        data_path = self.all_data[index] # 인덱스가 부여된 데이터 1개
        image = cv2.imread(data_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # cv2 라이브러리의 BGR 형식을 RGB로 permute

        # Transform 정의
        train_transforms = A.Compose([A.Resize(224,224),
                                      A.Transpose(p=0.5),
                                      A.HorizontalFlip(p=0.5), #좌우반전
                                      A.VerticalFlip(p=0.5), #상하반전
                                      A.ShiftScaleRotate(p=0.5),
                                      A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=20, val_shift_limit=20, p=0.5), #색도, 채도, 명도 변경
                                      A.RandomBrightnessContrast(brightness_limit=(-0.1,0.1), contrast_limit=(-0.1, 0.1), p=0.5), #밝기 및 대비를 랜덤 지정
                                      A.ChannelShuffle(), #RGB채널을 랜덤하게 섞음.
                                      A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225), max_pixel_value=255.0, always_apply=False, p=1.0), # 이미지넷 데이터셋 통계값으로 Normalize
                                      A.CoarseDropout(p=0.5), # 약간씩 없애기
                                      ToTensorV2()
                                      ])

        valid_transforms = A.Compose([A.Resize(224,224),
                                      A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225), max_pixel_value=255.0, always_apply=False, p=1.0), # 텐서타입은 안해줌
                                      ToTensorV2() # Normalize를 먼저하고 tensor화를 진행해야한다.
                                     ])

        # Transform 적용
        if self.mode == 'train':
            image = train_transforms(image = image)['image']
        else:
            image = valid_transforms(image = image)['image']

        # 이미지의 이름을 이용하여, 클래스 별로 label 부여
        class_name = os.path.basename(data_path).split('_')[0]
        label = self.class_names.index(class_name)
    
        return image, label
    
    
    def __len__(self):
        return len(self.all_data)

