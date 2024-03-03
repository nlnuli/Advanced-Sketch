import numpy as np
import pandas as pd
import scipy.stats as stats
# Data preprocessing:
# label the eight indicator values as Price1, Price2...Price8 respectively, and read the data file
df = pd.read_excel("prices multiasset portfolio 12-9-2016 - Homework Data Set.xlsx")

for i in range(8):
    Price='Price'+str(i+1)
# Linear returns
    linear_return='linear_return'+str(i+1)
    df[linear_return] = df[Price].pct_change()
    # df.to_excel("linear_return.xlsx", index=False)
# Compounded returns
    Log_Return='Log_Return'+str(i+1)
    df[Log_Return] = np.log(df[Price] / df[Price].shift(1))
    # df.to_excel("Log_Return.xlsx", index=False)
    datat={linear_return:df[linear_return],Log_Return:df[Log_Return]}
    # index_row=pd.date_range(start = '1999-04-01', end = '2011-05-17', freq = 'D')
    # index_row=pd.date_range(start='1/4/1999', periods=4517)
    # T = pd.DataFrame(datat,index=index_row)
    T = pd.DataFrame(datat)
    print(T)