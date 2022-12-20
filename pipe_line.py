# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 10:41:42 2022

@author: user
"""
import pandas as pd
import yaml
import requests
import numpy as np

class pipe_line:
    
    
    def __init__(self, yaml_file_path):
        """
        

        Args:
            conn_yaml (TYPE): DESCRIPTION.

        Returns:
            None.
            "pipeline.yml"
        """
        
        try:
            #print(os.getcwd())
            with open(yaml_file_path, "r") as file:
                self.conn_yaml = yaml.safe_load(file)
            self.asx_url = self.conn_yaml["connection"]["base_url"]
            self.asx_url_sfx = self.conn_yaml["connection"]["suffix"]
        except FileNotFoundError as err:
            print(err)
        except:
            print("Unknown failure")
            
        
        
        
        
    
    def build_driving_set(self):
        """
        

        Returns:
            None.

        """
        
    def asx_to_pandas_date(df):
        """
        

        Args:
            df (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        
        
    
    def pull_dt(self, asx_code):
        """
        This function was taken from:
            https://stackoverflow.com/questions/44979299/extracting-asx-data-using-pandas

        Args:
            data_ds (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        query_url_str = self.asx_url + asx_code + self.asx_url_sfx
        r = requests.get(query_url_str, timeout=10)
        asx_code_df = pd.DataFrame(r.json()["data"])
        return(asx_code_df)
        
    def write_dt(self, data_dt):
        """
        

        Args:
            data_dt (TYPE): DESCRIPTION.

        Returns:
            None.

        """
    def get_rsi(self, df, rsi_window = 14):
        """
        https://www.investopedia.com/terms/r/rsi.asp

        Args:
            df (TYPE): DESCRIPTION.
            window (TYPE, optional): DESCRIPTION. Defaults to 14.

        Returns:
            None.

        """
        def calc_delta_perc(x):
            return np.multiply(np.divide(x.iloc[-1] - x.iloc[0]
                                         , x.iloc[-1])
                               , 100.0)
        
        def calc_loss(delta_perc):
            # Rolling loss; if delta ngtve then loss, otherwise 0
            if (delta_perc.iloc[0] < 0):
                return np.abs(delta_perc.iloc[0])
            else:
                return np.float64(0)
            
        def calc_gain(delta_perc):
            # Rolling gain ; if delta pstve then gain, otherwise 0
            if (delta_perc.iloc[0] >= 0):
                return delta_perc.iloc[0]
            else:
                return np.float64(0)
        
        assert isinstance(df, pd.DataFrame)
        assert "close_price" in df.columns
        
        # Rolling difference for closing price (yesterday vs today)
        df["delta"] = df.close_price.rolling(window = 2).apply(calc_delta_perc)
        # Rolling loss; if delta ngtve then loss, otherwise 0
        df["loss"] = df.delta.rolling(window = 2).apply(calc_loss)
        # Rolling gain ; if delta pstve then gain, otherwise 0
        df["gain"] = df.delta.rolling(window = 2).apply(calc_gain)
        # Calculate the average loss/gain for RSI window (default 14)
        df["loss_mean"] = df.loss.rolling(window = rsi_window).mean()
        df["gain_mean"] = df.gain.rolling(window = rsi_window).mean()
        
        df["RSI"] = 100 - np.divide(100
                                    , 1 + np.divide((np.multiply(df.gain_mean, 13) + df.gain)
                                                    , (np.multiply(df.loss_mean, 13) + df.loss)))
        # Clean-up after calculation
        df.drop(["delta", "loss", "gain", "loss_mean", "gain_mean"], axis = 1)
        
        return df
        
        
        