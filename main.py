# новости с сайта взяты до 25 января 2021 года

import json
import math

import nltk
import pymorphy2

import numpy as np

from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from wiki_ru_wordnet import WikiWordnet

nltk.download('punkt')
nltk.download('stopwords')
nltk.download("wordnet")

es = Elasticsearch()
wikiwordnet = WikiWordnet()
stop_words = stopwords.words("russian")
morph = pymorphy2.MorphAnalyzer()
punctuation = [".", ",", "!", "?", ")", "(", ":", ";", "№", "``", "''", "-", " ", "..."]

# считывание файла
with open('ParseLysyeGory\output.json', 'r', encoding='utf-8') as fh:
    data = json.load(fh)

# подсчет количества записей
lines = 0
with open('ParseLysyeGory\output.json') as f:
    for line in f:
        lines = lines + 1

for i in range(1, 1000):
    doc = data[i]
    sent = doc["body"]
    sentence = ' '.join(sent)
    new_body = ''

    tokens = nltk.word_tokenize(sentence) # разделение на токены

    # удаление стоп-слов и знаков препинания, лемматизация
    for token in tokens:
        if (token not in stop_words) and (token not in punctuation):
            p = morph.parse(token)[0]
            new_body = new_body + p.normal_form + " "

    # создание индекса
    res = es.index(index='searching', id=i, body={'body': [new_body],
           'url': doc['url'],
           'date': doc['date'],
           })

case = int(input("1 - поиск по тексту \n2 - поиск по дате\n"))

if case == 1: # поиск по тексту
    chek = True
    while chek:
        new_data = []
        str = ""

        inputdata = input("Введите текст для поиска: ")
        tokens = nltk.word_tokenize(inputdata) # деление на токены

        # удаление стоп-слов и символов, лемматизация
        for token in tokens:
            if token not in stop_words and token not in punctuation:
                p = morph.parse(token)[0]
                new_data.append(p.normal_form)

        # синонимы
        for word in new_data:
            synsets = wikiwordnet.get_synsets(word)
            if synsets:
                synset1 = synsets[0]
                for w in synset1.get_words():
                    str = str + w.lemma() + " "
            else:
                str = str + word + " "

        inputdata = str

        res = es.search(index='searching', body={'query': {'match': {"body": inputdata}}}) # поиск

        print('Результаты:')
        count = 1
        for hit in res['hits']['hits']:
            print(hit['_source']['url'], hit['_score'])
            count += 1

        # оценка ранжирования
        grdcase = int(input("Посчитать NDCG метрику? \nда - 1 \nнет - любая другая цифра\n"))
        doci = np.zeros(count)
        docreli = np.zeros(count)
        DCG = np.zeros(count)
        IDCG = np.zeros(count)
        sumDCG = 0
        sumIDCG = 0
        if grdcase == 1:
            print("Оцените результаты \n0 - не релевантен \n1 - более менее релевантен \n2 - полностью релевантен\n")
            for j in range(1, count):
                doci[j] = j
                print(j, ' документ:')
                docreli[j] = int(input())
                DCG[j] = docreli[j]/math.log(doci[j]+1, 2)
                sumDCG += DCG[j]
            print("DCG = ", sumDCG)
            docreli2 = sorted(docreli)
            docreli2.reverse()
            for j in range(1, count):
                IDCG[j] = docreli2[j-1] / math.log(doci[j] + 1, 2)
                sumIDCG += IDCG[j]
            print("IDCG = ", sumIDCG)
            print("NDCG = ", sumDCG/sumIDCG)
        else:
            break

elif case == 2: # поиск по дате
    chek = True
    while (chek):
        inputdate = input('Введите дату в формате dd.mm.yyyy: ')

        res = es.search(index='searching', body={'query': {'match': {"date": inputdate}}}) # поиск

        print('Результаты:')
        for hit in res['hits']['hits']:
            print(hit['_source']['date'], hit['_source']['url'])

else:
    pass