import streamlit as st
import pandas as pd
from helper_methods import *

def main():
    datapath = 'Data-Preprocessed/word_freq.csv'
    data = pd.read_csv(datapath).sort_values(by='wordFreq', ascending=False)
    st.write('# The Wordler: Here to help you cheat at Wordle!')
    st.write('Here is the Wordle website: [https://www.nytimes.com/games/wordle/index.html](https://www.nytimes.com/games/wordle/index.html)')

    st.write('Enter the five letter Wordle word, then the feedback you get from Wordle in the text boxes below:')
    col1, col2 = st.columns(2)
    with col1:
        st.write('* 0 for black\n* 1 for yellow\n* 2 for green')
    with col2:
        st.write('Example:')
        st.write('hello')
        st.write('10112')
    st.write('NOTE: If there is a single "l" in the actual word, The Wordler will expect BOTH "l"s to have "1"s, but Wordle will only give the first "l" a "1". For now, you should enter the feedback for both "l"s as "1"s.')
    st.write('## Enter Wordle Guesses and Feedback Below')
    col3, col4 = st.columns(2)
    with col4:
        guesses = {}
        for i in range(1,6):
            st.write(f'### Word {i}')
            word = st.text_input(label=f'Wordle Word {i}', value='', max_chars=5).upper()
            feedback = st.text_input(label=f'Wordle Word {i} Feedback', value='', max_chars=5)
            guesses[word] = convert_feedback(feedback)
        
    with col3:
        if st.button(label='Filter Words', key='button'):
            data = suggest_words(guesses=guesses, words=data)
        if st.button(label='Reset Data Filter'):
            data = pd.read_csv(datapath).sort_values(by='wordFreq', ascending=False)
        st.write(f'Total Number of Words Remaining: {len(data)}')
        st.table(data.iloc[:20])
    return

if __name__ == '__main__':
    main()