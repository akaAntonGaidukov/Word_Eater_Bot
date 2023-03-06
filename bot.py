
# Not in use

# Bot
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove,InputMediaPhoto

# Methods
import aspose.words as aw
from PIL import Image
import io

#py
import config
import db
import nlp
import key_boards

API_TOKEN = config.BETA_TG_TOKEN



# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN,parse_mode="HTML")
dp = Dispatcher(bot)

# Functions 


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
    
def get_info(message,split_list=False,no_text=False):
    """id,list_name,text,command"""

    id = message.from_user.id
    
    txt = message.text
    if no_text == True:
        comand,list_name = txt.split(" ",2)
        return id, list_name

    comand,list_name, text= txt.split(" ",2)

    if split_list == True:
        text = text.split(",")
    return id, list_name ,text, comand




# COMAND HANDLERS

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    id = message.from_user.id
    if db.is_user(id) == None:
        db.new_user(id,message.from_user.full_name)
        await message.answer(
        """Привет я твой помошник в изучении Английского! 
    Ты можешь подгрузить и дополнять списки слов для обучения,
    или для начала попробовать страндртный список при помощи команды /StandartList"""
    )
        
    await message.answer("Вы уже являетесь пользователем")

@dp.message_handler(commands=["help"])
async def send_help(message: types.Message,id=None):
    """
    This handler will be called when user sends `/help` command
    """
    txt ="""
/Menu      /m - главное меню.
/NewList  /nl - создать новый список. \nпример /NewList IELTS

/AddToList /add - добавить слова в список. \nпример /AddToList IELTS word1, word2, word3

/MergeLists /ml - совместить два списка. Совмещение происходит в первый список. \nпример /MergeLists IELTS IeltsWriting

/StartList /sl - начать список, название списка указывается через пробел.

/StandartList - дает возможность попробовать тестовый список из 5 слов.

/Stat /s - показывает статистику.

/List /ls - показывает названия ваших сохраненных списков.

/DeleteList /dl - удалить список. \nпример /DeleteList IELTS

/RenameList /rl - переименновать списокю \nпример /RenameList IELTS TOEFL

/ShareList /share - позваляет получить уникальный номер списка. Отправь его другому пользователю чтоб он смог добавить копию списка себе при помощи /nl номер списка.

/er - обратная связь, можете написать о проблеммах в работе бота или предложить функционал

Также вы можете оправлять боту книжки в формате epub. Он достанет оттуда много уникальных слов и добавит их в новый список с названием Ebook (вы также можете добавить свое название в описании под файлом). 
        """
    if id == None:
        await message.answer(txt)
    else:
        await bot.send_message(id,text=txt,reply_markup=key_boards.main_menu())


@dp.message_handler(commands=["Menu","m"])
async def main_menu(message: types.Message):
    """
    This hadler sends Main menu inline keyboard
    """
    await message.answer(text="Главное меню: ",reply_markup=key_boards.main_menu())
    await message.delete()


@dp.message_handler(commands=["er"])
async def send_ER(message: types.Message):
    """
    This handler will save ER message to the queue
    """
    dump_to_log(f"\n{message.text[4:]},{message.from_user.id},{message.from_user.first_name},{message.from_user.last_name}")

    await message.answer("Спасибо за обращение.")


@dp.message_handler(commands=["NewList", "newlist", "nl"])
async def new_list(message: types.Message):
    """
    This handler will help user to create a list
    """
    try:
        id,list_name,text,_ = get_info(message=message,split_list=True)

        db.new_list(id,LIST_NAME=list_name, WORD_LIST=text)
        await message.answer(f"Создан новый список слов для изучения - <b>{list_name}</b>.")
    except ValueError:
        id,list_name = get_info(message=message,no_text=True)
        db.new_list(id,list_name,SHARED=True)
        await bot.send_message(id,f"Добавлен новый список слов для изучения.")

@dp.message_handler(commands=["AddtoList", "Add", "add"])
async def add_list(message: types.Message):
    """
    This handler will help user to add words to list
    """
    id,list_name,text,*_ = get_info(message=message,split_list=True)

    db.add_to_list(id, LIST_NAME=list_name, WORDS=text)
    await message.answer(f"Список слов для изучения - {list_name} дополнен.")

