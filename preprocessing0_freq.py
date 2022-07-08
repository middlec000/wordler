# Package Imports
import pandas as pd
import re
import time
from string import ascii_uppercase


def get_counts(letters: list, positions: list, df: pd.DataFrame) -> pd.DataFrame:
    tracker = pd.DataFrame(columns=['letter', 'position', 'letterPosFreq'])
    for letter in letters:
        for position in positions:
            # Generate regex
            regex = list('.'*len(positions))
            regex[position] = letter
            regex = ''.join(regex)
            # Calculate and record
            tracker = pd.concat([tracker, pd.DataFrame(data={'letter': letter, 'position': position, 'letterPosFreq': len(df[df['word'].str.match(regex)])}, index=[0])], ignore_index=True)
    return tracker.set_index(['letter', 'position'])

def get_letter_pos_freq_sum(word: list, letter_pos_freq: pd.DataFrame) -> int:
    a = 0
    for i in range(len(word)):
        letter = word[i]
        a += letter_pos_freq.loc[letter, i]['letterPosFreq']
    return a

def get_time() -> str:
    return time.strftime("%H:%M:%S", time.gmtime(time.time()))


def main():
    times = {'start': get_time()}
    print(f'pandas: {pd.__version__}')
    print(f're: {re.__version__}')

    # Global Variables
    WORD_LENGTH = 5

    # List of Wordle Words
    with open('Data-Original/wordle_words_04_15_22.txt', 'r') as file:
        wordle_words = file.read().replace('\n', '').replace('"', '').replace(',', '').upper().split(' ')
    df = pd.DataFrame(data={'word': wordle_words,'wordFreq': [0]*len(wordle_words)}).set_index('word')
    print(f'# Wordle Words: {len(df)}')

    # Kaggle Dataset
    kaggle = pd.read_csv('Data-Original/unigram_freq.csv')
    kaggle['word'] = kaggle['word'].astype('str').str.upper()
    # Correct length and is a Wordle word
    mask = kaggle['word'].apply(lambda x: (len(x) == WORD_LENGTH) & (x in df.index))
    kaggle = kaggle[mask]
    kaggle = kaggle.rename(columns={'count':'wordFreq'})
    kaggle = kaggle.set_index('word')
    print(f'# Kaggle Words: {len(df)}')
    df.update(other=kaggle, join='left', overwrite=True)

    # wordfrequency.info Dataset
    word_freq = pd.read_excel('Data-Original/lemmas_60k_words.xlsx')
    word_freq = pd.DataFrame(data={'wordFreq': word_freq['wordFreq'].astype('int'), 'word': word_freq['word'].astype('str').str.upper()})
    # Remove punctuation
    word_freq['word'] = word_freq['word'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
    # Correct length and is a Wordle word
    mask = word_freq['word'].apply(lambda x: (len(x) == WORD_LENGTH) & (x in df.index)).values
    word_freq = word_freq[mask]
    # Also want word to not have frequency from Kaggle dataset
    mask = word_freq['word'].apply(lambda x: df.loc[x] == 0).values
    word_freq = word_freq[mask].set_index('word')
    print(f'# word_freq Words: {len(word_freq)}')
    df.update(other=word_freq, join='left', overwrite=True)
    df = df.reset_index()
    times['wordFreq'] = get_time()

    # Compute sum of letter frequency and sum of letter position frequency
    letter_pos_freq = get_counts(letters=list(ascii_uppercase), positions=[0,1,2,3,4], df=df)
    letter_freq = letter_pos_freq.reset_index().drop('position', axis=1).groupby('letter').sum().sort_values(by='letterPosFreq', ascending=False).rename(columns={'letterPosFreq':'letterFreq'})
    df['letterFreqSum'] = df['word'].apply(lambda x: sum([letter_freq.loc[letter, 'letterFreq'] for letter in set(x)]))
    df['letterPosFreqSum'] = df['word'].apply(lambda x: get_letter_pos_freq_sum(word=x, letter_pos_freq=letter_pos_freq))

    # Save Preprocessed Data
    df.to_csv('Data-Preprocessed/word_freq.csv', index=False)

    # Print Time
    times['end']= get_time()
    print(f'Times:\n{times}')
    return

if __name__=='__main__':
    main()