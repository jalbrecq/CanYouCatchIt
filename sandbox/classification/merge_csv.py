import os, glob
import pandas as pd

path = "../data/csv/"

all_files = glob.glob(os.path.join(path, "*.csv"))

all_df = []
for f in all_files:
    df = pd.read_csv(f, sep=',')
    all_df.append(df)
    
merged_df = pd.concat(all_df, ignore_index=True, sort=False)

merged_df=merged_df.drop(merged_df[merged_df.delay.isna()].index)

merged_df.loc[merged_df.delay >=10.0,"delay"]= 10

merged_df.loc[(merged_df.delay >0) & (merged_df.delay <10.0),"delay"]= 1

merged_df.loc[merged_df.delay ==0,"delay"]= 0

merged_df.loc[(merged_df.delay >-10) & (merged_df.delay <0),"delay"]= -1

merged_df.loc[merged_df.delay <=-10,"delay"]= -10

merged_df.to_csv('../data/csv/merged.csv',index=False)