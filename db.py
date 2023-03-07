from pymongo import MongoClient
import config
import datetime
from collections import ChainMap, Counter
import numpy as np
import random
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from bson import ObjectId
import asyncio
from prettytable import PrettyTable
from PIL import Image
import io
from statistics import mean

import atranslator
#Connnection

con = f"mongodb+srv://bluebear:{config.mongo_pass}@cluster0.arneqvb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(con)
print(client.test)
db = client.get_database("WordEater")
UserTable = db.UserTable
WordListTable = db.WordListTable

#Styles
sns_tg = {'figure.facecolor': '#0e1621',
 'axes.labelcolor': '#f5f5f5',
 'xtick.direction': 'out',
 'ytick.direction': 'out',
 'xtick.color': '#f5f5f5',
 'ytick.color': '#0e1621',
 'axes.axisbelow': True,
 'grid.linestyle': '-',
 'text.color': '#f5f5f5',
 'font.family': ['sans-serif'],
 'font.sans-serif': ['Arial',
  'DejaVu Sans',
  'Liberation Sans',
  'Bitstream Vera Sans',
  'sans-serif'],
 'lines.solid_capstyle': 'round',
 'patch.edgecolor': '#182533',
 'patch.force_edgecolor': False,
 'image.cmap': 'rocket',
 'xtick.top': False,
 'ytick.right': False,
 'axes.grid': False,
 'axes.facecolor': '#182533',
 'axes.edgecolor': '#182533',
 'grid.color': '#182533',
 'axes.spines.left': True,
 'axes.spines.bottom': True,
 'axes.spines.right': True,
 'axes.spines.top': True,
 'xtick.bottom': False,
 'ytick.left': False}

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


