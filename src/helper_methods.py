import pandas as pd
import re
import streamlit as st


def compare(guess: str, actual: str):
    """
    Compare guess to actual word.

    Args:
        guess (str): Guessed word.
        actual (str): Actual word.

    Returns:
        comparison (List[int]):
            0 means not correct, 
            1 means correct letter + incorrect location, 
            2  means correct word + correct location
    """
    if len(guess) != len(actual):
        print('Lengths do not match!')
    comparison = [0] * len(actual)
    for i in range(len(actual)):
        if guess[i] == actual[i]:
            comparison[i] = 2
        elif guess[i] in actual:
            comparison[i] = 1
    return comparison


def repeated_letter(word: str) -> dict:
    """
    Check if a word has repeated letters.

    Args:
        word (str): Word to check.

    Returns:
        dict: {
            'A':{1,2},
            'B':{0,3},
            etc.
        } # Dictionary of repeated letters and the indices where they are repeated.
    """
    repeats = {}
    for i_a in range(len(word)):
        letter_a = word[i_a]
        for i_b in range(i_a+1, len(word)):
            letter_b = word[i_b]
            if letter_a == letter_b:
                if letter_a in repeats:
                    repeats[letter_a].add(i_b)
                else:
                    repeats[letter_a] = set({i_a, i_b})
    return repeats


def add_known_info(guess: str, result: list, knowns: dict) -> dict:
    """
    Add new information about correctness of guesses to knowns.

    Args:
        guess (str): _description_
        result (list): _description_
        knowns (dict): {
            'exact':['.']*5, # Single regex expression with all exact matches
            'exclude_at':{
                'A':{0,3,4},
                'C':{2,3},
                etc.
            }, # Dictionary with each exclude_at match letter and known location mismatches
            'exclude': set({}), # set of letters to be excluded entirely
            max_num_letters (dict): {
            'A':3,
            'B':1,
            etc.
        } # Dictionary of letters with known maximums repeats and their maximums.
            }

    Returns:
        dict: A copy of knowns with updated information.
    """
    knowns_local = knowns.copy()
    repeats = repeated_letter(word=guess)
    for i in range(len(guess)):
        if result[i] == 2:
            knowns_local['exact'][i] = guess[i]
        elif result[i] == 1:
            if guess[i] in knowns_local['exclude_at']:
                knowns_local['exclude_at'][guess[i]].add(i)
            else:
                knowns_local['exclude_at'][guess[i]] = set({i})
        elif result[i] == 0:
            if guess[i] in repeats:
                all_exclusions = True
                for r in repeats[guess[i]]:
                    if result[r] != 0:
                        all_exclusions = False
                        if guess[i] not in knowns_local['max_num_letter']:
                            max_num = 0
                            for rr in repeats[guess[i]]:
                                if result[rr] != 0:
                                    max_num += 1
                            knowns_local['max_num_letter'][guess[i]] = max_num
                if all_exclusions:
                    knowns_local['exclude'].add(guess[i])
                else:
                    if guess[i] in knowns_local['exclude_at']:
                        knowns_local['exclude_at'][guess[i]].add(i)
                    else:
                        knowns_local['exclude_at'][guess[i]] = set({i})
            else:
                knowns_local['exclude'].add(guess[i])
    return knowns_local


def filter_words(guesses: dict, words: pd.DataFrame, word_length: int=5) -> pd.DataFrame:
    """
    Filters words based on guesses.

    Args:
        guesses (dict): {
            'word1':[X,X,X,X,X],
            'word2':[X,X,X,X,X],
            etc.
        } # Tracks each word and feedback
            0 means letter is not correct (exclude), 
            1 means letter is correct but incorrect location (exclude_at), 
            2 means letter and location are correct (exact)
        words (pd.DataFrame): List of current possible words and their frequencies ['word', 'wordFreq'].

    Returns:
        pd.DataFrame: Filtered words.
    """
    knowns = {'exact':['.']*word_length, 'exclude_at':{}, 'exclude': set({})}
    for guess, result in guesses.items():
        if len(guess) == word_length:
            knowns = add_known_info(guess=guess, result=result, knowns=knowns)
    filtered_words = words.copy()
    filtered_words = filter_exact(exact=''.join(knowns['exact']), words=filtered_words)
    filtered_words = filter_exclude(exclude=knowns['exclude'], words=filtered_words)
    filtered_words = filter_exclude_at(exclude_at=knowns['exclude_at'], words=filtered_words, word_length=len(knowns['exact']))
    filtered_words = filter_max_num_letters(max_num_letters=knowns['max_num_letters'], words=filtered_words)
    filtered_words = filtered_words.sort_values(by='wordFreq', ascending=False)
    return filtered_words


