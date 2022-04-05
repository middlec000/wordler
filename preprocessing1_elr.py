# Package Imports
import pandas as pd
import time
from src.helper_methods import elr

def main():
    start = time.time()

    df = pd.read_csv('Data-Preprocessed/word_freq.csv').set_index('word')

    print(df.head())

    # Compute ELR
    # See repo README for explanation of Expected List Reduction (ELR)
    df = elr(words=df, word_legnth=5)

    # Print Time
    end = time.time()
    print(f'Seconds Elapsed: {end-start}')
    return

if __name__=='__main__':
    main()