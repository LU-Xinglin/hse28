import os
import pandas as pd

folder_path = ""

csv_files = [f for f in os.listdir(folder_path) if f.startswith('data_')]

dfs = []
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    dfs.append(df)

final_df = pd.concat(dfs, ignore_index=True)

final_df.to_csv("merged_25001-26455.csv", index=False, encoding="utf-8-sig")
