import pandas as pd
import requests
from bs4 import BeautifulSoup
from sys import argv
import wikipedia as wiki
import warnings
import time

if (len(argv) < 2):
    print('Usage: python {} filename'.format(argv[0]))
    quit()

target_count = int(argv[1])
outfile = open('data/wikipedia_samples.csv', 'a+')
error_log = open('logs/download_wikipedia.logs', 'a+')

def prepare_samples(text):
    samples = []
    target_length = 100
    words = text.split()
    for i in range((len(words) // target_length) - 1):
        samples.append(' '.join(words[(i*target_length):((i+1)*target_length)]))
    return samples

errors = 0
successes = 0
def print_status(errors, successes, msg="prev"):
    print("errors: {}\tsuccesses: {}\t\t[finished {}]".format(errors, successes, msg), " "*30, end='')
    print('\r', end='')
    time.sleep(1)

with warnings.catch_warnings():
    while successes < target_count:
        warnings.simplefilter("ignore")
        for term in wiki.random():
            results = wiki.search(term, results=3)
            for result in results:
                try:
                    text = wiki.page(result).content
                    for sample in prepare_samples(text):
                        outfile.write(sample + '\n')
                    successes += 1
                    print_status(errors, successes, result)
                except wiki.exceptions.DisambiguationError:
                    errors += 1
                    print_status(errors, successes, result)

print("Run finished. {} total samples downloaded and added to {}".format(count, outfile.name), " "*20)
