import pandas as pd
import re


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
    repeats = {'letters':{}, 'indices':set({})}
    for i_a in range(len(word)):
        letter_a = word[i_a]
        for i_b in range(i_a+1, len(word)):
            letter_b = word[i_b]
            if letter_a == letter_b:
                if letter_a in repeats:
                    repeats['letters'][letter_a].add(i_b)
                    repeats['indices'].add(i_b)
                else:
                    repeats['letters'][letter_a] = set({i_a, i_b})
                    repeats['indices'].add(i_a)
                    repeats['indices'].add(i_b)
    return repeats


def compare(guess: str, actual: str) -> list:
    """
    Compares guess to actual. This method is intended to match the output from the Wordle game.

    This method iterates through the 'guess' and 'actual' words twice. 
    The first pass is to find exact matches, removing these from the remaining letters in 'actual'.
    The second pass finds all inexact matches, the remaining letters are left as exclusions.

    Args:
        guess (str): Wordle guess word.
        actual (str): Dummy Wordle actual word.

    Returns:
        list: Response to guess if actual is the actual Wordle word.
    """
    remaining_letters_actual = list(actual)
    result = [0] * len(guess)
    # First pass: look for exact matches
    for i in range(len(guess)):
        guess_letter = guess[i]
        if guess_letter == remaining_letters_actual[i]:
            result[i] = 2
            remaining_letters_actual[i] = -1
    # Second pass: look for inexact matches
    for i in range(len(guess)):
        if result[i] != 2:
            guess_letter = guess[i]
            if guess_letter in remaining_letters_actual:
                result[i] = 1
                # Actual letter is at another index location, so use remove instead of index reassignment
                remaining_letters_actual.remove(guess_letter)
    # All other letters will be treated as exclusions
    return result


def add_known_info(guess: str, result: list, knowns: dict) -> dict:
    """
    Add new information about correctness of guesses to knowns.

    Args:
        guess (str): Wordle guess word.
        result (list): Response from Wordle: [X,X,X,X,X] (ints: 0, 1, or 2)
        knowns (dict): {
            'exact':['.']*5, # Single regex expression with all exact matches
            'exclude_at':{
                'A':{0,3,4},
                'C':{2,3},
                etc.
                }, # Dictionary with each exclude_at match letter and known location mismatches
            'exclude': set({}), # set of letters to be excluded entirely
            'max_num_letter' (dict): {
                'A':3,
                'B':1,
                etc.
                } # Dictionary of letters with known maximums repeats and their maximums.
            'min_num_letter' (dict): {
                'A':3,
                'B':1,
                etc.
                } # Dictionary of letters with known minimum repeats and their minimums.
            }

    Returns:
        dict: A copy of knowns with updated information.
    """
    letter_num = dict(zip(set(guess), [0]*len(guess)))
    knowns_local = knowns.copy()
    # First pass: look for exact and inexact matches
    for i in range(len(guess)):
        letter = guess[i]
        if result[i] == 2:
            letter_num[letter] += 1
            knowns_local['exact'][i] = letter
        elif result[i] == 1:
            letter_num[letter] += 1
            if letter in knowns_local['exclude_at']:
                knowns_local['exclude_at'][letter].add(i)
            else:
                knowns_local['exclude_at'][letter] = set({i})
    # Add nonzero letter numbers to min_num_letter in known_info
    letter_num = dict(filter(lambda item: item[1] != 0, letter_num.items()))
    for letter in letter_num:
        if letter in knowns_local['min_num_letter']:
            knowns_local['min_num_letter'][letter] = max(knowns_local['min_num_letter'][letter], letter_num[letter])
        else:
            knowns_local['min_num_letter'][letter] = letter_num[letter]
    # Second pass: look for and check exclusions, get max nums
    for i in range(len(guess)):
        if result[i] == 0:
            letter = guess[i]
            if letter not in knowns_local['exact'] and letter not in knowns_local['exclude_at']:
                knowns_local['exclude'].add(letter)
            else:
                if letter in knowns_local['exclude_at']:
                    knowns_local['exclude_at'][letter].add(i)
                else:
                    knowns_local['exclude_at'][letter] = set({i})
                knowns_local['max_num_letter'][letter] = letter_num[letter]
    return knowns_local


def filter_words(guesses: dict, words: pd.DataFrame, remove_previous_wordle_words: bool, word_length: int=5) -> pd.DataFrame:
    """
    Filters words based on guesses.

    Args:
        guesses (dict): {
            'word1':[X,X,X,X,X],
            'word2':[X,X,X,X,X],
            etc.
            }   # Tracks each word and feedback
                # 0 means letter is not correct (exclude), 
                # 1 means letter is correct but incorrect location (exclude_at), 
                # 2 means letter and location are correct (exact)
        words (pd.DataFrame): List of current possible words and their characteristics (index is 'word').
        remove_previous_wordle_words (bool): Remove previously used Wordle words from suggested words list. 
            List of previous Wordle words pulled from: https://raw.githubusercontent.com/eagerterrier/previous-wordle-words/main/alphabetical.txt
        word_length (int): Set length of words. (Defaults to 5)

    Returns:
        pd.DataFrame: Filtered words.
    """
    knowns = {'exact':['.']*word_length, 'exclude_at':{}, 'exclude': set({}), 'max_num_letter':{}, 'min_num_letter':{}}
    for guess, result in guesses.items():
        if len(guess) == word_length:
            knowns = add_known_info(guess=guess, result=result, knowns=knowns)
    filtered_words = words.copy()
    if remove_previous_wordle_words:
        filtered_words = filter_previous_words(words=filtered_words)
    # Filter exact matches
    filtered_words = filtered_words.filter(regex=''.join(knowns['exact']), axis=0)
    filtered_words = filter_exclude(exclude=knowns['exclude'], words=filtered_words)
    filtered_words = filter_exclude_at(exclude_at=knowns['exclude_at'], words=filtered_words, word_length=len(knowns['exact']))
    filtered_words = filter_max_num_letter(max_num_letter=knowns['max_num_letter'], words=filtered_words)
    filtered_words = filter_min_num_letter(min_num_letter=knowns['min_num_letter'], words=filtered_words)
    return filtered_words


