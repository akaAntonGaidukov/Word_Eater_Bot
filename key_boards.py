from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import translators as ts
import translators.server as tss

def translate_ru(wyw_text, translate_mode="FAST",k=4):
    

    from_language, to_language = 'en', 'ru'
    if translate_mode == "FAST":
        trans = tss.google(wyw_text, from_language, to_language,is_detail_result = True)
        output = []

        for n in range(k):
            da = []
            translations =  trans["data"][1][0][0][5][n][4]
            for i in translations:
                for x in i:
                    if type(x) == str:
                        da.append(x.replace(";","").strip().lower())
            output.append(set(da))

        output

    if translate_mode == "All":
        g_trans = tss.google(wyw_text, from_language, to_language).lower().split(";")
        y_trans = tss.alibaba(wyw_text, from_language, to_language).lower().split(";")
        b_trans = tss.bing(wyw_text, from_language, to_language).lower().split(";")
        output=[]
        for i in range(len(g_trans)):
            x = set([g_trans[i].strip(),y_trans[i].strip(),b_trans[i].strip()])
            output.append(x)
    
    if translate_mode == "G":
        output = tss.google(wyw_text, from_language, to_language).lower()
        return output
    return output


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