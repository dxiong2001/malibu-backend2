import numpy as np
import pandas as pd
import nltk
import re
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from scipy import spatial
import networkx as nx
import time

try:
  nltk.data.find('tokenizers/punkt')
  nltk.data.find('corpora/stopwords')
  
except:
  nltk.download('punkt')
  nltk.download('stopwords')


def textrank(text, iterations):

  #Preproces text
  sentences=sent_tokenize(text)
  sentences_clean=[re.sub(r'[^\w\s]','',sentence.lower()) for sentence in sentences]
  sentences_clean=[re.sub(r'\[\]','',sentence) for sentence in sentences_clean]
  stop_words = stopwords.words('english')
  sentence_tokens=[[words for words in sentence.split(' ') if words not in stop_words] for sentence in sentences_clean]

  w2v=Word2Vec(sentence_tokens,vector_size=128,min_count=1,epochs=iterations)
  sentence_embeddings=[[w2v.wv[word][0] for word in words] for words in sentence_tokens]
  max_len=max([len(tokens) for tokens in sentence_tokens])
  sentence_embeddings=[np.pad(embedding,(0,max_len-len(embedding)),'constant') for embedding in sentence_embeddings]

  similarity_matrix = np.zeros([len(sentence_tokens), len(sentence_tokens)])
  for i,row_embedding in enumerate(sentence_embeddings):
      for j,column_embedding in enumerate(sentence_embeddings):
          similarity_matrix[i][j]=1-spatial.distance.cosine(row_embedding,column_embedding)


  nx_graph = nx.from_numpy_array(similarity_matrix)
  scores = nx.pagerank_numpy(nx_graph)
  #print(scores[0])
  top_sentence={sentence:scores[index] for index,sentence in enumerate(sentences)}
  top=dict(sorted(top_sentence.items(), key=lambda x: x[1], reverse=True)[:4])
  
  #print(sentences_clean)
  summ = []
  i=0
  for sent in sentences:
    if sent in top.keys():
        summ.append(re.sub(r'\[\d*\] ','',sent))
        #print(re.sub(r'\[\d*\] ','',sent))
        i=i+1
  return summ

class Summarizer:
  def __init__(self, texttiler):
    self.texttiler = texttiler

  def texttile(self, text):
    tokenized = self.texttiler.tokenize(text)
    return tokenized

  def generate(self, tokenized, iterations, top=1, percentage=0.2):
    length_t = len(tokenized)
    l = []
    print(percentage)
    for t in range(length_t):
      
      section_text = []
      
      ranked_text = textrank(tokenized[t], iterations)
      loop = len(ranked_text)
      #loop = min(top,len(ranked_text))
      num_char_section = len(tokenized[t])
      num_char = 0
      for i in range(loop):
        section_text.append(ranked_text[i].replace("\n\n",""))
        num_char = num_char + len(ranked_text[i])
        if(num_char/num_char_section > percentage):
          break

      l.append(section_text)
      #textrank(tokenized[t])
      #summ[t][0]=textrank(tokenized[t])[0]
      #summ[t][1]=textrank(tokenized[t])#[1]
      
    return l

  def process(self, raw_text):
    processed_text = ""
    for i in raw_text:
      processed_text = processed_text + i.replace("\n", "") + " "

    return processed_text

