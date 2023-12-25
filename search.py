import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


def find_attributes(href_for_car, cookies=None, headers=None) -> dict:
	request_one_car = requests.get(f'{href_for_car}', cookies=cookies, headers=headers)
	time.sleep(4)
	soup = BeautifulSoup(request_one_car.text, 'lxml')
	value_attributes = dict()

	city_and_year = soup.find('h1', class_='css-1tjirrw e18vbajn0').get_text()
	if city_and_year is not None:
		value_attributes["Город"] = f'В {(city_and_year.split())[-1]}'
		value_attributes["Год выпуска"] = (city_and_year.split())[-4]
		value_attributes["Цена"] = soup.find('div', class_='css-eazmxc e162wx9x0').get_text().replace('\xa0', ' ')

	for elem in soup.findAll('th', class_='css-16lvhul ezjvm5n1'):
		if elem.string == 'Двигатель':
			engine_capacity = soup.find('span', class_='css-1jygg09 e162wx9x0').get_text()
			value_attributes[elem.string] = engine_capacity
		elif elem.string == 'Мощность':
			power = soup.find('span', class_='css-9g0qum e162wx9x0').get_text().replace('\xa0', ' ')
			value_attributes[elem.string] = str(power).replace(', налог', '')
		elif elem.string == 'Пробег':
			mileage = soup.find('span', class_='css-1osyw3j ei6iaw00').get_text().replace('\xa0', ' ')
			value_attributes[elem.string] = mileage
		elif elem.string == 'Поколение':
			generation = soup.find('a', class_='e1oy5ngb0 css-gfsg9y e104a11t0').get_text()
			value_attributes[elem.string] = generation

	all_attributes_list = soup.findAll('th', class_='css-16lvhul ezjvm5n1')
	tag_value_attributes = soup.findAll('td', class_='css-9xodgi ezjvm5n0')

	for key, value in zip(all_attributes_list, tag_value_attributes):
		if 'span' in str(value) or 'href' in str(value):
			continue
		else:
			value_attributes[key.string] = value.string
	print(value_attributes)
	return value_attributes


# for key, value in value_attributes.items():
# 	all_attributes[key].append(value)
#
# print(all_attributes)
