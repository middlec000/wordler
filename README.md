# The Wordler
A program to help you play the game [Wordle](https://www.nytimes.com/games/wordle/index.html).  
Visit the Streamlit website to view instructions and to use this program:  
[https://share.streamlit.io/middlec000/wordler/main/src/main.py](https://share.streamlit.io/middlec000/wordler/main/src/main.py)  

Why this application is helpful:  
1. It knows all possible Wordle words and all previously used Wordle words.
2. It removes words that cannot be today's answer based on the feedback you provide from Wordle.
3. It can remove previously used Wordle words.
4. It sorts suggested words by either frequency of use or how much the word is expected to help reduce the remaining words list.

# How the Filtering Works
This program is designed to take advantage of ALL information contained in the responses from Wordle.  
Users must enter their guessed words followed by Wordle's response transformed to a sequence of numbers according to the following schema:
* Grey -> 0  
* Yellow -> 1  
* Green -> 2    

The possible Wordle words list is filtered sequentially based on the Wordle guesses and responses you provide in the following manner:  
1. (Optional) Filter out previously used Wordle words.
1. Filter on exact letter matches (letters with known positions)
   - Example: Guess = HELLO, Wordle's Response = 02222
   - This filter will only retain words with '_ELLO'
2. Filter on letter exclusions (letters that are known not to be in the answer Wordle word)
   - Example: Guess = HELLO, Wordle's Response = 02222
   - This filter will exclude all words that contain an 'H'
3. Filter on inexact matches (letters that are known to be in the answer word but only positions where they do not reside are known)
   - Example: Guess = HELLO, Wordle's Response = 11001
   - This filter will retain only words that contain an 'H', an 'E', and an 'O' AND exclude all words with an 'H' as the first letter, an 'E' as the second letter, and an 'O' as the fifth letter
4. Filter on maximum possible number of each letter (if some, but not all of a repeated letter in the guess are in the answer word)
   - Example: Guess = HELLO, Wordle's Response = 02201
   - This filter will exclude all words with more than one 'L'
5. Filter on minimum possible number of each letter (if more than one of a multiple letter are found to be in the answer word)
   - Example: Guess = HELLO, Wordle's Response = 02222
   - This filter will exclude all words with fewer than two 'L's

# How the Word Suggestions are Ordered
Whichever option you choose to sort your suggested words, this app will always help you quickly and intelligently narrow down the list of potential words that could be the answer based on feedback from the Wordle game. The approaches below simply tell The Wordler how to order the words it suggests to you.

## Word Frequency Approach
More frequently used (more common) words are suggested above less frequently used ones.

## Letter Frequency Approach
The frequencies of all letters in the words list has been calculated. For each potential guess, the word list frequencies of all the letters in that word are added. Words with a higher sum of letter frequencies are suggested first.  

(Coming Soon) The ability to recalculate this metric based on the filtered words list.

## Letter at Position Frequency Approach
The frequencies of each letter in each position have been calculated. For each potential guess, the word list frequencies of all the (letter at that position)s in that word are added. Words with a higher sum of (letter at that position) frequencies are suggested first.  

(Coming Soon) The ability to recalculate this metric based on the filtered words list.

## Expected List Reduction Approach (Coming Soon)
Rank words by how helpful they are at reducing the remaining words list and suggest more helpful words first.  

For each word, find out how much we can expect guessing that word will reduce the remaining words list via filtering. The amount by which the words list is reduced, the List Reduction, depends upon Wordle's response, which depends upon the answer word. Since we don't know the answer word we can't get the actual List Reduction, but we can find the Expected List Reduction for a word by looking at all possible answer words and averaging over their List Reductions.  

The Wordle Response ($r$) depends on the guessed word and the answer word.
$$
r_{w,a} = \text{Wordle Response (word}_{w}, \text{answer}_a)
$$
The List Reduction (LR) depends on the response, $r$.
$$
\text{LR}(r_{w,a}) = \frac{len(\text{original list}) - len(\text{filtered list}(r_{w,a}))}{len(\text{original list})}
$$
For a given word, $w$, the Expected List Reduction (ELR) is the mean List Reduction over all potential answer words.
$$
\text{ELR}(w) = \frac{1}{len(\text{original list})} \sum_{a} \text{LR}(r_{w,a})
$$
$$
= \frac{1}{len(\text{original list})} \sum_{a} \frac{len(\text{original list}) - len(\text{filtered list}(r_{w,a}))}{len(\text{original list})}
$$
$$
= \frac{1}{len(\text{original list})^2} \Big[len(\text{original list})^2 - \sum_{a} len(\text{filtered list}(r_{w,a}))\Big]
$$
$$
= 1 - \frac{1}{len(\text{original list})^2} \sum_{a} len(\text{filtered list}(r_{w,a}))
$$

# Data Sources
## Kagle Word Frequency Dataset
https://www.kaggle.com/rtatman/english-word-frequency  
Accessed: 03/07/2022  
## Additional Word Frequency Data
https://www.wordfrequency.info/  
Free sample of 'Top 60,000 lemmas + word forms (100,000+ forms)'  
https://www.wordfrequency.info/samples.asp  
Accessed: 03/06/2022  
## List of all Possible Wordle Words
Source: Wordle website (https://www.nytimes.com/games/wordle/index.html) code inspection:  
Inspect -> Application -> vars Ma and Oa  
Accessed: 03/10/22  
## List of Previously Used Wordle Words
https://github.com/eagerterrier/previous-wordle-words/blob/main/index.md  
Accessed: App accesses source when run.  
Thank you Toby Cox (eagerterrier) for maintaining this dataset!  

# Contact Me
Feel free to contact me with any suggestions or discussion:  
colindmiddleton@gmail.com