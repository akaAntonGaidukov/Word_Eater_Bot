
# Not in use
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import random

import re

# Bot
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,InputMediaPhoto

# Methods
import config
import db
import translators as ts
import translators.server as tss
API_TOKEN = config.TG_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN,parse_mode="HTML")
dp = Dispatcher(bot)

# Functions 
def translate_ru(wyw_text, translate_mode="All"):

    from_language, to_language = 'en', 'ru'

    if translate_mode == "All":
        g_trans = tss.google(wyw_text, from_language, to_language).lower().split(";")
        y_trans = tss.alibaba(wyw_text, from_language, to_language).lower().split(";")
        b_trans = tss.bing(wyw_text, from_language, to_language).lower().split(";")
        output=[]
        for i in range(len(g_trans)):
            x = set([g_trans[i].strip(),y_trans[i].strip(),b_trans[i].strip()])
            output.append(x)
    
    if translate_mode == "G":
        output = tss.google(wyw_text, from_language, to_language).lower().split(";")

    return output


def dump_to_log(data):
    try:
        file = open("ER.txt", "x",encoding="utf-8")
        file.close()

    except Exception as err:
        print([err,"НУ НЕ МООООГУУУУ ЯЯЯЯЯЯЯ, все ок."])

    with open("ER.txt", "a",encoding="utf-8") as file:
        file.write(data)
        file.close()

def text_handler(text):
    
    if "!g" in text:
        return "good"

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
    
    variants = variants[:4] #can controll number of words in the future
    variants = [i.strip() for i in [*dict(variants).keys()]]
    translated = translate_ru(str(" ; ".join(variants)))

    rw = 1
    ikm = InlineKeyboardMarkup(row_width=rw)


    if len(variants)>0:
        ib1 = InlineKeyboardButton(
            text=" , ".join(translated[0]),
            callback_data=(f"{variants[0]},{LIST_NAME},{special_word}")
        )
        variants.pop(0)
        translated.pop(0)
        ikm.add(ib1)

    if len(variants)>0:
        ib2 = InlineKeyboardButton(
            text=" , ".join(translated[0]),
            callback_data=(f"{variants[0]},{LIST_NAME},{special_word}")
        )
        translated.pop(0)
        variants.pop(0)
        ikm.insert(ib2)

    if len(variants)>0:
        ib3 = InlineKeyboardButton(
            text=" , ".join(translated[0]),
            callback_data=(f"{variants[0]},{LIST_NAME},{special_word}")
        )
        translated.pop(0)
        variants.pop(0)
        ikm.insert(ib3)

    if len(variants)>0:
        ib4 = InlineKeyboardButton(
            text=" , ".join(translated[0]),
            callback_data=(f"{variants[0]},{LIST_NAME},{special_word}")
        )
        translated.pop(0)
        variants.pop(0)
        ikm.insert(ib4)

    return ikm


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    db.new_user(message.from_user.id,message.from_user.full_name)
    await message.answer(
        """Привет я твой помошник в изучении Английского! 
    Ты можешь подгрузить и дополнять списки слов для обучения,
    или для начала попробовать страндртный список при помощи команды /StandartList"""
    )