@dp.message_handler(commands=["RemoveWord", "rw"])
async def remove_word(message: types.Message):
    """
    This handler will help user to add words to list
    """
    try:
        id,list_name,text,*_ = get_info(message=message,split_list=True)

        db.words_delete(id, LIST_NAME=list_name, WORDS_D=text)
        await message.answer(f"Из списка слов {list_name} удалены слова <b>{', '.join(text)}</b>.")
    except Exception as err:
        print(err)
        await message.answer(f"У вас точно есть такой список?")

@dp.message_handler(commands=["ShareList","share"])
async def share_list(message: types.Message):
    """
    This handler will help user to share their lists
    """
    id,list_name, = get_info(message=message, no_text=True)

    list_id = db.get_list_id(id,list_name)
    await message.answer(f"Уникальный номер списка - {list_id}\n Чтобы добавить данный список введите команду:\n <code>/nl {list_id}</code>")

@dp.message_handler(commands=["StandartList", "stl"])
async def send_standart_list(message: types.Message):
    """
    This handler will give a trial version of the bot
    """
    LIST_NAME="Deafult_list_WaiX4"
    if db.check_avg_weight(message.from_user.id)==1:
        db.add_to_a_shared_list(message.from_user.id,LIST_NAME)
    variants, special_word = db.get_word_list(message.from_user.id,LIST_NAME,SHARED=True)

    
    await bot.send_message(
        chat_id = message.from_user.id,
        text=f"Пожалуйста выберите правильный перевод <b>{special_word}</b>",
        reply_markup=key_boards.keybord_answ(variants,special_word,LIST_NAME)
        )

@dp.message_handler(commands=["StartList","sl","SL"])
async def give_choice(message: types.Message):
    """
    This handler starts a list for user
    """
    
    id,list_name = get_info(message=message,no_text=True)
    variants, special_word = db.get_word_list(id,list_name)
    try:
        await bot.send_message(
            chat_id = id,
            text=f"Пожалуйста выберите правильный перевод <b>{special_word[0]}</b>",
            reply_markup=key_boards.keybord_answ(variants,special_word,list_name)
            )
    except Exception:
            
            t = f"Произошла ошибка с словами <b>{', '.join(list(variants))}</b>"
            await bot.send_message(
                chat_id = id,
                text=t
                )
            dump_to_log(t)

async def give_choice_restart(id,list_name):
    """
    This handler starts a list for user
    """
    variants, special_word = db.get_word_list(id,list_name)
    try:
        await bot.send_message(
            chat_id = id,
            text=f"Пожалуйста выберите правильный перевод <b>{special_word[0]}</b>",
            reply_markup=key_boards.keybord_answ(variants,special_word,list_name)
            )
    except Exception:
            
            t = f"Произошла ошибка с словами <b>{', '.join(list(variants))}</b>"
            await bot.send_message(
                chat_id = id,
                text=t
                )
            dump_to_log(t)
   


@dp.message_handler(commands=["visualize","v","Stat","s"])
async def get_v(message: types.Message,id=None):
    if id == None:
        uid = message.from_user.id
        photo_path,stats = db.get_visulization(uid)
        photo = open(photo_path, 'rb')
        await bot.send_photo(chat_id=uid,photo=photo,caption=f"\t    {stats[0]}\n\nВес слов 0.5 - Хорошее знание списка(при условии что количество повторов >1)\n\nКоличество повторов >1 - Список полностью пройден.")
    else:
        uid = id
        photo_path,stats = db.get_visulization(uid)
        photo = open(photo_path, 'rb')
        await bot.send_photo(chat_id=uid,photo=photo,caption=f"\t    {stats[0]}\n\nВес слов 0.5 - Хорошее знание списка(при условии что количество повторов >1)\n\nКоличество повторов >1 - Список полностью пройден.",reply_markup=key_boards.main_menu())



@dp.message_handler(commands=["List", "list", "getlist","ls"])
async def get_l(message: types.Message,id=None):
    """
    This handler will sho user all list in users collection
    """
    if id == None:
        
        list_names = db.get_list_names(message.from_user.id)
        await message.answer(f"Списки слов для изучения - {', '.join(list_names)}.")
    else:
        path,list_names = db.get_list_names(id,PIC=True)
        photo = open(path, 'rb')
        await bot.send_photo(id,photo=photo,caption="Ваши списки",reply_markup=key_boards.main_menu(preset="List"))        

