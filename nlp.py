from epub2txt import epub2txt
import re
import random

from stop_words import get_stop_words
from pymorphy2 import MorphAnalyzer
from razdel import tokenize
from string import punctuation
import spacy

import db

# from a local epub file
filepath = r'.\temp.epub'
model = spacy.load(r".\model")

def get_vocabluary(TG_CHAT,LIST_NAME="Ebook"):

    # Если токен является именем, заменяем его словом "REDACTED" 
    def replace_name_with_placeholder(token):
        if token.ent_iob != 0 and token.ent_type_ == "PERSON":
            return "[REDACTED] "
        elif token.ent_iob != 0 and token.ent_type_ == "GPE":
            return "[RED] "
        elif token.ent_iob != 0 and token.ent_type_ == "ORG":
            return "[REDACT] "
        else:
            return token.text

    # Проверка всех сущностей
    def scrub(text):
        doc = model(text)
        with doc.retokenize() as retokenizer:
            for ent in doc.ents:
                retokenizer.merge(ent)
        tokens = map(replace_name_with_placeholder, doc)
        return " ".join(tokens)

    BOOK = epub2txt(filepath)
    BOOK = scrub(BOOK)

    # загрузка популярных слов
    with open(r".\words.txt","r") as file:
        x = file.readlines()
    STOP_POP = [i.replace("\n","") for i in x]
    SW = set(get_stop_words("en"))
    morpher = MorphAnalyzer()

    def preprocess_txt(text):

        # Удаляет именованные сущности
        text = re.sub(fr'[REDACTED]', '', text)

        # Оставляет только англ символы
        eng = re.compile('[a-zA-Z]+')
        text = ' '.join(eng.findall(text))
            
        # Чистим пунктуацию
        text = re.sub(fr'[{punctuation}]+', ' ', text)
        
        # Убираем всё, не являющееся набором букв, + цифры
        text = ' '.join(word for word in text.split() if word.isalpha())

        # Приводим к общему регистру
        text = text.lower() 

        # Токенизация с помощью библиотеки razdel
        text = [token.text for token in list(tokenize(text))]
        
        # Лемматизация
        text = [morpher.parse(word)[0].normal_form for word in text]
        
        # Убираем стопслова
        text = [word for word in text if word not in SW]

        # Убираем популярные англ слова из топ 3000
        text = [word for word in text if word not in STOP_POP]

        # Убираем слова меньше 3х символов 
        text = [word for word in text if len(word) > 3]
        
        # Возвращаем обработанный текст
        return text

    new_words = preprocess_txt(BOOK)

    ordered_tokens = set()
    result = []
    for word in new_words:
        if word not in ordered_tokens:
            ordered_tokens.add(word)
            result.append(word)
    sorted_text = sorted(result, key=len, reverse=True)

    # Подбор слов от кол-ва процентов
    pro = int(len(sorted_text)*(1/(len(sorted_text)+1000)*100000)/100)
    random_text = list(set(random.sample(sorted_text, k=pro)))

    db.new_list(TG_CHAT,LIST_NAME,random_text)

    return len(random_text)