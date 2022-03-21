import streamlit as st
import pandas as pd
from helper_methods import *

def main():
    # Set Page Configuration
    st.set_page_config(
        initial_sidebar_state='collapsed'
    )
    num_words_to_display = int(st.sidebar.number_input(label='Number of words to suggest', min_value=0, value=10))
    remove_previous_words = st.sidebar.radio(label='Remove previously used Wordle words', options=['No', 'Yes']) == 'Yes'

    # Get Data
    # datapath = 'Data-Preprocessed/word_freq_wordle_only.csv'
    datapath = 'https://raw.githubusercontent.com/middlec000/wordler/main/Data-Preprocessed/word_freq_wordle_only.csv'
    data = pd.read_csv(datapath).sort_values(by='wordFreq', ascending=False)
    original_length = len(data)
    
    # User Instructions
    st.write('# The Wordler')
    st.write('## Here to help you win Wordle!')
    st.write('Here is the Wordle website: [https://www.nytimes.com/games/wordle/index.html](https://www.nytimes.com/games/wordle/index.html)')
    instructions = st.expander("How to enter your words")
    with instructions:
        col11, col12, col13 = st.columns(3)
        with col11:
            st.write('Gray -> 0')
        with col12:
            st.write('Yellow -> 1')
        with col13:
            st.write('Green -> 2')
        st.write('Example Entry: hello-10112')
        st.write('Enter each of your five letter Wordle guesses, a dash (-), then the feedback you get from Wordle in the text boxes below:')
        st.write('See left sidebar for additional options.')

    st.write('## Enter Your Guesses')
    user_inputs = []
    # Get user input
    for i in range(1,7):
        user_input = st.text_input(label=f'Word{i}-XXXXX',value='', max_chars=11).upper()
        if user_input:
            user_inputs.append(user_input)
    
    st.write('## Wordler Suggested Words')
    # Check User Input
    guesses, bad_input = check_convert_input(user_inputs=user_inputs)
    if bad_input:
        st.warning('Input is invalid - please see example above.')
    # num_words_to_display = int(st.number_input(label='Number of words to display', min_value=0, value=10))
    # Display (Filtered) Words
    if guesses and not bad_input:
        filtered_data = filter_words(guesses=guesses, words=data, remove_previous_words=remove_previous_words)
        suggest(df=filtered_data, original_length=original_length, num_words_to_display=num_words_to_display)
    else:
        suggest(df=data, original_length=original_length, num_words_to_display=num_words_to_display)
    return

if __name__ == '__main__':
    main()