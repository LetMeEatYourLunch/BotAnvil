# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 12:49:35 2022

@author: user
"""
import os
os.chdir("C:\\Users\\user\\Documents\\Python Scripts\\Projects\\TraderTool\\")
import pandas as pd
import yaml
import requests
import pipe_line as pl
import numpy as np


test = pl.pipe_line("pipeline.yml")

q = test.pull_dt("VDHG")
# https://stackoverflow.com/questions/13703720/converting-between-datetime-timestamp-and-datetime64
# Convert to datetime object
t = pd.to_datetime(q["close_date"])
# Convert to numpy 
t_np = t.to_numpy()

# Metrics
# https://www.investopedia.com/terms/t/technicalindicator.asp
# SMA
q.close_price.rolling(4).mean()
#RSI with 14 days
test.get_rsi(q)
   


                          