def filter_exact(exact: str, words: pd.DataFrame) -> pd.DataFrame:
    """
    Filter words by retaining only those that contain the regex exact.

    Args:
        exact (str): Regex with letters of known position.
        words (pd.DataFrame): List of current possible words and their frequencies ['word', 'wordFreq'].

    Returns:
        pd.DataFrame: Filtered words.
    """
    return words[words['word'].str.match(exact)]


def filter_exclude(exclude: set, words: pd.DataFrame) -> pd.DataFrame:
    """
    Filter words by removing any letter in exclude.

    Args:
        exclude (set): Set of words to exclude entirely from dataset.
        words (pd.DataFrame): List of current possible words and their frequencies ['word', 'wordFreq'].

    Returns:
        pd.DataFrame: Filtered words.
    """
    mask = pd.Series([False] * len(words), index=words.index)
    for exclusion in exclude:
        mask = words['word'].str.contains(exclusion) | mask
    return words[~mask]


def filter_exclude_at(exclude_at: dict, words: pd.DataFrame, word_length: int) -> pd.DataFrame:
    """
    Filters words based on exclude_at matches. 
    Retain only words with the exclude_at matches.
    If a word contains any letters in positions where we know they aren't, filter the word out.

    Args:
        exclude_at (dict):{
                'A':{0,3,4},
                'C':{2,3},
                etc.
            }, # dictionary with each exclude_at match letter and known location mismatches
        words (pd.DataFrame): List of current possible words and their frequencies ['word', 'wordFreq'].

    Returns:
        pd.DataFrame: Filtered words.
    """
    # Retain only words containing all exclude_at matches
    mask_contains = pd.Series([True] * len(words), index=words.index)
    for exclude_at_match in exclude_at:
        mask_contains = words['word'].str.contains(exclude_at_match) & mask_contains
    # Exclude words with exclude_at matches at all found location(s)
    mask_exclude = pd.Series([False] * len(words), index=words.index)
    for exclude_at_match in exclude_at:
        for index in exclude_at[exclude_at_match]:
            regex = list('.'*word_length)
            regex[index] = exclude_at_match
            regex = ''.join(regex)
            mask_exclude = words['word'].str.match(regex) | mask_exclude
    return words[mask_contains & ~mask_exclude]


def filter_max_num_letters(max_num_letters: dict, words: pd.DataFrame) -> pd.DataFrame:
    """
    Filters words by removing any words with letters repeated more than specified in max_num_letters.

    Args:
        max_num_letters (dict): {
            'A':3,
            'B':1,
            etc.
        } # Dictionary of letters with known maximums repeats and their maximums.
        words (pd.DataFrame): List of current possible words and their frequencies ['word', 'wordFreq'].

    Returns:
        pd.DataFrame: Filtered words.
    """
    if max_num_letters:
        filtered_words = words.copy()
        for restricted_letter in max_num_letters:
            mask = filtered_words['word'].apply(lambda x: x.count(restricted_letter) > max_num_letters[restricted_letter])
            filtered_words = filtered_words[~mask]
        return filtered_words
    else:
        return words


def check_convert_input(user_inputs: list):
    """
    Check input for erroneous formatting.
    If input is clean, convert it to more useful format.

    Args:
        guesses (dict): {
            'word1':'XXXXX',
            'word2':'XXXXX',
            etc.
        }

    Returns:
        guesses (dict): {
            'word1':[X,X,X,X,X],
            'word2':[X,X,X,X,X],
            etc.
        }
        bad_input (bool): True if input is incorrect format.
    """
    guesses = {}
    bad_input = False
    for user_input in user_inputs:
        if re.match(pattern='[A-Z]{5}[-][0-2]{5}', string=user_input):
            guesses[user_input.split('-')[0]] = [int(x) for x in list(user_input.split('-')[1])]
        else:
            bad_input = True
    return guesses, bad_input


def suggest(df: pd.DataFrame, original_length: int, num_words_to_display: int) -> None:
    """
    Print the suggested words nicely.

    Args:
        df (pd.DataFrame): Remaining words.
        original_length (int): Original number of words.
        num_words_to_display (int): Number of words to display.
    """
    st.write(f'Words Remaining: {len(df)} ({len(df)*100/original_length:.2f}%)')
    for i in range(min(num_words_to_display, len(df))):
        st.markdown(f"<div style='text-align: center'> {df['word'].iloc[i]} </div>", unsafe_allow_html=True)
    return