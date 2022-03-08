import string
import re
import pandas as pd

def compare(guess: str, actual: str):
    """
    0 means not correct, 
    1 means correct letter + incorrect location, 
    2  means correct word + correct location

    Args:
        guess (str): _description_
        actual (str): _description_

    Returns:
        _type_: _description_
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
    knowns_local = knowns.copy()
    for i in range(len(guess)):
        if guess[i] not in knowns_local['exact']:
            if result[i] == 2:
                knowns_local['exact'][i] = guess[i]
            elif result[i] == 1:
                knowns_local['inexact'][guess[i]][i] = guess[i]
            elif result[i] == 0:
                knowns_local['exclude'].add(guess[i])
    return knowns_local

def filter(knowns: dict, words: pd.DataFrame) -> pd.DataFrame:
    # Filter by exact matches
    regex = ''.join(knowns['exact'])
    filtered_data = words[words['word'].str.match(regex)]
    # Filter by exclude - must contain none of these
    mask = [False] * len(filtered_data)
    for exclusion in knowns['exclude']:
        mask = filtered_data['word'].str.contains(exclusion) | mask
    filtered_data = filtered_data[~mask]
    # Filter by inexact matches - must contain all
    mask = [True] * len(filtered_data)
    for inexact_match in knowns['inexact']:
        if re.search('[A-Z]', ''.join(knowns['inexact'][inexact_match])):
            mask = filtered_data['word'].str.contains(inexact_match) & mask
    filtered_data = filtered_data[mask]
    # Filter by inexact matches - must not contain at specific locations
    mask = [False] * len(filtered_data)
    for inexact_match in knowns['inexact']:
        if re.search('[A-Z]', ''.join(knowns['inexact'][inexact_match])):
            regex = ''.join(knowns['inexact'][inexact_match])
            mask = filtered_data['word'].str.match(regex) | mask
    filtered_data = filtered_data[~mask]
    # Sort result by count
    filtered_data = filtered_data.sort_values(by='count', ascending=False)
    return filtered_data