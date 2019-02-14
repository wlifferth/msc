import pandas as pd
import requests
from bs4 import BeautifulSoup
from sys import argv

if (len(argv) < 2):
    print('Usage: python {} filename'.format(argv[0]))
    quit()

raw_df_medium = pd.read_csv('data/medium_urls.csv')

urls = raw_df_medium[['url']]

print(len(urls))

sample_num = int(argv[1])
urls = urls.sample(n=sample_num)['url']
count = 0

outfile = open('data/medium_samples.csv', 'a+')
error_log = open('logs/download_medium.logs', 'a+')

for url in urls:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for p in soup.find_all('p'):
            words = p.text.split()
            for i in range(len(words) // 100):
                sample = ' '.join(words[(i*100):((i+1)*100)])
                count += 1
                outfile.write(sample + '\n')
        print("{} total samples".format(count), " "*20, end='\r')
    except Exception as e:
        error_log.write(str(e))

print("Run finished. {} total samples downloaded and added to {}".format(count, outfile.name), " "*20)
