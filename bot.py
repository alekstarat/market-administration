import telebot
from CONFIG import *
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time
from datetime import datetime


#maxLen(InlineKeyboardButton) = 69
# айди анасика - 493131120
#69 - 5 - len(j[1]) - len(j[2]) - len(str(j[3])) = X + 5 + len(str(j[0]))
# X = 59 - len(j[1]) - len(j[2]) - len(str(j[3])) = len(str(j[0]))


#icon.run()

def sql_connect():

    con = sqlite3.connect(BASE, check_same_thread=False)
    cur = con.cursor()

    return con, cur

con, cur = sql_connect()
jiji = []

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    global first
    
    first = message.message_id
    print(first)
    bot.clear_step_handler(message)
    for i in range(message.message_id - 10, message.message_id+5):
                try:
                    bot.delete_message(message.chat.id, i)
                except: pass
    if len([i for i in cur.execute(f"SELECT * FROM TelegramUsers WHERE id = {message.chat.id}")]) == 0:
        cur.execute(f"""INSERT INTO TelegramUsers VALUES ({message.chat.id},'{message.from_user.username}', 0, 0, NULL)""")
        con.commit()
        bot.send_message(message.chat.id, f'Вы занесены в базу как @{message.from_user.username}\nВаш уникальный номер - {message.chat.id}')
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text='Забронировать', callback_data='Бронь'))
    if len([i for i in cur.execute(f"SELECT * FROM Reservation WHERE userID = {message.chat.id}")]) > 0:
        markup.add(InlineKeyboardButton(text='Отменить бронь', callback_data='ResCancel'))
    markup.add(InlineKeyboardButton('Посмотреть', callback_data='Просмотр'))
    
    bot.send_message(message.chat.id, '*Привет*\!\ \nХочешь оформить бронь или посмотреть наличие?👇', reply_markup=markup, parse_mode='MarkdownV2')
    

