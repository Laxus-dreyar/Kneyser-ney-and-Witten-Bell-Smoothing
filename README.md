# Project to make a Language Model and calculate perplexity
This project aims to build a language model that can use either Witten bell and Kneyser Ney smoothing depending upon the input provided by the user


## Steps to execute the code
python3 language_model.py <nGram> <smoothing_type> <path_corpus>

###### nGram = Value of n for our Language model that considers n-Gram

###### smoothing_type = k for Kneser Ney Smoothing and
###### smoothing_type = w for Witten Bell Smoothing

##### example prompt: 
 			python3 language_model.py 4 k ./corpus.txt
