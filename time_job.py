from aiogram import Bot
import db

async def notify_me(bot:Bot):

    notif_list = db.who_notify()
    if len(notif_list) != 0:
        for i in notif_list:
            await bot.send_message(i,text="Got time for English?😎")
            db.update_notif(i)