def filter_previous_words(words: pd.DataFrame) -> pd.DataFrame:
    """
    Filter words by retaining only words that have not been used in the Wordle game before.

    Args:
        words (pd.DataFrame): List of current possible words and their characteristics (index is 'word').

    Returns:
        pd.DataFrame: Filtered words.
    """
    url = 'https://raw.githubusercontent.com/eagerterrier/previous-wordle-words/main/alphabetical.txt'
    previous_words = list(pd.read_csv(url, header=None).squeeze().str.upper())
    filtered_index = pd.Index(data=[word for word in words.index if word not in previous_words])
    return words.loc[filtered_index]


def filter_exclude(exclude: set, words: pd.DataFrame) -> pd.DataFrame:
    """
    Filter words by removing any letter in exclude.

    Args:
        exclude (set): Set of words to exclude entirely from dataset.
        words (pd.DataFrame): List of current possible words and their characteristics (index is 'word').

    Returns:
        pd.DataFrame: Filtered words.
    """
    mask = pd.Series([False] * len(words), index=words.index, dtype=bool)
    for exclusion in exclude:
        mask = words.index.str.contains(exclusion) | mask
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
            }, # Dictionary with each exclude_at match letter and known location mismatches
        words (pd.DataFrame): List of current possible words and their characteristics (index is 'word').
        word_length (int): Length of words in words list.

    Returns:
        pd.DataFrame: Filtered words.
    """
    # Retain only words containing all exclude_at (inexact) matches
    mask_include = pd.Series([True] * len(words), index=words.index, dtype=bool)
    for inexact_match in exclude_at:
        mask_include = words.index.str.contains(inexact_match) & mask_include
    # Exclude words with exclude_at matches at all found location(s)
    mask_exclude = pd.Series([False] * len(words), index=words.index, dtype=bool)
    for inexact_match in exclude_at:
        for index in exclude_at[inexact_match]:
            regex = list('.'*word_length)
            regex[index] = inexact_match
            regex = ''.join(regex)
            mask_exclude = words.index.str.match(regex) | mask_exclude
    return words[mask_include & ~mask_exclude]


def filter_max_num_letter(max_num_letter: dict, words: pd.DataFrame) -> pd.DataFrame:
    """
    Filters words by removing any words with letters repeated more than specified in max_num_letter.

    Args:
        max_num_letter (dict): {
            'A':3,
            'B':1,
            etc.
        } # Dictionary of letters with known maximums repeats and their maximums.
        words (pd.DataFrame): List of current possible words and their characteristics (index is 'word').

    Returns:
        pd.DataFrame: Filtered words.
    """
    if max_num_letter:
        filtered_words = pd.Series(data=words.index)
        for restricted_letter in max_num_letter:
            mask = filtered_words.apply(lambda x: x.count(restricted_letter) > max_num_letter[restricted_letter])
            filtered_words = filtered_words[~mask]
        return words.loc[filtered_words]
    else:
        return words


def filter_min_num_letter(min_num_letter: dict, words: pd.DataFrame) -> pd.DataFrame:
    """
    Filters words by removing any words with letters repeated less than specified in min_num_letter.

    Args:
        min_num_letter (dict): {
            'A':3,
            'B':1,
            etc.
            } # Dictionary of letters with known minimum repeats and their minimums.
        words (pd.DataFrame): List of current possible words and their characteristics (index is 'word').

    Returns:
        pd.DataFrame: Filtered words.
    """
    if min_num_letter:
        filtered_words = pd.Series(data=words.index)
        for restricted_letter in min_num_letter:
            mask = filtered_words.apply(lambda x: x.count(restricted_letter) < min_num_letter[restricted_letter])
            filtered_words = filtered_words[~mask]
        return words.loc[filtered_words]
    else:
        return words


def elr(words: pd.DataFrame, word_legnth: int) -> pd.DataFrame:
    """
    Calculate the Expected List Reduction (see README for repo) for each word in words.

    Args:
        words (pd.DataFrame): List of current possible words and their characteristics (index is 'word').
        word_legnth (int): Length of words to consider.

    Returns:
        pd.DataFrame: words with added 'ELR' column.
    """
    tracker = words.copy()
    tracker['ELR'] = [1.0]*len(tracker)
    # Iterate over all potential guesses
    for guess in tracker.index:
        # Iterate over all potential Wordle words
        for potential_wordle_word in tracker.index:
            if guess != potential_wordle_word:
                guesses = {guess: compare(guess=guess, actual=potential_wordle_word)}
                filtered_words = filter_words(guesses=guesses, words=words, remove_previous_wordle_words=False, word_length=word_legnth)
                tracker.loc[guess, 'ELR'] += len(filtered_words)
    tracker['ELR'] = 1 - (tracker['ELR'] / len(words)**2)
    return tracker


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