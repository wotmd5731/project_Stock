# -*- coding: utf-8 -*-

import pandas as pd

df = pd.read_excel("./List.xlsx")
df = df[['회사명','종목코드']].iloc[0:10]

for idx, row in df.iterrows():
    print(row[1])
    


