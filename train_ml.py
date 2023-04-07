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
        # Remove cuda:0 flag
        output_i = output_i.item()
        #loss = torch.tensor(np.array((output_i - label_i)**2))
        loss = (output_i - label_i)**2
        loss = torch.tensor(loss, requires_grad = True)
        self.log("train_loss", loss)
        # Need to update the loss logging; need an automated way to manager labels
        if (label_i == 0):
            self.log("out_0", output_i)
        elif(label_i == 1):
            self.log("out_1", output_i)

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
            len_itm = len(req_modules[k])
            if len_itm == 0:
                import_string = "import {module}".format(module = k)
            elif len_itm > 0:
                import_string = "import {module} as {reference}".format(module = k
                                                                        , reference = req_modules[k])
            else:
                raise Exception("Bad import string")
            
            try:
                exec(import_string)
            except Exception as e:
                print(str(e) + "\n" + import_string)
            
        try:
            from torch.optim import Adam as adam
            from torch.utils.data import TensorDataset as tensordataset
            from torch.utils.data import DataLoader as dataloader
        except Exception as e:
            print(str(e) + "; module/class not available")

        self.model = None
        self.num_cpus = os.cpu_count()            
        return None
        
    def scale_inputs(self, input_data, feature_cols, label_cols):
        assert(isinstance(input_data, pandas.core.frame.DataFrame))
        # Assert no intersection between features and labels
        assert(set(feature_cols).intersection(label_cols) == set())
        scaled_input = input_data.copy()
        scale_meta_dat = {}
        for col in feature_cols + label_cols:
            col_mean = np.mean(input_data[str(col)])
            col_std  = np.std(input_data[str(col)])
            scaled_input[str(col)] -= col_mean
            scaled_input[str(col)] /= col_std
            scale_meta_dat[col] = [col_mean, col_std]
        return(scaled_input, scale_meta_dat)
            
    def unscale_col(self, scaled_col, col_mean, col_std):
        descaled_col   = scaled_col
        descaled_col *= col_std
        descaled_col += col_mean
        return(descaled_col)
          
    def get_learn_dat(self, training_dt, feature_col, ts_train_length = 6):
        
        feature_set = []
        label_set   = []
        
        ts = training_dt[feature_col]
        for w in ts.rolling(window = ts_train_length):
            if len(w) == ts_train_length:
                train_data = w.values
                feature_set.append(train_data[0:ts_train_length - 2])
                label_set.append(train_data[ts_train_length - 1])
        
        ml_features = torch.tensor(np.array(feature_set, dtype = np.float32))
        ml_labels   = torch.tensor(np.array(label_set, dtype = np.float32))
        learn_superset = tensordataset(ml_features, ml_labels)
        
        return(learn_superset)
    
    
    
    def apportion_train_set(self, learn_superset, train_split = 0.8):

        # Allocate training and test data sets
        # Length of training batches
        len_learn_superset = len(learn_superset)
        # Divide learning data into training and test components
        num_training_batch = int(train_split * len_learn_superset)
        num_test_batch     = len_learn_superset - num_training_batch
        assert(num_training_batch + num_test_batch == len_learn_superset)
        train_set, test_set = torch.utils.data.random_split(learn_superset
                                                            , [num_training_batch
                                                               , num_test_batch])
        return(train_set, test_set)
    
    def generate_ml(self):
        self.model = lstm()
    
    def train_ml(self                 
                 , train_set
                 , max_epochs
                 , best_checkpoint_path = False):
        assert(isinstance(train_set, torch.utils.data.dataset.TensorDataset) or
               isinstance(train_set, torch.utils.data.dataset.Subset))
        assert(isinstance(max_epochs, int))
        print(self.model)
        assert(not self.model is None)
        
        data_loader = dataloader(train_set, num_workers = self.num_cpus)
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
            assert(isinstance(best_checkpoint_path, str))
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
    
    def get_ml_test_results(self, train_set):
        
        data_loader = dataloader(train_set)
        
        trainer.test(dataloaders = test_dataloaders)
        trainer = l.Trainer(max_epochs = max_epochs)
        trainer.test(dataloaders = test_dataloaders)
        