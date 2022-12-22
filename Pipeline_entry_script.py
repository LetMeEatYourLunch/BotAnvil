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
#def get_ema(x, window):
#    ema = np.zeros(len(x))
#    ema[window + 1] = np.mean(x[0:window])
#    mult = np.divide(2.0, window + 1.0)
#    for i in range(window + 2, len(x)):
#        ema[i] =  np.multiply(x[i], mult) + np.multiply(ema[i-1], 1 - mult) 
#    return ema

w = test.get_ema(q, 20, 2)
ww = test.get_macd(q)


                          