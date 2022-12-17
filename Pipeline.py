# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 10:41:42 2022

@author: user
"""

class pipe_line:
    
    
    def __init__(self, yaml_file_path):
        """
        

        Args:
            conn_yaml (TYPE): DESCRIPTION.

        Returns:
            None.
            "pipeline.yml"
        """
        import pandas as pd
        import yaml
        import requests
        
        try:
            print(os.getcwd())
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
        
        