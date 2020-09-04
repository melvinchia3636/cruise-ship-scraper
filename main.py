from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import html
import threading
import json
import re
import os

url_file = os.listdir(r'C:\Users\kelvi\Documents\Python_V2\cruise ship tracker\url')

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--no-default-browser-check')
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--disable-default-apps')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

main = {}

def run(url):

	driver.get(url)
	page = BeautifulSoup(driver.page_source, 'html.parser')
	ship_name = page.find('h1').text
	main[ship_name] = {}
	company = page.find('a', {'class': 'shipCompanyLink'}).text.replace('&amp;', '&')
	main[ship_name]['company'] = company
	try:
		homeports = [i.text.strip() for i in page.find('ul', {'class': 'homeports'}).findAll('a')]
	except:
		homeports = None
	try:
		longlat = [float(i.split()[0]) for i in re.search('\(.+?\)', page.find('div', {'class': 'currentItineraryInfo'}).find('p').text.strip()).group().replace('(coordinates ', '').replace(')', '').split(' / ')]
	except:
		longlat = []
	main[ship_name]['homeports'] = homeports
	huge_raw = page.findAll('div', {'class': 'specificationTable'})
	if len(huge_raw) == 2:
		left = huge_raw[0]
		right = huge_raw[1]
		title = [i.text.lower() for i in left.findAll('td')[::2]]+[i.text.lower() for i in right.findAll('td')[::2]]
		huge_raw = [i.text.replace('\u2019', '\'').replace('\u00a0', '') for i in left.findAll('td')[1::2]]+[i.text.replace('\u2019', '\'') for i in right.findAll('td')[1::2]]
	else:
		huge_raw = page.find('table', {'class': 'table-striped'})
		title = [i.text.lower() for i in huge_raw.findAll('td')[::2]]
		huge_raw = [i.text.replace('\u2019', '\'').replace('\u00a0', '') for i in huge_raw.findAll('td')[1::2]]
	
	for i in range(len(title)):
		main[ship_name][title[i]] = huge_raw[i]
	if "year built" in main[ship_name]:
		if 'new ship' not in main[ship_name]['year built']:
			main[ship_name]['year built'] = {'year': int(main[ship_name]['year built'].replace(' ', '').split('/Age:')[0]), 
											'age': int(main[ship_name]['year built'].replace(' ', '').split('/Age:')[1])}
		else:
			main[ship_name]['year built'] = {'year': int(main[ship_name]['year built'].split(' ')[0]),
											'age': 'new ship'}
	if "crew" in main[ship_name]:
		main[ship_name]["crew"] = int(main[ship_name]["crew"])
	if "cabins" in main[ship_name]:
		main[ship_name]["cabins"] = int(main[ship_name]["cabins"])
	if "speed" in main[ship_name]:
		main[ship_name]['speed'] = {'knot': int(main[ship_name]['speed'].split(' / ')[0].replace(' kn', '')) if '.' not in main[ship_name]['speed'].split(' / ')[0] else float(main[ship_name]['speed'].split(' / ')[0].replace(' kn', '')),
									'kph': int(main[ship_name]['speed'].split(' / ')[1].replace(' kph', '')) if '.' not in main[ship_name]['speed'].split(' / ')[1] else float(main[ship_name]['speed'].split(' / ')[1].replace(' kph', '')),
									'mph': int(main[ship_name]['speed'].split(' / ')[2].replace(' mph', '')) if '.' not in main[ship_name]['speed'].split(' / ')[2] else float(main[ship_name]['speed'].split(' / ')[2].replace(' mph', ''))}
	if 'length (loa)' in main[ship_name]:
		main[ship_name]['length (loa)'] = {'meter': float(main[ship_name]['length (loa)'].split(' / ')[0].replace(' m', '')),
											'feet': float(main[ship_name]['length (loa)'].split(' / ')[1].replace(' ft', ''))}
	if 'beam (width)' in main[ship_name]:
		main[ship_name]['beam (width)'] = {'meter': float(main[ship_name]['beam (width)'].split(' / ')[0].replace(' m', '')),
											'feet': float(main[ship_name]['beam (width)'].split(' / ')[1].replace(' ft', ''))}
	if "passengers" in main[ship_name]:									
		main[ship_name]['passengers'] = {'double occupancy': int(main[ship_name]['passengers'].split(' - ')[0]) if main[ship_name]['passengers'].split(' - ')[0].isnumeric() else None,
										'max occupancy': int(main[ship_name]['passengers'].split(' - ')[1]) if main[ship_name]['passengers'].split(' - ')[1].isnumeric() else None} if len(main[ship_name]['passengers'].split(' - ')) > 1 else int(main[ship_name]['passengers']) if main[ship_name]['passengers'].isnumeric() else None
	if "gross tonnage" in main[ship_name]:
		main[ship_name]['gross tonnage'] = int(main[ship_name]['gross tonnage'].replace(' gt', ''))
	if "decks with cabins" in main[ship_name]:
		main[ship_name]["decks with cabins"] = int(main[ship_name]["decks with cabins"])
	if "decks" in main[ship_name]:
		main[ship_name]["decks"] = int(main[ship_name]["decks"])
	if "passengers-to-space ratio" in main[ship_name]:
		main[ship_name]["passengers-to-space ratio"] = int(main[ship_name]["passengers-to-space ratio"])
	if 'sister-ships' in main[ship_name]:
		main[ship_name]['sister-ships'] = main[ship_name]['sister-ships'].split(', ')
	if 'last refurbishment' in main[ship_name]:
		main[ship_name]['last refurbishment'] = int(main[ship_name]['last refurbishment']) if main[ship_name]['last refurbishment'].isnumeric() else [int(i) for i in main[ship_name]['last refurbishment'].split('-')] if len(main[ship_name]['last refurbishment'].split('-')) > 1 and all([i.isnumeric() for i in main[ship_name]['last refurbishment'].split('-')]) else main[ship_name]['last refurbishment']
	itinerary = []
	if page.find('div', {'id':'itinerary'}):
		for i in page.find('div', {'class': 'tab-content'}).find('div', {'id': 'itinerary'}).find('tbody').findAll('tr'):
			datetime = i.find('td', {'class': 'cruiseDatetime'}).text
			title = i.find('td', {'class': 'cruiseTitle'}).text.strip()
			departure = i.find('td', {'class': 'cruiseDeparture'}).text.strip()
			price = i.find('td', {'class': 'cruisePrice'}).text.strip()

			itinerary.append(
				{
				'date': datetime,
				'title': title,
				'departure': departure,
				'price($USD)': int(price.replace('$', '')) if price != '' else None
				}
				)
	else:	
		itinerary = None
	main[ship_name]['itinerary'] = itinerary
	print(ship_name, ' Done')
	
for file in os.listdir(os.path.abspath(os.getcwd())+'/url')[56:]:
	main = {}
	print(file, 'start')
	current = file
	 
	content = open('url/'+current, 'r').read().split(',')
	content.pop()
	for i in range(len(content)):
		run(content[i])
		print(i+1, ' / ', len(content))

	with open('data/'+file.replace('.dat', '.json'), 'w') as file:
		json.dump(main, file, indent=4)

driver.close()
