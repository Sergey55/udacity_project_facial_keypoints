## TODO: define the convolutional neural network architecture

import torch
import torch.optim as optim

from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
# can use the below import should you choose to initialize the weights of your Net
import torch.nn.init as I

import pytorch_lightning as pl


class Net(pl.LightningModule):
    """Neural ntwork for detecting facial keypoints"""

    def __init__(self):
        """Constructor"""
        super(Net, self).__init__()
        
        self.conv1 = nn.Conv2d(1, 32, 5)
        self.conv2 = nn.Conv2d(32, 64, 4)
        self.conv3 = nn.Conv2d(64, 128, 3)
        self.conv4 = nn.Conv2d(128, 256, 3)
        self.conv5 = nn.Conv2d(256, 512, 3)

        self.maxPooling = nn.MaxPool2d(2, 2)

        self.fc1 = nn.Linear(4 * 4 * 512, 2048)
        self.fc2 = nn.Linear(2048, 1024)
        self.fc3 = nn.Linear(1024, 136)

        self.dropout1 = nn.Dropout(0.1)
        self.dropout2 = nn.Dropout(0.25)

        self.criterion = nn.MSELoss()
        
    def forward(self, x):

        x = self.maxPooling(F.relu(self.conv1(x)))
        x = self.dropout1(x)
        x = self.maxPooling(F.relu(self.conv2(x)))
        x = self.dropout1(x)
        x = self.maxPooling(F.relu(self.conv3(x)))
        x = self.dropout1(x)
        x = self.maxPooling(F.relu(self.conv4(x)))
        x = self.dropout1(x)
        x = self.maxPooling(F.relu(self.conv5(x)))
        x = self.dropout1(x)

        x = x.view(x.size(0), -1)

        x = self.dropout2(F.elu(self.fc1(x)))
        x = self.dropout2(F.elu(self.fc2(x)))
        x = self.fc3(x)

        return x

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=0.001)

        scheduler = ReduceLROnPlateau(
            optimizer, 
            mode='min', 
            patience=10, 
            factor=0.5, 
            verbose=True)

        return {
           'optimizer': optimizer,
           'lr_scheduler': scheduler,
           'monitor': 'train_loss'
        }

    def training_step(self, batch, batch_idx):
        images, key_points = batch
        key_points = key_points.view(key_points.size(0), -1)
        images, key_points = images.float() , key_points.float()

        y_hat = self(images)

        loss = self.criterion(y_hat, key_points)

        self.log('train_loss', loss, on_step=True, on_epoch=True)

        return {'loss': loss}