@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    req = call.data.split('_')
 

    global cancel
    cancel = False

    if req[0] == 'restart':
         start(call.message)

    elif req[0] == 'back':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        

    elif req[0] == 'Бронь':
        #bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = InlineKeyboardMarkup()

        for i in cur.execute('SELECT DISTINCT name from Liquids WHERE amount > 0'):
            jiji.append(i[0])
            markup.add(InlineKeyboardButton(text=i[0], callback_data=i[0]))
        markup.add(InlineKeyboardButton(text='НАЗАД', callback_data='restart'))
        bot.send_message(call.message.chat.id, '👇Производители в наличии👇', reply_markup=markup)
        
        
        
    elif req[0] == 'Просмотр':

        jijiCheck = []
        check_markup = InlineKeyboardMarkup()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        for i in cur.execute('SELECT DISTINCT name from Liquids WHERE amount > 0'):
             #print(i)
             jijiCheck.append(i[0])
             check_markup.add(InlineKeyboardButton(text=i[0], callback_data=f'{i[0]} CHECK'))
        check_markup.add(InlineKeyboardButton(text='НАЗАД', callback_data='restart'))
        bot.send_message(call.message.chat.id, '👇чекай👇', reply_markup=check_markup)

        
    elif 'CHECK' in req[0]:

        currName = req[0].split(' ')[0]
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markupCurr = InlineKeyboardMarkup()
        for j in cur.execute(f'SELECT name, type, price FROM Liquids WHERE name = "{currName}"'):
            print('CHECK')
            markupCurr.add(InlineKeyboardButton(text=f'{j[0]} {j[1]} ||  Цена : {str(j[2])}р', callback_data='REDIRECT', url='https://t.me/nasikfluids'))
        markupCurr.add(InlineKeyboardButton(text='НАЗАД', callback_data='Просмотр'))
        
        bot.send_message(call.message.chat.id, f'Вот что есть в наличии от {currName}.\n👇Выбери товар👇', reply_markup=markupCurr)

        
    if req[0] == 'Отмена брони':
        cancel = True


    elif any([req[0] == i for i in jiji]):

        bot.delete_message(call.message.chat.id, call.message.message_id)
        markupCurr = InlineKeyboardMarkup()
        for j in cur.execute(f'SELECT id, name, type, price FROM Liquids WHERE name = "{req[0]}"'):
            markupCurr.add(InlineKeyboardButton(text=f'{j[1]} {j[2]} => {j[3]}p{" "*(59 - len(j[1]) - len(j[2]) - len(str(j[3])) - len(str(j[0])))}ID : {j[0]}', callback_data=int(j[0])))
        bot.send_message(call.message.chat.id, f'Вот что есть в наличии от {req[0]}.\n👇Выбери товар👇', reply_markup=markupCurr)


    elif req[0] == 'ResCancel':
        cancelMarkup2 = InlineKeyboardMarkup()
        reservations = [(i[0],' '.join([j for j in cur.execute(f'SELECT name, type FROM Liquids WHERE id = {i[2]}')][0]), 'до ' + datetime.utcfromtimestamp(i[3]).strftime('%d-%m-%Y')) for i in con.execute(f"SELECT * FROM Reservation WHERE userID = {call.message.chat.id}")]
        for i in reservations:

            cancelMarkup2.add(InlineKeyboardButton(text='  ||  '.join(i[1:]), callback_data=f'CANCEL {i[0]}'))
        cancelMarkup2.add(InlineKeyboardButton(text='НАЗАД', callback_data='restart'))
        bot.send_message(call.message.chat.id, "Выберите нужную бронь", reply_markup=cancelMarkup2)

    elif 'CANCEL' in req[0]:
        resID = int(req[0].split(' ')[-1])
        jijID = [i for i in cur.execute(f'SELECT positionReserved FROM Reservation WHERE operationID = {resID}')][0][0]
        cur.execute(f'UPDATE TelegramUsers SET reservationCount = reservationCount - 1 WHERE id = {call.message.chat.id}')
        cur.execute(f'UPDATE Liquids SET amount = amount + 1 WHERE id = {jijID}')
        cur.execute(f'DELETE FROM Reservation WHERE operationID = {resID}')
        con.commit()
        bot.edit_message_text(text = "Успех✅", chat_id=call.message.chat.id, message_id=call.message.message_id)
        time.sleep(3)
        """ for i in range(call.message.message_id - 10, call.message.message_id + 5):
                    try:
                        bot.delete_message(call.message.chat.id, i)
                    except: pass """

        start(call.message)

    elif req[0].isdigit():
        cancel = False

        cancelMarkup = InlineKeyboardMarkup()
        cancelMarkup.add(InlineKeyboardButton(text='Отменить', callback_data='Отмена брони'))
        t = 5
        bot.send_message(call.message.chat.id, "👍")
        time.sleep(2)
        while not cancel:
            bot.edit_message_text(text = f'Подтверждение брони _*{t}*c_', chat_id=call.message.chat.id, message_id=call.message.message_id + 1, parse_mode='MarkdownV2', reply_markup=cancelMarkup)
            t-=1
            time.sleep(1)
            if t == 0:
                print(list(cur.execute(f"SELECT isBanned FROM TelegramUsers WHERE id = {call.message.chat.id}")))
                if [i for i in cur.execute(f"SELECT isBanned FROM TelegramUsers WHERE id = {call.message.chat.id}")][0][0] != 1:
                    if [i for i in cur.execute(f"SELECT reservationCount FROM TelegramUsers WHERE id = {call.message.chat.id}")][0][0] < 3:
                        
                        cur.execute(f"""INSERT INTO Reservation VALUES (NULL, {call.message.chat.id}, {int(req[0])}, {int(time.time())+604800})""")
                        cur.execute(f"""UPDATE Liquids SET amount = amount - 1 WHERE id = {req[0]}""")
                        cur.execute(f"UPDATE TelegramUsers SET reservationCount = reservationCount + 1 WHERE id = {call.message.chat.id}")
                        con.commit()
                        bot.edit_message_text(text = "Успех✅", chat_id=call.message.chat.id, message_id=call.message.message_id + 1)
                        msg = ' '.join([i for i in cur.execute(f"SELECT name, type FROM Liquids WHERE id = {req[0]}")][0])
                        utime = datetime.utcfromtimestamp([i for i in cur.execute(f'SELECT reservationUntil as a FROM Reservation')][-1][0]).strftime('%d-%m-%Y')
                        #bot.send_message(text=f'БРОНЬ {msg} ДО {utime}', chat_id=493131120)
                        time.sleep(3)
                        start(call.message)
                    else:    
                        bot.send_message(call.message.chat.id, "Нельзя делать больше 3 бронирований одновременно")
                        time.sleep(3)

                else:
                    bot.send_message(call.message.chat.id, "Дружище, ты в бане. Извинись перед Насиком!!!")
                    time.sleep(3)
                """ for i in range(call.message.message_id - 10, call.message.message_id + 5):
                    if i != 0:
                        try:
                            bot.delete_message(call.message.chat.id, i)
                        except: pass """

                start(call.message)

        else:       
            bot.edit_message_text(text = "Отмена❌", chat_id=call.message.chat.id, message_id=call.message.message_id + 1)
            time.sleep(3)
            print("Сработала отмена")

            """ for i in range(call.message.message_id - 10, call.message.message_id + 5):
                
                    try:
                        bot.delete_message(call.message.chat.id, i)
                    except: pass """
            
            start(call.message)
   
    
bot.infinity_polling()
