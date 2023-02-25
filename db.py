from pymongo import MongoClient
import config
import datetime
from collections import ChainMap, Counter
import numpy as np
import random
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
#Connnection

con = f"mongodb+srv://bluebear:{config.mongo_pass}@cluster0.arneqvb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(con)
print(client.test)
db = client.get_database("WordEater")
UserTable = db.UserTable
WordListTable = db.WordListTable


def new_user(TG_CHAT_ID,TG_NAME):
    time_now = datetime.datetime.utcnow()

    user_cell = {
    "uid" : TG_CHAT_ID,
    "Name" : TG_NAME,
    "Date_of_registration" : time_now,
    "Date_last_call" : time_now,
    "List_of_Lists" : [],
    "Words_total" : 0,
    "Words_avg_weight" : 1.0
}
    UserTable.insert_one(user_cell)


def new_list(TG_CHAT,LIST_NAME,WORD_LIST=[]):
    time_now = datetime.datetime.utcnow()

    Word_lists_table = {
    "List_Name": LIST_NAME,
    "Student" : TG_CHAT,
    "Date_of_creation" : time_now,
    "words" : {WORD_LIST[i] : {'weight':1,'count':0} for i in range(len(WORD_LIST))},
    "Last_used_in" : time_now
}
    WordListTable.insert_one(Word_lists_table)

    table_to_update = UserTable.find_one({'uid': TG_CHAT})

    table_to_update["Date_last_call"] = time_now
    all_books = list(WordListTable.find({'Student': TG_CHAT}))
    table_to_update["List_of_Lists"].append(LIST_NAME)
    total_words = [i["words"] for i in all_books]
    table_to_update["Words_total"] = len(list(ChainMap(*total_words).keys()))
    table_to_update["Words_avg_weight"] = np.median([i['weight'] for i in dict(ChainMap(*total_words)).values()])

    UserTable.update_one({'uid': TG_CHAT}, {'$set': table_to_update})


def get_word_list(TG_CHAT,LIST_NAME,SHARED=False):
    if SHARED == True:
        Wordsinlist = WordListTable.find_one({"List_Name":LIST_NAME})['words']
        top_4_words = random.choices(list(Wordsinlist.items()),k=4)
        special_word = random.choice(top_4_words)[0]
        return top_4_words, special_word

    else:
        Wordsinlist = WordListTable.find_one({'Student': TG_CHAT,"List_Name":LIST_NAME})['words']
    top_8_words = sorted(Wordsinlist.items(), key=lambda x:x[1]['weight'],reverse=True)[:8]  
    random.shuffle(top_8_words)
    top_4_words = top_8_words[:4]
    special_word = random.choice(top_4_words)[0]

    return top_4_words, special_word

def word_update(TG_CHAT,LIST_NAME,word,answer,SHARED=False):
    if SHARED == True:
        pass
    else:
        time_now = datetime.datetime.utcnow()

        Wordsinlist = WordListTable.find_one({'Student':TG_CHAT,"List_Name":LIST_NAME})
        Wordsinlist["words"][word]["count"] +=1
        if answer == True:
            Wordsinlist["words"][word]["weight"] = Wordsinlist["words"][word]["weight"] * 0.55
        else:
            Wordsinlist["words"][word]["weight"] = Wordsinlist["words"][word]["weight"] * 1.85
        Wordsinlist["Last_used_in"] = time_now

        WordListTable.update_one({"List_Name":LIST_NAME,"Student":TG_CHAT},{"$set":Wordsinlist})

        table_to_update = UserTable.find_one({'uid': TG_CHAT})
        table_to_update["Date_last_call"] = time_now
        all_books = list(WordListTable.find({'Student': TG_CHAT}))
        total_words = [i["words"] for i in all_books]
        table_to_update["Words_avg_weight"] = np.mean([i['weight'] for i in dict(ChainMap(*total_words)).values()])

        UserTable.update_one({'uid': TG_CHAT}, {'$set': table_to_update})

def add_to_list(TG_CHAT,LIST_NAME,WORDS):
    time_now = datetime.datetime.utcnow()


    Wordsinlist = WordListTable.find_one({'Student': TG_CHAT,"List_Name":LIST_NAME})
    
    for i in WORDS:
        Wordsinlist["words"][i]={'weight': 1, 'count': 0}
    
    Wordsinlist["Last_used_in"] = time_now
    WordListTable.update_one({"List_Name":LIST_NAME,"Student":TG_CHAT},{"$set":Wordsinlist})
    
    table_to_update = UserTable.find_one({'uid': TG_CHAT})
    table_to_update["Date_last_call"] = time_now
    all_books = list(WordListTable.find({'Student': TG_CHAT}))
    total_words = [i["words"] for i in all_books]
    table_to_update["Words_total"] = len(list(ChainMap(*total_words).keys()))
    table_to_update["Words_avg_weight"] = np.mean([i['weight'] for i in dict(ChainMap(*total_words)).values()])
    
    UserTable.update_one({'uid': TG_CHAT}, {'$set': table_to_update})

def get_visulization(TG_CHAT):
    all_data = list(WordListTable.find({"Student":TG_CHAT}))
    df = pd.DataFrame()
    for i in all_data:
        df = pd.concat([pd.DataFrame(i),df],axis=0,join="outer")
    df.reset_index(inplace=True)    
    df["weight"] = [i["weight"] for i in df.words]
    df["count"] = [i["count"] for i in df.words]

    g = sns.jointplot(
    data=df[["weight","count","List_Name"]],
    x="weight", y="count", hue="List_Name",
    kind="kde",xlim=[0,2]
    )
    path_to_pic = "stat_v.png"
    plt.savefig(path_to_pic)
    statistics = df[['List_Name','weight','count']].groupby(df["List_Name"]).agg([np.mean]).rename(columns ={"weight":"Вес слов","count":"Количество повторов"});
    return path_to_pic,[statistics]

def check_avg_weight(TG_CHAT):
    Avg_weight = UserTable.find_one({"uid":TG_CHAT})["Words_avg_weight"]

    return Avg_weight

def add_to_a_shared_list(TG_CHAT,LIST_NAME):
    shared_list = WordListTable.find_one({"List_Name":LIST_NAME})

    shared_list["Student"].append(TG_CHAT)

    WordListTable.update_one({"List_Name":LIST_NAME},{"$set":shared_list})
