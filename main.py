# новости с сайта взяты до 25 января 2021 года

import json
import nltk
import pymorphy2

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

for i in range(1, lines-2):
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
    while (chek):
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
        for hit in res['hits']['hits']:
            print(hit['_source']['url'], hit['_score'])

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