import streamlit as st
import pandas as pd
from helper_methods import *

def main():
    # Get Data
    datapath = 'Data-Preprocessed/word_freq.csv' # TODO: update w/url
    data = pd.read_csv(datapath).sort_values(by='wordFreq', ascending=False)
    data_length = len(data)

    # User Instructions
    st.write('# The Wordler: Here to help you cheat at Wordle!')
    st.write('Here is the Wordle website: [https://www.nytimes.com/games/wordle/index.html](https://www.nytimes.com/games/wordle/index.html)')

    st.write('Enter the five letter Wordle word, then the feedback you get from Wordle in the text boxes below:')
    col1, col2 = st.columns(2)
    with col1:
        st.write('* 0 for black\n* 1 for yellow\n* 2 for green')
    with col2:
        st.write('Example Entry:')
        st.write('hello-10112')
    st.write('NOTE: For the example word of "hello", if there is a single "l" in the actual word, The Wordler will expect BOTH "l"s to have "1"s, but Wordle will only give the first "l" a "1". For now, you should enter the feedback for both "l"s as "1"s.')
    st.write('## Enter Wordle Guesses and Feedback Below')
    col3, col4 = st.columns(2)
    user_inputs = []
    with col4:
        # Get user input
        for i in range(1,7):
            st.write(f'### Word {i}')
            user_input = st.text_input(label=f'Word{i}-XXXXX',value='', max_chars=11).upper()
            if user_input:
                user_inputs.append(user_input)
        
    with col3:
        # Check User Input
        guesses, bad_input = check_convert_input(user_inputs=user_inputs)
        if bad_input:
            st.warning('Input is invalid - please see example above.')
        # Display Filtered Data
        if guesses and not bad_input:
            filtered_data = filter_words(guesses=guesses, words=data)
            data_length = len(filtered_data)
            st.write(f'Total Number of Words Remaining: {data_length}')
            st.table(filtered_data.iloc[:24])
        else:
            st.write(f'Total Number of Words Remaining: {data_length}')
            st.table(data.iloc[:24])
    return

if __name__ == '__main__':
    main()