@dp.message_handler(commands=["MergeLists", "ml"])
async def rename_l(message: types.Message):
    """
    This handler will save ER message to the queue
    """
    comand, name1, name2 = message.text.split()
    id=message.from_user.id

    list_names = db.get_list_names(id)
    if name1 and name2 in list_names:
        db.merge_lists(id,name1,name2)
        await message.answer(f"Списки слов {name2} добавлен в список {name1}.")
    else: 
        await bot.send_message(id,f"У вас нет такого списка, проверте правильность написания.\nВаши списки: {','.join(list_names)}")


@dp.message_handler(commands=["RenameList", "rl"])
async def rename_l(message: types.Message):
    """
    This handler will save ER message to the queue
    """
    comand, name, new_name = message.text.split()
    id=message.from_user.id
    list_names = db.get_list_names(id)
    if name in list_names:
        db.rename_list(id,name,new_name)
        await message.answer(f"Списки слов {name} переименнован в {new_name}.")
    else: 
        await message.answer(f"У вас нет такого списка, проверте правильность написания.\nВаши списки: {','.join(list_names)}")

@dp.message_handler(commands=["RemoveList","DeleteList", "dl"])
async def remove_list(message: types.Message):
    """
    This handler delets selected list
    """
    id = message.from_user.id
    comand, name = message.text.split()
    list_names = db.get_list_names(id)
    if name in list_names:
        db.list_delete(id,name)
        await message.answer(f"Список слов {name} удален.")
    else: 
        await message.answer(f"У вас нет такого списка, проверте правильность написания.\nВаши списки: {','.join(list_names)}")


