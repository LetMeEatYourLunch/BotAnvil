# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 13:18:25 2022

@author: user
"""
import os
os.chdir("C:\\Users\\user\\Documents\\Python Scripts\\Projects\\TraderTool\\")
import pandas as pd
import yaml
import requests
import pipe_line as pl
import numpy as np
import collections.abc

def analyse_tickers(tickers):
    # Assertions
    #assert(isinstance(tickers, collections.abc.Sequence))

    # Create pipeline object
    pipe = pl.pipe_line("pipeline.yml")
    # Define empty data frame
    df_all = pd.DataFrame(columns=["code"
                                   , "close_date"
                                   , "close_price"
                                   , "change_price"
                                   , "volume"
                                   , "day_high_price"
                                   , "day_low_price"
                                   , "change_in_percent"
                                   , "delta"
                                   , "loss"
                                   , "gain"
                                   , "loss_mean"
                                   , "gain_mean"
                                   , "RSI"
                                   , "ema"
                                   , "ema_12"
                                   , "ema_26"
                                   , "macd"])
    for ticker in tickers:
        df_ticker = pipe.pull_dt(ticker)
        df_ticker = pipe.get_rsi(df_ticker)
        df_ticker = pipe.get_macd(df_ticker)
        df_all = pd.concat([df_all, df_ticker])
        
    df_all = pipe.asx_to_unix_datetime(df_all)
    
    return df_all
    
        
    