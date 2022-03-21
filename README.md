# The Wordler
A program to help you play the game [Wordle](https://www.nytimes.com/games/wordle/index.html).  
Visit the website to use this program:  
[https://share.streamlit.io/middlec000/wordler/main/src/main.py](https://share.streamlit.io/middlec000/wordler/main/src/main.py)

# Philosophy
The idea behind this app is that more common words are more likely to be used as the Wordle answer. Though this is not always the case, this app will at least let you quickly narrow down the potential words that could be the answer based on feedback from the Wordle game.

# Data Sources
## Kagle Word Frequency Dataset
https://www.kaggle.com/rtatman/english-word-frequency  
Accessed: 03/07/2022  
## Additional Word Frequency Data
https://www.wordfrequency.info/  
Free sample of 'Top 60,000 lemmas + word forms (100,000+ forms)'  
https://www.wordfrequency.info/samples.asp  
Accessed: 03/06/2022  
## NLTK English Dictionary Word List
https://www.nltk.org/index.html  
Accessed via:  
```nlt.corpus.words.words()```  
NLTK Version: 3.6.5  
## Previously Used Wordle Words List
https://github.com/eagerterrier/previous-wordle-words/blob/main/index.md  
Accessed: When used.  

# TODO
* Figure out initial letter-getting mode.  
  * Try as many vowels as possible.