@dp.callback_query_handler()
async def send_result(callback: types.CallbackQuery):
    choice,LIST_NAME,correct = callback.data.split(";")
    id = callback.from_user.id

    if choice in ["Restart_List"]:
        await callback.message.delete()
        await give_choice_restart(id,LIST_NAME)
        await callback.answer()
        
    elif choice in ["STOP"]:
        await callback.message.delete()
        await bot.send_message(id,"Согласен! Отличная работа!😁",reply_markup=key_boards.main_menu())
        await callback.answer()

    elif choice in ["LIST"]:
        await callback.message.delete()
        await get_l(message= None, id=id)
        await callback.answer()
    
    elif choice in ["STAT"]:
        await callback.message.delete()
        await get_v(message= None, id=id)
        await callback.answer()

    elif choice in ["HELP"]:
        await callback.message.delete()
        await send_help(message= None, id=id)
        await callback.answer()

    elif choice in ["ADDBOOK"]:
        await callback.message.delete()
        await bot.send_message(id,"Вы можете добавить книгу в формате .epub отправив ее боту,\nкнижка сохранится с стандартным названием Ebook,обработка займет от 1-10 минут.\nЧтобы сохранить книжку под другим именем впишите его в описании файла при отправке.",reply_markup=key_boards.main_menu())
        await callback.answer()

    elif choice in ["ADDLIST"]:
        await callback.message.delete()
        await bot.send_message(id,"Вы можете добавить свой список для изучения при помощи команды /nl\nПример можете скопировать как шаблон <code>/nl NewList word1,word2,word and word </code>\nЧтобы начать список необходимо хотябы 8 слов в списке",reply_markup=key_boards.main_menu())
        await callback.answer()

    elif choice in ["CONTINUE","START_LIST"]:
        await callback.message.delete()
        list_name =  db.get_last_list(id)
        await bot.send_message(id,f"Продолжаем список - {list_name}")
        await give_choice_restart(id,list_name)

    #LIST

    elif choice in ["WORD_STAT"]:
        await callback.message.delete()
        await bot.send_message(id,"Эта кнопка еще не готова, sorry.. 💩",reply_markup=key_boards.main_menu(preset="List"))
        await callback.answer()

    elif choice in ["DELETE_LIST"]:
        await callback.message.delete()
        await bot.send_message(id,"Вы можете удалить свой список для изучения при помощи команды /dl\nПример можете скопировать как шаблон <code>/dl NewList</code>",reply_markup=key_boards.main_menu(preset="List"))
        await callback.answer()

    elif choice in ["MERGE"]:
        await callback.message.delete()
        await bot.send_message(id,"Вы можете совместить свои списоки для изучения при помощи команды /ml\nПример можете скопировать как шаблон <code>/ml BigList SmallList</code>",reply_markup=key_boards.main_menu(preset="List"))
        await callback.answer()
    
    elif choice in ["RENAME"]:
        await callback.message.delete()
        await bot.send_message(id,"Вы можете переименовать свои списоки для изучения при помощи команды /rl\nПример можете скопировать как шаблон <code>/rl Ebook LOTR</code>",reply_markup=key_boards.main_menu(preset="List"))
        await callback.answer()

    elif choice in ["MENU"]:
        await callback.message.delete()
        await bot.send_message(id,text="Главное меню: ",reply_markup=key_boards.main_menu())
        await callback.answer()   

    
    else:
        
        
        if LIST_NAME == "Deafult_list_WaiX4":
            await callback.answer(text=f"ИИИИиии это.....")
            if choice == "1":
                db.word_update(
                TG_CHAT=id,
                LIST_NAME=LIST_NAME,
                word=correct,
                answer=True,
                SHARED=True
                )
                await bot.send_message(chat_id=id,text=f"Правильный ответ!")
            else:
                db.word_update(
                TG_CHAT=id,
                LIST_NAME=LIST_NAME,
                word=correct,
                answer=False,
                SHARED=True
                )
                await bot.send_message(chat_id=id,text=f"Не правильный ответ!\n Правильный ответ - <b>{', '.join(db.get_translation(id,LIST_NAME,correct))}</b>")
            await bot.send_message(
                chat_id = id,
                text="Еще?",
                reply_markup=key_boards.Key_Board(["/StandartList","С меня хватит.."])
                )
        else:
            await callback.answer(text=f"ИИИИиии это.....")
            if choice == "1":
                db.word_update(
                TG_CHAT=id,
                LIST_NAME=LIST_NAME,
                word=correct,
                answer=True
                )
                await bot.send_message(chat_id=id,text=f"Правильный ответ!")
            else:
                db.word_update(
                TG_CHAT=id,
                LIST_NAME=LIST_NAME,
                word=correct,
                answer=False)
                await bot.send_message(chat_id=id,text=f"Не правильный ответ!\n Правильный ответ - <b>{', '.join(db.get_translation(id,LIST_NAME,correct))}</b>")
            if db.check_avg_weight(callback.from_user.id) == 1:
                await bot.send_message(
                chat_id = id,
                text=f"Если хотите повторить нажмите на кнопку в выпадающей клавиатуре",
                reply_markup=key_boards.key_short_options({"Ещё":f"Restart_List;{LIST_NAME};Restart_List"},{"С меня хватит..":"STOP;STOP;STOP"})
                )
            else:
                await bot.send_message(
                chat_id = id,
                text="Еще?",
                reply_markup=key_boards.key_short_options({"Да!":f"Restart_List;{LIST_NAME};Restart_List"},{"С меня хватит..":"STOP;STOP;STOP"})
                )
            await callback.answer()


# CONTENT HANDLER

@dp.message_handler(content_types=['photo', 'document'])
async def photo_or_doc_handler(message: types.Message):
    file_in_io = io.BytesIO()
    id=message.from_user.id

    if message.content_type == 'photo':
        await bot.send_message(chat_id=id,text="Спасибо за фото конечно, но я не знаю что с ним делать.. Если у вас есть идеи пишите в /er")
        await message.photo[-1].download(destination_file=file_in_io)
        img_exp = Image.open(file_in_io)
        img_exp.save('my.png')

    elif message.content_type == 'document':

        if message.document.file_name[-4:] == "epub":
            await bot.send_message(id,"Ваша книжка обрабатывается, это займет около 10 минут.")
            thumb = message.caption
            print(thumb)
            await message.document.download(destination_file="temp.epub")
            if thumb == None:
                wordcount = nlp.get_vocabluary(id)
            else:
                thumb.replace(" ",".")
                wordcount = nlp.get_vocabluary(id,thumb)

            await bot.send_message(id,f"Ваша книжка обработана и сохранена под именем <code>{thumb}</code>, добавленно {wordcount} слов.")

        else:
            await bot.send_message(id,"В настоящий момент поддерживаются тоько файлы с расширением epub.")
    

# NO COMAND HENDLER      
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