@dp.message_handler(commands=["help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    await message.answer(
        """*\t\tHELP\t\t*
    /NewList - создать новый список. пример /NewList IELTS
    /AddToList - добавить слова в список. пример /AddToList IELTS word1, word2, word3
    /StartList - начать список, название списка указывается через пробел.
    /StandartList - дает возможность попробовать тестовый список из 5 слов.
    /Stat - показывает статистику
    /er - обратная связь, можете написать о проблеммах в работе бота или предложить функционал
        """
    )

@dp.message_handler(commands=["er"])
async def send_welcome(message: types.Message):
    """
    This handler will save ER message to the queue
    """
    dump_to_log(f"\n{message.text[4:]},{message.from_user.id},{message.from_user.first_name},{message.from_user.last_name}")

    await message.answer("Спасибо за обращение.")


@dp.message_handler(commands=["NewList", "newlist", "nl"])
async def send_welcome(message: types.Message):
    """
    This handler will save ER message to the queue
    """
    msgList = message.text.split(" ", 2)

    db.new_list(message.from_user.id,LIST_NAME=msgList[1], WORD_LIST=msgList[2].split(","))
    await message.answer(f"Создан новый список слов для изучения - <b>{msgList[1]}<b/>.")

@dp.message_handler(commands=["AddtoList", "Add", "add"])
async def send_welcome(message: types.Message):
    """
    This handler will save ER message to the queue
    """
    msgList = message.text.split(" ", 2)

    db.add_to_list(message.from_user.id,LIST_NAME=msgList[1], WORDS=msgList[2].split(","))
    await message.answer(f"Список слов для изучения - {msgList[1]} дополнен.")

@dp.message_handler(commands=["StandartList", "stl"])
async def send_standart_list(message: types.Message):
    """
    This handler will save ER message to the queue
    """
    LIST_NAME="Deafult_list_WaiX4"
    if db.check_avg_weight(message.from_user.id)==1:
        db.add_to_a_shared_list(message.from_user.id,LIST_NAME)
    variants, special_word = db.get_word_list(message.from_user.id,LIST_NAME,SHARED=True)

    
    await bot.send_message(
        chat_id = message.from_user.id,
        text=f"Пожалуйста выберите правильный перевод <b>{special_word}</b>",
        reply_markup=keybord_answ(variants,special_word,LIST_NAME)
        )

@dp.message_handler(commands=["StartList","sl","SL"])
async def give_choice(message: types.Message):
    
    LIST_NAME = message.text.split()[1]
    iterations = 1
    try:
        iterations =  int(message.text.split()[2])
    except Exception as err:
        pass
    for i in range(iterations):
        variants, special_word = db.get_word_list(message.from_user.id,LIST_NAME)

    
        await bot.send_message(
            chat_id = message.from_user.id,
            text=f"Пожалуйста выберите правильный перевод <b>{special_word}</b>",
            reply_markup=keybord_answ(variants,special_word,LIST_NAME)
            )
        

@dp.callback_query_handler()
async def send_result(callback: types.CallbackQuery):
    choice,LIST_NAME,correct = callback.data.split(",")

    if LIST_NAME == "Deafult_list_WaiX4":
        await callback.answer(text=f"ИИИИиии это.....")
        if choice == correct:
            db.word_update(
            TG_CHAT=callback.from_user.id,
            LIST_NAME=LIST_NAME,
            word=correct,
            answer=True,
            SHARED=True
            )
            await bot.send_message(chat_id=callback.from_user.id,text=f"Правильный ответ!")
        else:
            db.word_update(
            TG_CHAT=callback.from_user.id,
            LIST_NAME=LIST_NAME,
            word=correct,
            answer=False,
            SHARED=True
            )
            await bot.send_message(chat_id=callback.from_user.id,text=f"Не правильный ответ!\n Правильный ответ - <b>{str(' , '.join(translate_ru(correct)[0]))}</b>")
        await bot.send_message(
            chat_id = callback.from_user.id,
            text="Еще?",
            reply_markup=Key_Board(["/StandartList","С меня хватит.."])
            )
    else:
        await callback.answer(text=f"ИИИИиии это.....")
        if choice == correct:
            db.word_update(
            TG_CHAT=callback.from_user.id,
            LIST_NAME=LIST_NAME,
            word=correct,
            answer=True
            )
            await bot.send_message(chat_id=callback.from_user.id,text=f"Правильный ответ!")
        else:
            db.word_update(
            TG_CHAT=callback.from_user.id,
            LIST_NAME=LIST_NAME,
            word=correct,
            answer=False)
            await bot.send_message(chat_id=callback.from_user.id,text=f"Не правильный ответ!\n Правильный ответ - <b>{str(' , '.join(translate_ru(correct)[0]))}</b>")
        if db.check_avg_weight(callback.from_user.id) == 1:
            await bot.send_message(
            chat_id = callback.from_user.id,
            text=f"Если хотите повторить нажмите на кнопку в выпадающей клавиатуре",
            reply_markup=Key_Board([f"/StartList {LIST_NAME}","С меня хватит.."])
            )
        else:
            await bot.send_message(
            chat_id = callback.from_user.id,
            text="Еще?",
            reply_markup=Key_Board([f"/StartList {LIST_NAME}","С меня хватит.."])
            )
    ReplyKeyboardRemove()

@dp.message_handler(commands=["visualize","v","Stat"])
async def get_v(messege: types.Message):
    uid = messege.from_user.id
    photo_path,stats = db.get_visulization(uid)
    photo = open(photo_path, 'rb')
    await bot.send_photo(chat_id=uid,photo=photo,caption=f"\t    {stats[0]}\n\nВес слов 0.5 - Хорошее знание списка(при условии что количество повторов >1)\n\nКоличество повторов >1 - Список полностью пройден.")

@dp.message_handler()
async def not_a_comand(message: types.Message):
    """
    This handler will handle all text exept 
    """

    if message.text == "С меня хватит..":
        await message.answer(f"Согласен, хорошая работа! 😁")

    else:
        await message.answer(f'Извини, я не умею поддерживать беседу...')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)