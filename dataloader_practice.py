import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as f
from torch.nn import init
import torch.optim as optim
from torch.utils import data
import torchvision.models as models
import numpy as np
import cv2
import os
from datetime import datetime
import matplotlib.pyplot as plt

def getData(mode):
    if mode == 'train':
        img = pd.read_csv('train_img.csv')
        label = pd.read_csv('train_label.csv')
        return np.squeeze(img.values), np.squeeze(label.values)
    else:
        img = pd.read_csv('test_img.csv')
        label = pd.read_csv('test_label.csv')
        return np.squeeze(img.values), np.squeeze(label.values)

class RetinopathyLoader(data.Dataset):
    def __init__(self, mode):
        """
        Args:
            mode : Indicate procedure status(train or test)
            
            self.root (str): Root path of the dataset.
            self.img_name (str list): String list that store all image names.
            self.label (int or float list): Numerical list that store all ground truth label values.
        """

    def __len__(self):
        """'return the size of dataset"""
        return ...

    def __getitem__(self, index):
        """
           step1. load the image file
                  hint : path = root + self.img_name[index] + '.jpeg'
           
           step2. Get the ground truth label from self.label
                     
           step3. (optional)
                  Transform the .jpeg rgb images during the training phase,
                  such as resizing, random flipping, rotation, cropping, normalization etc. 
                       
                  In the testing phase, if you have a normalization process during the training phase,
                  you only need to normalize the data. 
                  
                  hints: Convert the pixel value to [0, 1]
                         Transpose the image shape from [H, W, C] to [C, H, W]
                         
            step4. Return processed image and label
        """
        return ...

if __name__ == '__main__':

    BATCH_SIZE = 4
    LR = 0.001
    EPOCH = 1
    WEIGHT_DECAY = 5e-4

    train_loader = RetinopathyLoader(mode='train')
    train_data = data.DataLoader(train_loader, batch_size=BATCH_SIZE, num_workers=2)

    test_loader = RetinopathyLoader(mode='test')
    test_data = data.DataLoader(test_loader, batch_size=BATCH_SIZE, num_workers=2)
    
    # resnet18
    net = models.resnet18(pretrained=False, progress=False)
    net.fc = nn.Sequential(
                    nn.Dropout(0.5),
                    nn.Linear(512, 5)
                )
    net = net.cuda()
    optimizer = optim.SGD(net.parameters(), lr=LR, momentum=0.9, weight_decay=WEIGHT_DECAY)
    criterion = nn.CrossEntropyLoss()

    # train
    for epoch in range(1, EPOCH+1):
        net.train()
        epoch_start = datetime.now()
        epoch_loss = 0.0

        # in each iteration
        for imgs, labels in train_data:
            # prepare data
            imgs = imgs.float().cuda()
            labels = labels.cuda()
            # forward
            outputs = net(imgs)
            # loss
            loss = criterion(outputs, labels)
            # backward + optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        # in each epoch
        # compute acc
        with torch.no_grad():
            net.eval()
            # for test data acc
            test_acc = 0.0
            for imgs, labels in test_data:
                # prepare data
                imgs = imgs.float().cuda()
                labels = labels.cuda()
                # forward
                outputs = net(imgs)
                # acc
                for i in range(len(outputs)):
                    if outputs[i][labels[i]] == max(outputs[i]):
                        test_acc += 1
            test_acc /= 7025

            # for train data acc
            train_acc = 0.0
            for imgs, labels in train_data:
                # prepare data
                imgs = imgs.float().cuda()
                labels = labels.cuda()
                # forward
                outputs = net(imgs)
                # acc
                for i in range(len(outputs)):
                    if outputs[i][labels[i]] == max(outputs[i]):
                        train_acc += 1
            train_acc /= 28099

        # print info
        epoch_end = datetime.now()
        print ('Epoch '+str(epoch)+' ---------------- '+str((epoch_end-epoch_start).seconds)+' sec')
        print ('\ttraining loss: '+str(epoch_loss)+', train acc: '+str(train_acc)+', test acc: '+str(test_acc))



