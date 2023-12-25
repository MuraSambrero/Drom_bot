import telebot
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from search import find_attributes
import time
from headers_and_cookies import headers, cookies
import os

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Включаем логгирование

bot = telebot.TeleBot(os.environ.get('TOKEN'))


@bot.message_handler(commands=['start'])  # Бот принимает сообщение от пользователя
def send_welcome(message):
	bot.reply_to(message, 'Привет! Какую машину вы ищете?\
	\nПросьба писать запрос как в примере:\
	\n"toyota allion"')


@bot.message_handler(content_types=['text'])
def enter_car(message):
	name_car = message.text.lower()  # Добавляем данные введеные пользователем в переменную
	checkname_car(name_car, message)  # Здесь мы проверяем корректно ли введено название
	name_car = name_car.split()  # Делим на отдельные срезы название авто которое ввел пользователь
	bot.reply_to(message, f'Ищем информацию по данному авто. Просьба подождать.')

	# Сразу создаю словарь в котором будут храниться атрибуты которые мы найдем
	all_attributes = {
		'Город': [], 'Год выпуска': [], 'Цена': [], 'Двигатель': [],
		'Мощность': [], 'Пробег': [], 'Поколение': [], 'Коробка передач': [], 'Привод': [],
		'Тип кузова': [], 'Комплектация': [], 'Цвет': [], 'Руль': []
	}
	df = pd.DataFrame(
		data=[],
		columns=list(all_attributes.keys())
	)
	# bool_flag = True
	num_page = 1
	while True:
		print(num_page)
		page = f'page{num_page}'
		request_cars = request_href(num_page, name_car, page, headers, cookies)
		time.sleep(2)
		soup = BeautifulSoup(request_cars.text, 'lxml')
		tags_all_hrefs = soup.findAll('a', class_='css-1oas0dk e1huvdhj1')
		hrefs_for_cars = [tags_all_hrefs[i]['href'] for i in range(len(tags_all_hrefs))]
		if not hrefs_for_cars:
			break
		# Сохраняю запрошенную страницу для себя на просмотр возможных ошибок
		with open(r"C:\Users\MuraSambrero\Desktop\python_developer\My projects\drom_bot\response.txt", "w") as f:
			f.write(request_cars.text)

		# С этого момента заходим на каждую ссылку с авто на странице
		for href_for_car in hrefs_for_cars:
			try:
				attributes = find_attributes(href_for_car, headers, cookies)
				df = df.append(attributes, ignore_index=True)
				# for key, value in attributes.items():  # Добавим все атрибуты в словарь
				# 	all_attributes[key].append(value)
			except:
				print('Выскочила ошибка в цикле for, сон 3 секунды')
		print(len(hrefs_for_cars))
		num_page += 1
		print(num_page)

	# Создадим дата фрейм(таблицу) с нашими атрибутами
	# df = pd.DataFrame(all_attributes)
	# Сохраняем дата фрейм на сервер(ПК)
	df.to_excel(
		rf'C:\Users\MuraSambrero\Desktop\python_developer\My projects\drom_bot\{name_car}.xlsx'
	)
	# Бот отправляет нам созданный файл
	bot.send_document(
		message.chat.id,
		open(rf'C:\Users\MuraSambrero\Desktop\python_developer\My projects\drom_bot\{name_car[0]}.xlsx', 'rb')
	)


def checkname_car(name_car, message):
	if ' ' in name_car:
		for i in name_car:
			if (ord(i) in list(range(97, 123))) or \
				(ord(i) in list(range(49, 58))) or \
				(ord(i) in list(range(1072, 1103))) or \
				(ord(i) == 32):
				continue
			else:
				bot.reply_to(message, 'Вы ввели неверные символы.\
				Пожалуйста попробуйте заново. Введите "/start"')
				break
	else:
		bot.reply_to(message, 'Вы ввели неверные символы или\
				ввели только марку или модель.\
				Пожалуйста попробуйте заново. Нажмите "/start"')


def request_href(num_page, name_car, page, headers=None, cookies=None):
	if num_page == 1:
		return num_page_one(name_car, cookies=cookies, headers=headers)
	elif num_page > 1:
		return num_page_more_than_one(name_car, page, cookies=cookies, headers=headers)


def num_page_one(name_car, request_site=None, cookies=None, headers=None):
	if len(name_car) == 2:
		request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}/', cookies=cookies, headers=headers)
	elif len(name_car) == 3:
		request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}/', cookies=cookies, headers=headers)
	elif len(name_car) == 4:
		request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}_{name_car[3]}/', cookies=cookies, headers=headers)
	return request_site


def num_page_more_than_one(name_car, page, request_site=None, cookies=None, headers=None):
	if len(name_car) == 2:
		request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}/{page}/', cookies=cookies, headers=headers)
	elif len(name_car) == 3:
		if name_car[0].lower() == 'alfa' and name_car[1].lower() == 'romeo':
			request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}_{name_car[1]}/{name_car[2]}/{page}/', cookies=cookies, headers=headers)
		else:
			request_site = requests.get(f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}/{page}/', cookies=cookies, headers=headers)
	elif len(name_car) == 4:
		request_site = requests.get(
			f'https://auto.drom.ru/{name_car[0]}/{name_car[1]}_{name_car[2]}_{name_car[3]}/{page}/', cookies=cookies, headers=headers)
	return request_site


if __name__ == '__main__':
	bot.polling(none_stop=False)
