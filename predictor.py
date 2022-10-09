"""
Writing a script to predict future prices for an article based on the existing data.

Author: Pranav Sekhar
Date: 8 Oct, 2022
"""

import pandas as pd

working_df = pd.read_csv('modules/maintenance.csv')
print(working_df.info)
print(working_df.shape)