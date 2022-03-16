import pandas as pd
import re


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
            1 means letter is correct but incorrect location (inexact), 
            2 means letter and location are correct (exact)
        words (pd.DataFrame): List of current possible words and their frequencies ['word', 'wordFreq'].

    Returns:
        pd.DataFrame: Filtered words.
    """
    knowns = {'exact':['.']*word_length, 'inexact':{}, 'exclude': set({})}
    for guess, result in guesses.items():
        if len(guess) == word_length:
            knowns = add_known_info(guess=guess, result=result, knowns=knowns)
    filtered_words = words.copy()
    filtered_words = filter_exact(exact=''.join(knowns['exact']), words=filtered_words)
    filtered_words = filter_exclude(exclude=knowns['exclude'], words=filtered_words)
    filtered_words = filter_inexact(inexact=knowns['inexact'], words=filtered_words, word_length=len(knowns['exact']))
    # Sort result by word frequency
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
    mask_contains = pd.Series(mask_contains)
    # Exclude words with inexact matches at all found location(s)
    mask_exclude = [False] * len(words)
    for inexact_match in inexact:
        for index in inexact[inexact_match]:
            regex = list('.'*word_length)
            regex[index] = inexact_match
            regex = ''.join(regex)
            mask_exclude = words['word'].str.match(regex) | mask_exclude
    mask_exclude = pd.Series(mask_exclude)
    if mask_contains.all() & (~mask_exclude).all():
        # No filtering is required
        return words
    else:
        return words[mask_contains & ~mask_exclude]
    

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