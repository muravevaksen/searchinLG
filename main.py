# новости с сайта взяты до 25 января 2021 года

import json
import nltk
import pymorphy2

from elasticsearch import Elasticsearch
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

es = Elasticsearch()
stop_words = stopwords.words("russian")
morph = pymorphy2.MorphAnalyzer()

# считывание файла
with open('ParseLysyeGory\output.json', 'r', encoding='utf-8') as fh:
    data = json.load(fh)

# подсчет количества записей
lines = 0
with open('ParseLysyeGory\output.json') as f:
    for line in f:
        lines = lines + 1

# очень долго обрабатывает все записи, поэтому для тестов взяты 1000 записей вместо всех (lines)
for i in range(1, 1000):
    doc = data[i]
    sent = doc["body"]
    sentence = ' '.join(sent)

    tokens = nltk.word_tokenize(sentence) # разделение на токены

    filtered_tokens = []
    lemmatize = []
    stemming = []
    new_body = ''
    chek_punctuation = True

    # удаление стоп-слов
    for token in tokens:
        if token not in stop_words:
            filtered_tokens.append(token)

    # лемматизация
    for token in filtered_tokens:
        p = morph.parse(token)[0]
        lemmatize.append(p.normal_form)

    # удаление символов
    for word in lemmatize:
        if word != '.' and word != ',' and word != '!' and word != '?' and word != ")" and word != "(" and word != ":"\
                and word != ';' and word != "№" and word != '``' and word != "''" and word != "-":
            new_body = new_body + word + " "

    doc = {'body': [new_body],
           'url': doc['url'],
           'date': doc['date'],
           }

    # создание индекса
    res = es.index(index='searching', id=i, body=doc)

case = int(input("1 - поиск по тексту \n2 - поиск по дате\n"))

if case == 1: # поиск по тексту
    chek = True
    while (chek):
        filtered_tokens = []
        lemmatize = []
        new_data = ""
        inputdata = input("Введите текст для поиска: ")

        tokens = nltk.word_tokenize(inputdata) # деление на токены

        # удаление стоп-слов
        for token in tokens:
            if token not in stop_words:
                filtered_tokens.append(token)

        # лемматизация
        for token in filtered_tokens:
            p = morph.parse(token)[0]
            lemmatize.append(p.normal_form)

        # удаление символов
        for word in lemmatize:
            if word != '.' and word != ',' and word != '!' and word != '?' and word != ")" and word != "(" and word != ":"\
                    and word != ';' and word != "№" and word != '``' and word != "''" and word != "-":
                new_data = new_data + word + " "
        inputdata = new_data

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