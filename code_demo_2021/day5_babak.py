import pandas as pd
import numpy as np


def naughty_recognizer(df):
    forb_cond = pd.Series(np.zeros(len(df)))
    double_cond = pd.Series(np.zeros(len(df)))
    vowel_cond = pd.Series(np.zeros(len(df)))

    for i in range(len(strings.columns) -1 ): # -1 is for staying in bounds
        # removing forbidden combos
        forb_cond += (df[i] + df[i+1]).isin(['ab','cd','pq','xy']).astype(int)
        # keeping the double ones
        double_cond += (df[i] == df[i+1]).astype(int)
        
    # keeping the more than 3 vowels
    for i in range(len(df.columns)):
        vowel_cond += (df[i].isin(list('aioue'))).astype(int)
        
    forb_cond = forb_cond == 0
    double_cond = double_cond != 0
    vowel_cond = vowel_cond >= 3
    return(sum(forb_cond & double_cond & vowel_cond))


data = pd.read_csv('day5_input.txt', header=None)
strings = pd.DataFrame(data[0].apply(list).tolist())
print('The answer is: ',naughty_recognizer(strings))
