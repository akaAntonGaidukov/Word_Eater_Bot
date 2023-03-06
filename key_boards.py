from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def clear_i():
    return InlineKeyboardMarkup([])

def Key_Board(keys_calls):
    rkm = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)

    if len(keys_calls)>0:
        rb1 = KeyboardButton(text=keys_calls[0])
        keys_calls.pop(0)
        rkm.add(rb1)
    if len(keys_calls)>0:
        rb1 = KeyboardButton(text=keys_calls[0])
        keys_calls.pop(0)
        rkm.add(rb1)

    return rkm


def keybord_answ(variants, special_word,LIST_NAME):

    rw = 1
    ikm = InlineKeyboardMarkup(row_width=rw)
    

    if len(variants)>0:
        correct = 0
        if variants[0][0] == special_word[0]:
            correct = 1
        ib1 = InlineKeyboardButton(
            text=", ".join(variants[0][1]["translation"][:3]),
            callback_data=(f"{correct};{LIST_NAME};{special_word[0]}")
        )
        variants.pop(0)
        ikm.add(ib1)

    if len(variants)>0:
        correct = 0
        if variants[0][0] == special_word[0]:
            correct = 1
        ib2 = InlineKeyboardButton(
            text=", ".join(variants[0][1]["translation"][:3]),
            callback_data=(f"{correct};{LIST_NAME};{special_word[0]}")
        )
        variants.pop(0)
        ikm.add(ib2)

    if len(variants)>0:
        correct = 0
        if variants[0][0] == special_word[0]:
            correct = 1
        ib3 = InlineKeyboardButton(
            text=", ".join(variants[0][1]["translation"][:3]),
            callback_data=(f"{correct};{LIST_NAME};{special_word[0]}")
        )
        variants.pop(0)
        ikm.add(ib3)

    if len(variants)>0:
        correct = 0
        if variants[0][0] == special_word[0]:
            correct = 1
        ib4 = InlineKeyboardButton(
            text=", ".join(variants[0][1]["translation"][:3]),
            callback_data=(f"{correct};{LIST_NAME};{special_word[0]}")
        )
        variants.pop(0)
        ikm.add(ib4)

    return ikm

def key_short_options(opt1={"Buttname":"Buttcallback"},opt2={"Buttname":"Buttcallback"}):
    sikm = InlineKeyboardMarkup(row_width=2)
    
    sib1 = InlineKeyboardButton(text=list(opt1.keys())[0],
                               callback_data=list(opt1.values())[0])
    sib2 = InlineKeyboardButton(text=list(opt2.keys())[0],
                               callback_data=list(opt2.values())[0])
    sikm.add(sib1,sib2)

    return sikm

def main_menu(LIST_NAME="KB",preset=None,
        top_row = {
    "bt1":["Мои списки","LIST"],
    "bt2":["Моя Статистика","STAT"]
        },
        middle_row = {
    "bt1":["Помощь","HELP"],
    "bt2":["Продолжить изучение","CONTINUE"]
        },
        bot_row = {
    "bt1":["Добавить книгу","ADDBOOK"],
    "bt2":["Добавить список","ADDLIST"]
        },
        ):
    
    #PRESETS#

    #list menu
    if preset == "List":
        top_row = {
            "bt1":["Начать список","START_LIST"],
            "bt2":["Отчет по словам","WORD_STAT"]
            }
        middle_row = {
            "bt1":["Удалить список","DELETE_LIST"],
            "bt2":["Совместить списки","MERGE"]
            }
        bot_row = {
            "bt1":["Переименовать","RENAME"],
            "bt2":["НАЗАД","MENU"]
            }
    

    
    mikm = InlineKeyboardMarkup(row_width=2)
    
    mikb1 = InlineKeyboardButton(
        text=top_row["bt1"][0],
        callback_data=top_row["bt1"][1]+f";{LIST_NAME};"+top_row["bt1"][1]
    )

    mikb2 = InlineKeyboardButton(
        text=top_row["bt2"][0],
        callback_data=top_row["bt2"][1]+f";{LIST_NAME};"+top_row["bt2"][1]
    )
    mikm.add(mikb1,mikb2)

    mikb3 = InlineKeyboardButton(
        text=middle_row["bt1"][0],
        callback_data=middle_row["bt1"][1]+f";{LIST_NAME};"+middle_row["bt1"][1]
    )

    mikb4 = InlineKeyboardButton(
        text=middle_row["bt2"][0],
        callback_data=middle_row["bt2"][1]+f";{LIST_NAME};"+middle_row["bt2"][1]
    )
    mikm.add(mikb3,mikb4)

    mikb5 = InlineKeyboardButton(
        text=bot_row["bt1"][0],
        callback_data=bot_row["bt1"][1]+f";{LIST_NAME};"+bot_row["bt1"][1]
    )

    mikb6 = InlineKeyboardButton(
        text=bot_row["bt2"][0],
        callback_data=bot_row["bt2"][1]+f";{LIST_NAME};"+bot_row["bt2"][1]
    )
    mikm.add(mikb5,mikb6)
    

    return mikm

    

