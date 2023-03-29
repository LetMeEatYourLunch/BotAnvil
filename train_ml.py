# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 11:56:33 2023

@author: user
"""

# IDE imports; remove prior to deployment
import pipe_line as pline
import numpy as np
import pandas as pd
import os
import torch
import torch.nn as nn
import torch.nn.functional as f
from torch.optim import Adam as adam
import pytorch_lightning as l
from torch.utils.data import TensorDataset as tensordataset
from torch.utils.data import DataLoader as dataloader

class lstm(l.LightningModule):
    def __init__(self, num_features = 1):
        super().__init__()
        #hidden_size refers to output size length e.g. if output 3 then hidden size 2 would yield [3,3]
        self.lstm = nn.LSTM(input_size = num_features, hidden_size = 1)
    def forward(self, input):
        # column of length input
        input_trans = input.view(len(input), 1)
        # unrolls LSTM for length of input
        lstm_out, temp = self.lstm(input_trans)
        # The prediction is the output of the last LSTM output
        pred = lstm_out[-1]
        return pred
    def configure_optimizers(self):
        #lr is learning rate; default value is 0.001
        return adam(self.parameters(), lr = 0.1)
    def training_step(self, batch, batch_idx):
        input_i, label_i = batch
        output_i = self.forward(input_i[0])
        loss = (output_i - label_i)**2
        
        self.log("train_loss", loss)
        if (label_i == 0):
            self.log("out_0", output_i)
        elif(label_i == 1):
            self.log("out_1", output_i)
        else:
            return False
        return loss
    
class machine_learn_predict:
    def __init__(self):
        req_modules = {"pipe_line" : "pline"
                       , "numpy" : "np"
                       , "pandas" : "pd"
                       , "os" : ""
                       , "torch" : ""
                       , "torch.nn" : "nn"
                       , "torch.nn.functional" : "nn_func"
                       , "pytorch_lightning" : "lightning"}
                       
        for k in req_modules.keys():
            try:
                exec("import {module} as {reference}".format(module = k, reference = req_modules[k]))
            except Exception as e:
                print(e)
            
        from torch.optim import Adam as adam
        from torch.utils.data import TensorDataset as tensordataset
        from torch.utils.data import DataLoader as dataloader
        return True
        

    
    def get_train_dat(self):
        pass
        
    def generate_ml(self):
        self.model = model = lstm()
    
    def train_ml(self                 
                 , train_set
                 , max_epochs
                 , best_checkpoint_path = False
                 ):
        assert(isinstance(train_set, torch.utils.data.dataset.TensorDataset))
        assert(isinstance(max_epochs, int))
        
        data_loader = dataloader(train_set)
        # Smokem if you've gottem
        if torch.cuda.is_available():
            trainer = l.Trainer(max_epochs = max_epochs
                                , accelerator="gpu"
                                , devices=1)
        # Or just use your boring CPU
        else:
            trainer = l.Trainer(max_epochs = max_epochs)
        # Reload from previous save-point
        if best_checkpoint_path != False:
            assert(best_checkpoint_path, str)
            trainer.fit(self.model
                        , train_dataloaders = data_loader
                        , ckpt_path         = best_checkpoint_path)
        else:
            trainer.fit(self.model
                        , train_dataloaders = data_loader)
        
        return True
    
    def score(self, timeseries):
        assert(isinstance(timeseries, torch.tensor))
        score = self.model(timeseries).detach()
        if isinstance(score, float):
            return self.model(timeseries).detach()
        else:
            return False
    
    def get_ml_test_results(self):
        pass
        