import dill
import pandas as pd
import numpy as np
import spacy
from multiprocessing import Pool

nlp = spacy.load('en_core_web_lg')

num_partitions = 10 #number of partitions to split dataframe
num_cores = 6 #number of cores on your machine

def chunks(l, n):
    """Yield n chunks from l."""
    size = (len(l) // n) + 1
    for i in range(0, len(l), size):
        yield l[i:i + size]

def parallelize_map(data, func):
    data_split = chunks(data, num_partitions)
    pool = Pool(num_cores)
    mapped_data = sum(pool.map(func, data_split), [])
    pool.close()
    pool.join()
    return mapped_data

def get_vector(data_list):
    vectors = []
    for text in data_list:
        vectors.append(nlp(text).vector)
    return vectors

clean_text_df = pd.read_csv('clean_text.csv').sample(n=10000)
word_embedding_df = clean_text_df
word_embedding_df['vector'] =  parallelize_map(clean_text_df['text'].tolist(), get_vector)
word_embedding_df.to_hdf('data/training_data.hdf', 'id')
