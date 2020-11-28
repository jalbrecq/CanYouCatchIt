import os, glob
import pandas as pd

path = "../data/csv/"

all_files = glob.glob(os.path.join(path, "*.csv"))

all_df = []
for f in all_files:
    df = pd.read_csv(f, sep=',')
    all_df.append(df)
    
merged_5_df = pd.concat(all_df, ignore_index=True, sort=False)

merged_5_df=merged_5_df.drop(merged_5_df[merged_5_df.delay.isna()].index)

merged_5_df.loc[merged_5_df.delay >10.0,"delay"]= 10
merged_5_df.loc[(merged_5_df.delay >0) & (merged_5_df.delay <=10.0),"delay"]= 1
merged_5_df.loc[merged_5_df.delay ==0,"delay"]= 0
merged_5_df.loc[(merged_5_df.delay >=-10) & (merged_5_df.delay <0),"delay"]= -1
merged_5_df.loc[merged_5_df.delay <-10,"delay"]= -10

merged_5_df.to_csv('../data/csv/merged_5.csv',index=False)


merged_3_df = pd.concat(all_df, ignore_index=True, sort=False)

merged_3_df=merged_3_df.drop(merged_3_df[merged_3_df.delay.isna()].index)


merged_3_df.loc[merged_3_df.delay >0,"delay"]= 1
merged_3_df.loc[merged_3_df.delay ==0,"delay"]= 0
merged_3_df.loc[merged_3_df.delay <0,"delay"]= -1


merged_3_df.to_csv('../data/csv/merged_3.csv',index=False)


