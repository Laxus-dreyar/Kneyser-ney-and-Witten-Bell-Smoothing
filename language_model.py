import numpy as np
import re
import math
import time
import random
from sys import argv

class mytokenizer:
    
    def __init__(self):
        self.hashtags = re.compile(r"#\w+")
        self.mentions = re.compile(r"@\w+")
        self.urls = re.compile(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})")
        self.punct = re.compile(r"[\w|']+|[^\w\s]+")
        
    def remove_punct(self,sent):
        tokens = re.findall(self.punct,sent)
        new_sent = ""
        for w in tokens:
            w1 = w
            if w[0] == '\'':
                w1 = w[1:]
            
            match = re.match(r"\A[^\w\s]",w1)
            if not match:
                if '\'' in w:
                    new_sent = new_sent + " ".join(self.apostofy(w)) + " "
                else:
                    new_sent = new_sent + w + " "
                continue
            
            new_word = w[0]
            for i in range(1,len(w)):
                if w[i] == w[i-1]:
                    continue
                new_word = new_word + w[i]
            
            new_sent = new_sent + new_word + " "
        
        return new_sent.split()
            
    def apostofy(self,sent):
        toks = []
        i = 0
        cur_word = ""
        while(i < len(sent)):
            if sent[i] != '\'':
                cur_word = cur_word + sent[i]
                i = i+1
            else:
                toks.append(cur_word)
                cur_word = '\''
                while(i < len(sent) and sent[i] == '\''):
                    i = i+1
        
        if cur_word != "" and cur_word != '\'':
            toks.append(cur_word)
        
        return toks
    
    def tokenize(self,sent):
        sent = sent.strip()
        sent = sent.lower()
        sent = re.sub(self.hashtags,' <HASHTAG> ',sent)
        sent = re.sub(self.mentions,' <MENTION> ',sent)
        sent = re.sub(self.urls,' <URL> ',sent)
        tokens = sent.split()
        
        new_toks = []
        for i in tokens:
            if i == "<URL>" or i == "<MENTION>" or i == "<HASHTAG>":
                new_toks.append(i)
            else:
                new_toks.extend(self.remove_punct(i))
        
        return new_toks

def create_nGram(toks,n):

    if n == 0:
        return {}

    nGram = {}
    #bigram
    nGram[n] = {}

    for i in range(len(toks)-(n-1)):
        w = tuple(toks[i:i+n])
        if w not in nGram[n]:
            nGram[n][w] = 1
        else:
            nGram[n][w] = 1 + nGram[n][w]
    
    prev = create_nGram(toks, n-1)
    nGram.update(prev)
    return nGram

def searchDict(phrase,nGram):
    if len(phrase) == 0:
        s = 0
        for i in nGram[1]:
            s = s + nGram[1][i]
        return s
    if phrase in nGram[len(phrase)]:
        return nGram[len(phrase)][phrase]
    else:
        return 0

def kneser(phrase, maximumLen , nGram):
    d = 0.75
    prevPhrase = phrase[:-1]
    prevval = searchDict(prevPhrase,nGram)
    if prevval == 0:
        lamda = random.uniform(0,1)
        term = random.uniform(0.00001,0.0001)
    else:
        if len(phrase) == maximumLen:
            term = searchDict(phrase,nGram)-d
            if term <=0:
                term = 0
            
            term = term / prevval
        else:
            term = 0
            for token in nGram[len(phrase) + 1]:
                if token[1:] == phrase:
                    term = term + 1
            
            term = term - d
            if term <= 0:
                term = 0
            
            term = term / prevval

        lamda = 0
        for token in nGram[len(phrase)]:
            if token[:-1] == prevPhrase:
                lamda = lamda + 1
        
        lamda = lamda * d / prevval

    if len(phrase) == 1:
       return term
    else:
        return term + lamda * kneser(prevPhrase, maximumLen,nGram)

def wittenSecond(phrase,nGram):
    match = 0
    for token in nGram[len(phrase)+1]:
        if(token[:-1] == phrase):
            match = match + 1
            
    k = match + searchDict(phrase,nGram)
    if(k == 0):
        return random.uniform(0.00001,0.0001)
    else:
        match = float(match)
        match = match / k
        return match

def witten(phrase,nGram):
    prevPhrase = phrase[:-1]
    prevval = searchDict(prevPhrase,nGram)
    curval = searchDict(phrase,nGram)
    if len(phrase) == 1:
        curval = curval / searchDict((),nGram)
        return curval
    
    prev = (wittenSecond(prevPhrase,nGram) * witten(prevPhrase,nGram))
    if(prevval != 0):
        curval = curval / prevval
        curval = curval * (1 - wittenSecond(prevPhrase,nGram))
    else:
        curval = random.uniform(0.00001, 0.0001)
    
    return curval + prev

def perplexity(inp, nGram, n=4,smoothType='k'):

    cl = mytokenizer()
    inp_toks = cl.tokenize(inp)
    sent_prob = 0
    for i in range(len(inp_toks)-(n-1)):
        phrase = tuple(inp_toks[i:i+n])
        if smoothType == 'k':
            sent_prob = sent_prob + math.log(kneser(phrase, len(phrase),nGram) + 0.0000001)
        elif smoothType == 'w':
            sent_prob = sent_prob + math.log(witten(phrase, nGram) + 0.0000001)
    
    word_count = len(inp_toks)
    perplexity = -(sent_prob/word_count)

    print(np.exp(sent_prob))
    return perplexity

n = int(argv[1])
smoothType = argv[2]
path = argv[3]

f = open(path,'r')
cl = mytokenizer()
tokens = cl.tokenize(f.read())
# print("tokenization done")
f.close()


nGram = create_nGram(tokens, n)

# print("nGram done")

inp = input("Input sentence: ")

a = perplexity(inp, nGram,n,smoothType)
print(a)