import pandas as pd
import streamlit as st


def compare(guess: str, actual: str):
    """
    Compare guess to actual word.

    Args:
        guess (str): _description_
        actual (str): _description_

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


def add_known_info(guess: str, result: list, knowns: dict) -> dict:
    """
    Add new information about correctness of guesses to knowns.

    Args:
        guess (str): _description_
        result (list): _description_
        knowns (dict): {
            'exact':['.']*5, # single regex expression with all exact matches
            'inexact':{
                'A':{0,3,4},
                'C':{2,3},
                etc.
            }, # dictionary with each inexact match letter and known location mismatches
            'exclude': set({}) # set of letters to be excluded entirely
            }

    Returns:
        dict: A copy of knowns with updated information.
    """
    knowns_local = knowns.copy()
    for i in range(len(guess)):
        if guess[i] not in knowns_local['exact']:
            if result[i] == 2:
                knowns_local['exact'][i] = guess[i]
            elif result[i] == 1:
                if guess[i] in knowns_local['inexact']:
                    knowns_local['inexact'][guess[i]].add(i)
                else:
                    knowns_local['inexact'][guess[i]] = set({i})
                #knowns_local['inexact'][guess[i]][i] = guess[i]
            elif result[i] == 0:
                knowns_local['exclude'].add(guess[i])
    return knowns_local


def filter(knowns: dict, words: pd.DataFrame) -> pd.DataFrame:
    """
    Filters words based on knowns.

    Args:
        knowns (dict): {
            'exact':['.']*5, # single regex expression with all exact matches
            'inexact':{
                'A':{0,3,4},
                'C':{2,3},
                etc.
            }, # dictionary with each inexact match letter and known location mismatches
            'exclude': set({}) # set of letters to be excluded entirely
            }
        words (pd.DataFrame): List of current possible words and their frequencies ['word', 'wordFreq'].

    Returns:
        pd.DataFrame: Filtered words.
    """
    filtered_data = words.copy()
    filtered_data = filter_exact(exact=''.join(knowns['exact']), words=filtered_data)
    filtered_data = filter_exclude(exclude=knowns['exclude'], words=filtered_data)
    filtered_data = filter_inexact(inexact=knowns['inexact'], words=filtered_data, word_length=len(knowns['exact']))
    # Sort result by word frequency
    filtered_data = filtered_data.sort_values(by='wordFreq', ascending=False)
    return filtered_data


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
    mask = [False] * len(words)
    for exclusion in exclude:
        mask = words['word'].str.contains(exclusion) | mask
    return words[~pd.Series(mask)]


def filter_inexact(inexact: dict, words: pd.DataFrame, word_length: int) -> pd.DataFrame:
    """
    Filters words based on inexact matches. 
    Retain only words with the inexact matches.
    If a word contains any letters in positions where we know they aren't, filter the word out.

    Args:
        inexact (dict):{
                'A':{0,3,4},
                'C':{2,3},
                etc.
            }, # dictionary with each inexact match letter and known location mismatches
        words (pd.DataFrame): List of current possible words and their frequencies ['word', 'wordFreq'].

    Returns:
        pd.DataFrame: Filtered words.
    """
    # Retain only words containing all inexact matches
    mask_contains = [True] * len(words)
    for inexact_match in inexact:
        mask_contains = words['word'].str.contains(inexact_match) & mask_contains
    # Exclude words with inexact matches at all found location(s)
    mask_exclude = [False] * len(words)
    for inexact_match in inexact:
        for index in inexact[inexact_match]:
            regex = list('.'*word_length)
            regex[index] = inexact_match
            regex = ''.join(regex)
            mask_exclude = words['word'].str.match(regex) | mask_exclude
    return words[pd.Series(mask_contains) & ~pd.Series(mask_exclude)]


def suggest_words(guesses: dict, words: pd.DataFrame, word_length: int=5):
    knowns = {'exact':['.']*word_length, 'inexact':{}, 'exclude': set({})}
    for guess, result in guesses.items():
        if len(guess) == word_length:
            knowns = add_known_info(guess=guess, result=result, knowns=knowns)
    return filter(knowns=knowns, words=words)
    

def convert_feedback(feedback: str) -> list:
    return [int(x) for x in list(feedback)]