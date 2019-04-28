from flask import jsonify, request

from app import db
from app.main import bp
from app.models import Tickets

from bs4 import BeautifulSoup
import requests
import json
import math
from dataclasses import dataclass
from threading import Thread


def get_nearest_api(coor):
	CLIENT_ID = '5SOB0CFR2GLLAJWEJL2W4QQRRUV0LZHZIU4NC4QQZM3LIM1Z'
	CLIENT_SECRET = 'RWMRY2PWNPV5ORV3M52QX5VMCJADJALTC4F5CRMT45SBKX2A'

	url = 'https://api.foursquare.com/v2/venues/explore'

	# coor = {'lat': 55.815361, 'lng': 37.512489}

	def get_nearest(coor, url):
		
		params = dict(
			client_id=CLIENT_ID,
			client_secret=CLIENT_SECRET,
			v='20180323', # версия данных для запроса, технический параметр 
			ll='{},{}'.format(coor['latitude'], coor['longitude']),
			radius = 50 
		)

		data_nearest = requests.get(url=url, params=params).json()
		nearest_list = data_nearest['response']['groups'][0]['items']

		props_nearist_list = []
		for i in range(len(nearest_list)):
			temp_dic = {
				'name': data_nearest['response']['groups'][0]['items'][i]['venue']['name'],
				'categories': data_nearest['response']['groups'][0]['items'][i]['venue']['categories'][0]['name'],
				'distance': data_nearest['response']['groups'][0]['items'][i]['venue']['location']['distance']
			}
			props_nearist_list.append(temp_dic)

		return props_nearist_list
	return get_nearest(coor, url)


def get_route_api(coor_from, coor_to):
	APP_ID = 'wPO9uLZlQtPAe3WJ4KgD'
	APP_CODE = 'MVBTSJpnlc83Yb1sCzzXIg'

	api_queue = 'https://route.api.here.com/routing/7.2/calculateroute.json?waypoint0={0}%2C{1}&waypoint1={2}%2C{3}&mode=pedestrian&app_id={4}&app_code={5}'

	# coor_from = {'lat': 55.762141, 'lng': 37.633742}
	# coor_to = {'lat': 55.749407, 'lng': 37.623742}

	def find_route_HERE_API(coor_from, coor_to, api_queue, APP_ID, APP_CODE):
		temp_queue = api_queue.format(coor_from['lat'], coor_from['lng'], coor_to['lat'], coor_to['lng'], APP_ID, APP_CODE)
		data = requests.get(temp_queue).json()
		str_temp = data['response']['route'][0]['summary']['text']
		print('•• ',str_temp)

		# [km, min]
		len_time_list = str_temp.replace('The trip takes <span class="length">', '').replace('km</span> and <span class="time">', '').replace(' mins</span>.', '').split(' ')
		# [coor of rout]
		temp_list =	data['response']['route'][0]['leg'][0]['maneuver'] 

		rout_coor_list = []
		for i in range (len(temp_list)):
			rout_coor_list.append(temp_list[i]['position'])
		print('>> ', len_time_list)
		return (rout_coor_list, len_time_list)

	# Вызов функции 
	return find_route_HERE_API(coor_from, coor_to, api_queue, APP_ID, APP_CODE)


def find_in_xml(*kwargs):
	with open('data.xml', 'r') as f:
		soup = BeautifulSoup(f, features="lxml")
	companies = soup.findAll('company')
	return_data = []
	param = kwargs[0]
	for i in range(len(companies)):
		for key in param:
			if param[key] in companies[i].find(key).text:
				return_data.append(companies[i])
	return return_data


def find_near(coord):
	min_dist = 10000
	curr_comp = None
	lat = float()
	lon = float()
	for company in find_in_xml({'locality-name': 'город Москва'}):
		dist = math.hypot(float(company.coordinates.lat.text) - float(coord[0]), float(company.coordinates.lon.text) - float(coord[1]))
		if min_dist > dist:
			min_dist = dist
			lat = company.coordinates.lat.text
			lon = company.coordinates.lon.text
			curr_comp = company

	return {'company': curr_comp, 'lat': lat, 'lon': lon}



def walking_to_coor(rout_coor_list):
	for coor in rout_coor_list:
		# print('::> ', get_nearest_api(coor))
		print('Get near company - Good')
	# Потом отправляет 


@bp.route('/')
@bp.route('/index', methods=['GET'])
def index():
	return 'Hello world!'


@bp.route('/test', methods=['GET'])
def test():
	return jsonify({'Connection': 'DONE'})


@bp.route('/get_help', methods=['GET'])
def get_help():
	return jsonify({'con': 'done'})


@bp.route('/get_near', methods=['GET'])
def get_near():
	args = request.args.to_dict()
	# ['company-id', 'name', 'address', 'country' 'locality-name', 'street', 'house', 'phone', 'info-page', 'working-time', 'coordinates']

	ans_curr_comp = find_near([args['lon'], args['lat']])
	curr_comp = ans_curr_comp['company']
	dict_curr_comp = {
		'company-id': str(curr_comp.find('company-id').text),
		'name': str(curr_comp.find('name').text),
		'address': str(curr_comp.find('address').text),
		'info-page': str(curr_comp.find('info-page').text),
		'working-time': str(curr_comp.find('working-time').text),
		'lat': float(ans_curr_comp['lat']),
		'lon': float(ans_curr_comp['lon']),
	}

	coor_from = {'lat': float(args['lon']), 'lng': float(args['lat'])}
	coor_to = {'lat':float(dict_curr_comp['lat']), 'lng':float(dict_curr_comp['lon'])}
	rout_coor_list, len_time_list = get_route_api(coor_from=coor_from, coor_to=coor_to)
	Thread(target=walking_to_coor, args=([rout_coor_list])).start()
	print('good')
	print(':::> ', len_time_list)

	return jsonify(dict_curr_comp)