def new_list(TG_CHAT,LIST_NAME,WORD_LIST=[],SHARED=False):
    time_now = datetime.datetime.utcnow()
    if SHARED == True:
        shared_list = WordListTable.find_one({"_id" : ObjectId(LIST_NAME)})
        WORD_LIST = [*shared_list["words"]]
        LIST_NAME = shared_list["List_Name"]
        translated = [shared_list["words"][i]["translation"] for i in shared_list["words"]]
    if SHARED == False:   
        translated =atranslator.batch_translate(WORD_LIST)
    Word_lists_table = {
    "List_Name": LIST_NAME,
    "Student" : TG_CHAT,
    "Date_of_creation" : time_now,
    "words" : {WORD_LIST[i].strip() : {'weight':1,'count':0,'translation':translated[i] ,'used_in':[]} for i in range(len(WORD_LIST))},
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
    special_word = random.choice(top_4_words)##########

    return top_4_words, special_word

def word_update(TG_CHAT,LIST_NAME,word,answer,SHARED=False):
    if SHARED == True:
        pass
    else:
        time_now = datetime.datetime.utcnow()

        Wordsinlist = WordListTable.find_one({'Student':TG_CHAT,"List_Name":LIST_NAME})
        Wordsinlist["words"][word]["count"] +=1
        try:
            Wordsinlist["words"][word]["used_in"] = Wordsinlist["words"][word]["used_in"].append(time_now)
        except AttributeError:
            Wordsinlist["words"][word]["used_in"] = [time_now]
        if answer == True:
            Wordsinlist["words"][word]["weight"] = Wordsinlist["words"][word]["weight"] * 0.55
        else:
            Wordsinlist["words"][word]["weight"] = Wordsinlist["words"][word]["weight"] * 1.85
        Wordsinlist["Last_used_in"] = time_now

        WordListTable.update_one({"List_Name":LIST_NAME,"Student":TG_CHAT},{"$set":Wordsinlist})

        table_to_update = UserTable.find_one({'uid': TG_CHAT})
        table_to_update["Date_last_call"] = time_now
        table_to_update["Last_list"] = LIST_NAME
        all_books = list(WordListTable.find({'Student': TG_CHAT}))
        total_words = [i["words"] for i in all_books]
        table_to_update["Words_avg_weight"] = np.mean([i['weight'] for i in dict(ChainMap(*total_words)).values()])

        UserTable.update_one({'uid': TG_CHAT}, {'$set': table_to_update})

def add_to_list(TG_CHAT,LIST_NAME,WORDS):
    time_now = datetime.datetime.utcnow()


    Wordsinlist = WordListTable.find_one({'Student': TG_CHAT,"List_Name":LIST_NAME})

    translated = atranslator.batch_translate(WORDS)
    for k, w in enumerate(WORDS):
        Wordsinlist["words"][w.strip()]={'weight': 1, 'count': 0,'translation':translated[k] ,'used_in':[]}
    
    Wordsinlist["Last_used_in"] = time_now
    WordListTable.update_one({"List_Name":LIST_NAME,"Student":TG_CHAT},{"$set":Wordsinlist})
    
    table_to_update = UserTable.find_one({'uid': TG_CHAT})
    table_to_update["Date_last_call"] = time_now
    all_books = list(WordListTable.find({'Student': TG_CHAT}))
    total_words = [i["words"] for i in all_books]
    table_to_update["Words_total"] = len(list(ChainMap(*total_words).keys()))
    table_to_update["Words_avg_weight"] = np.mean([i['weight'] for i in dict(ChainMap(*total_words)).values()])
    
    UserTable.update_one({'uid': TG_CHAT}, {'$set': table_to_update})

def merge_lists(TG_CHAT,LIST_NAME1,LIST_NAME2,dl=False):
    table1 = WordListTable.find_one({"Student":TG_CHAT,"List_Name":LIST_NAME1})
    words2 = WordListTable.find_one({"Student":TG_CHAT,"List_Name":LIST_NAME2})["words"]

    for w in words2:
        table1["words"][w] = {'weight': words2[w]['weight'],'count': words2[w]['count'],'translation':words2[w]["translation"] ,'used_in':words2[w]['used_in']}
    
    WordListTable.update_one({"Student":TG_CHAT,"List_Name":LIST_NAME1},{'$set':table1})
    if dl == True:
        WordListTable.find_one_and_delete({"Student":TG_CHAT,"List_Name":LIST_NAME2})


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

    if TG_CHAT in shared_list["Student"]:
        pass
    else:
        shared_list["Student"] = list(set(shared_list["Student"]).append(TG_CHAT))
        WordListTable.update_one({"List_Name":LIST_NAME},{"$set":shared_list})

def get_list_names(TG_CHAT,PIC=False):
    all_data = list(WordListTable.find({"Student":TG_CHAT}))
    
    if PIC == True:    
        df = pd.DataFrame()
        for i in all_data:
            df = pd.concat([pd.DataFrame(i),df],axis=0,join="outer")
        df.reset_index(inplace=True)
        df["weight"] = [i["weight"] for i in df.words]
        df["count"] = [1 if i["count"] != 0 else 0 for i in df.words]
        df["used_in"] = [i["used_in"] for i in df.words]
        df["len_word"] = [len(i) for i in df["index"]]
        
        x = PrettyTable()
        w = df["weight"].groupby(df["List_Name"][df["count"]!=0]).agg([np.mean])
        p = df["count"].groupby(df["List_Name"]).mean()
        v = p[p>0.1]*100
        all_lists =df.List_Name.value_counts()
        x.field_names=["Cписок","Пройдено","Оценка","Слов"]
        len_table = 1
        for i, k in enumerate(all_lists.keys()):
            try:   
                x.add_row([k,f"{np.round(v[k],2)}%",f"{np.round(1-w['mean'][k],2)*100}",f"\t{all_lists[k]}".strip()])
            except Exception:
                x.add_row([k,"N/A","N/A",f"\t{all_lists[k]}".strip()])
            len_table+=1

        x.border=False
        
        path_to_save ="lists_short.png"
        sns.set_style(sns_tg)
        dis = sns.displot(data=df, x="weight", hue="List_Name", kind="kde",height=2,aspect=3,)
        dis.set(xlim=(0,1))
        dis.ax.set_xlabel("Оценка")
        dis.ax.set_ylabel("")
        sns.move_legend(dis, "lower left", bbox_to_anchor=(0.05, -0.15-len_table*0.1))
        dis.ax.set_title(x,fontdict={"size":12,"family":"monospace"},x=0.6,y=-1-len_table*0.1)
        dis.savefig(path_to_save)
        return path_to_save, [i["List_Name"] for i in all_data]
    return [i["List_Name"] for i in all_data]
    

def get_last_list(TG_CHAT):

    LL = UserTable.find_one({"uid":TG_CHAT})["Last_list"]
    if LL == None:
        try:
            return UserTable.find_one({"uid":TG_CHAT})["List_of_Lists"][-1]
        except Exception:
            return "У вас нет списков! Добавте список и попробуйте снова."
    return LL
        

def rename_list(TG_CHAT,LIST_NAME,NEW_NAME):

    WordListTable.find_one_and_update({"Student":TG_CHAT,"List_Name":LIST_NAME},{'$set':{"List_Name":NEW_NAME}})
    
    new_list_Names = [i["List_Name"] for i in list(WordListTable.find({'Student':TG_CHAT}))]
    UserTable.find_one_and_update({"uid":TG_CHAT},{'$set':{'List_of_Lists':new_list_Names}})

def list_delete(TG_CHAT,LIST_NAME):

    WordListTable.find_one_and_delete({"Student":TG_CHAT,"List_Name":LIST_NAME})
    new_list_Names = [i["List_Name"] for i in list(WordListTable.find({'Student':TG_CHAT}))]
    UserTable.find_one_and_update({"uid":TG_CHAT},{'$set':{'List_of_Lists':new_list_Names}})

def words_delete(TG_CHAT,LIST_NAME,WORDS_D=[]):
    word_list = WordListTable.find_one({"Student":TG_CHAT, "List_Name":LIST_NAME})

    for i in WORDS_D:
        if i in word_list["words"]:
            word_list["words"].pop(i)
        
    WordListTable.find_one_and_replace({"Student":TG_CHAT, "List_Name":LIST_NAME},word_list)

def is_user(TG_CHAT):
    """Returns bool"""
    return UserTable.find_one({"uid":TG_CHAT})

    
def get_list_id(TG_CHAT,LIST_NAME):
    """Returns _id of a list"""
    return WordListTable.find_one({"Student":TG_CHAT,"List_Name":LIST_NAME})["_id"]


def get_translation(TG_CHAT,LIST_NAME,WORD):
    """Returns translated list cuz TG is 64 - byte gay"""

    return WordListTable.find_one({'Student': TG_CHAT,"List_Name":LIST_NAME})['words'][WORD]["translation"]

def check_params(TG_CHAT):
    table = UserTable.find_one({"uid":TG_CHAT})

    return table["Notifications"], table["Difficulty"]

def change_params(TG_CHAT,notify=None,dif=None):

    if notify != None:

        n =  UserTable.find_one({"uid":TG_CHAT})["Notifications"]
        x = abs(n-1)
        UserTable.update_one({"uid":TG_CHAT},{"$set":{"Notifications":x}})

    if dif != None:

        d = UserTable.find_one({"uid":TG_CHAT})["Difficulty"]
        if d < 3:
            d+=1
        else:
            d=1
        UserTable.update_one({"uid":TG_CHAT},{"$set":{"Difficulty":d}})

def who_notify():
    CHATS = [[i["uid"],i["Last_notify"],i["Notifications"]] for i in [*UserTable.find({})]]
    notify_time_user = []
    for id in CHATS:
        datetimeList =[i["Last_used_in"] for i in [*WordListTable.find({"Student":id[0]})]]
        datetimeList = [datetime.datetime(year=2000,month=1,day=1,hour=i.hour,minute=i.minute).timestamp() for i in datetimeList]
        notify_time = datetime.datetime.fromtimestamp(mean(datetimeList)).time()
        if id[1] != datetime.datetime.utcnow().date() and id[2] == 1:
            notify_time_user.append({id[0]:notify_time})
            

    send_que=[]

    for k in notify_time_user:
        t =[*k.values()][0]

        time_now = datetime.datetime.utcnow()
        time_plus30 = time_now+datetime.timedelta(minutes=30)
        time_minus30 = time_now-datetime.timedelta(minutes=30)
        if time_minus30.time()<t<time_plus30.time():
            print("Yes")

            send_que.append([*k.keys()][0])
        else: print("No")
    print(send_que)

    return send_que

def update_notif(TG_CHAT):
    time_now = datetime.datetime.utcnow()
    UserTable.update_one({"uid":TG_CHAT},{"$set":{"Last_notify":time_now}})

