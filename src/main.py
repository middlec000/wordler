import streamlit as st
import pandas as pd
from helper_methods import *


def suggest(df: pd.DataFrame, original_length: int, num_words_to_display: int, sort_by: str) -> None:
    """
    Print the suggested words nicely and ordered by the desired metric.

    Args:
        df (pd.DataFrame): Remaining words.
        original_length (int): Original number of words.
        num_words_to_display (int): Number of words to display.
        sort_by (str): How suggestions should be sorted. Supported options:
            'Word Frequency', 
            'Letter Frequency', 
            'Letter at Position Frequency'
    """
    sort_by_to_col_map = {'Word Frequency': 'wordFreq', 'Letter Frequency': 'letterFreqSum', 'Letter at Position Frequency': 'letterPosFreqSum'}
    sort_by_col = sort_by_to_col_map[sort_by]
    df = df.sort_values(by=sort_by_col, ascending=False)
    st.write(f'Words Remaining: {len(df)} ({len(df)*100/original_length:.2f}%)')
    for i in range(min(num_words_to_display, len(df))):
        st.markdown(f"<div style='text-align: center'> {df.iloc[i].name} </div>", unsafe_allow_html=True)
    return


def main():
    # Set Page Configuration
    st.set_page_config(
        initial_sidebar_state='collapsed'
    )
    num_words_to_display = int(st.sidebar.number_input(label='Number of words to suggest', min_value=0, value=10))
    remove_previous_words = st.sidebar.radio(label='Remove previously used Wordle words?', options=['Yes', 'No'], index=1) == 'Yes'
    sort_by = st.sidebar.radio(label='Sort suggested words (high to low) by', options=['Word Frequency', 'Letter Frequency', 'Letter at Position Frequency'], index=1)

    # Get Data
    datapath = 'Data-Preprocessed/word_freq.csv'
    # datapath = 'https://raw.githubusercontent.com/middlec000/wordler/main/Data-Preprocessed/word_freq_wordle_only.csv'
    data = pd.read_csv(datapath).sort_values(by='wordFreq', ascending=False).set_index('word')
    original_length = len(data)
    
    # User Instructions
    st.write('# The Wordler')
    st.write('## Here to help you win Wordle!')
    instructions = st.expander("HELP")
    with instructions:
        st.write('Wordle website: [https://www.nytimes.com/games/wordle/index.html](https://www.nytimes.com/games/wordle/index.html)')
        st.write('Enter Wordle feedback according to the following mapping:\n* Gray -> 0\n* Yellow -> 1\n* Green -> 2')
        st.write('Example Entry: hello-10112')
        st.write('Enter each of your five letter Wordle guesses, a dash (-), then the feedback you get from Wordle in the text boxes below:')
        st.write('Open the sidebar (upper left >) for additional options.')
        st.write('See the GitHub repo for the code and how calculations are performed: \n[https://github.com/middlec000/wordler](https://github.com/middlec000/wordler)')

    st.write('## Enter Guesses and Feedback')
    user_inputs = []
    # Get user input
    for i in range(1,7):
        user_input = st.text_input(label=f'Word{i}-XXXXX',value='', max_chars=11).upper()
        if user_input:
            user_inputs.append(user_input)
    
    st.write('## Words Suggested by Wordler:')
    # Check User Input
    guesses, bad_input = check_convert_input(user_inputs=user_inputs)
    if bad_input:
        st.warning('Input is invalid - please see example above.')
    # Display (Filtered) Words
    if guesses and not bad_input:
        filtered_data = filter_words(guesses=guesses, words=data, remove_previous_wordle_words=remove_previous_words)
        suggest(df=filtered_data, original_length=original_length, num_words_to_display=num_words_to_display, sort_by=sort_by)
    else:
        suggest(df=data, original_length=original_length, num_words_to_display=num_words_to_display, sort_by=sort_by)
    return

if __name__ == '__main__':
    main()