# Package Imports
import pandas as pd
import numpy as np
import time
import multiprocessing as mp
from src.helper_methods import filter_words, compare # elr


def elr_multiprocess(words: pd.DataFrame, idx0: int, idx1: int, word_legnth: int, q: mp.Queue) -> pd.DataFrame:
    # Iterate over all potential guesses
    for guess in words.index[idx0:idx1]:
        # Iterate over all potential Wordle words
        for potential_wordle_word in words.index:
            if guess != potential_wordle_word:
                guesses = {guess: compare(guess=guess, actual=potential_wordle_word)}
                filtered_words = filter_words(guesses=guesses, words=words, remove_previous_wordle_words=False, word_length=word_legnth)
                words.loc[guess, 'ELR'] += len(filtered_words)
    q.put(words.iloc[idx0:idx1])
    return

def main():
    start = time.time()
    num_words = 10

    df = pd.read_csv('Data-Preprocessed/word_freq.csv').set_index('word')
    df['ELR'] = 1.0
    # df = df.iloc[:num_words]
    print(f'Original Length: {len(df)}')
    num_cores = mp.cpu_count()
    print(f'Number of Cores: {num_cores}')
    chunk_size = int(np.ceil(len(df) / num_cores))
    print(f'Chunk Size: {chunk_size}')
    queues = [mp.Queue() for i in range(num_cores)]
    processes = [mp.Process(target=elr_multiprocess, args=(df, i*chunk_size, (i+1)*chunk_size, 5, queues[i])) for i in range(num_cores)]
    for p in processes:
        p.start()
    for p in processes:
        p.join() 
    results = []
    for q in queues:
        results.append(q.get())
    df = pd.concat(results, axis=0)
    df['ELR'] = 1 - (df['ELR'] / len(df)**2)
    print(df.head())

    # Save Data
    df.reset_index().to_csv('Data-Preprocessed/word_elr.csv', index=False)

    # Print Time
    end = time.time()
    print(f'Words: {len(df)}\nSeconds Elapsed: {end-start}')
    return

if __name__=='__main__':
    main()