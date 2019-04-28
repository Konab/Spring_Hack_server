from flask import jsonify, request

from app import db
from app.main import bp
from app.models import Tickets

from bs4 import BeautifulSoup
import requests
import json
import math
from dataclasses import dataclass


def get_route_api(coor_from, coor_to):
	APP_ID = 'wPO9uLZlQtPAe3WJ4KgD'
	APP_CODE = 'MVBTSJpnlc83Yb1sCzzXIg'

	api_queue = 'https://route.api.here.com/routing/7.2/calculateroute.json?waypoint0={0}%2C{1}&waypoint1={2}%2C{3}&mode=fastest%3Bpedestrian&language=ru-ru&app_id={4}&app_code={5}'


	# coor_from = {'lat': 55.762141, 'lng': 37.633742}
	# coor_to = {'lat': 55.749407, 'lng': 37.623742}


	def find_route_HERE_API(coor_from, coor_to, api_queue, APP_ID, APP_CODE):
	    temp_queue = api_queue.format(coor_from['lat'], coor_from['lng'], coor_to['lat'], coor_to['lng'], APP_ID, APP_CODE)
	    return requests.get(temp_queue).json()

	# Вызов функции 
	return find_route_HERE_API(coor_from, coor_to, api_queue, APP_ID, APP_CODE)

	# Возвращает json  в поле 'text' храниться информация о пути и времени 
	# 'text': 'The trip takes <span class="length">1.8 km</span> and <span class="time">31 mins</span>.'
	#
	# Доступ :
	#        str_temp = data['response']['route'][0]['summary']['text']
	#


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
	['company-id', 'name', 'address', 'country' 'locality-name', 'street', 'house', 'phone', 'info-page', 'working-time', 'coordinates']

	ans_curr_comp = find_near([args['lat'], args['lon']])
	curr_comp = ans_curr_comp['company']
	dict_curr_comp = {
		'company-id': curr_comp.find('company-id').text,
		'name': curr_comp.find('name').text,
		'address': curr_comp.find('address').text,
		'info-page': curr_comp.find('info-page').text,
		'working-time': curr_comp.find('working-time').text,
		'lat': float(ans_curr_comp['lat']),
		'lon': float(ans_curr_comp['lon']),
	}

	coor_from = {'lat': float(args['lat']), 'lng': float(args['lon'])}
	coor_to = {'lat':float(dict_curr_comp['lat']), 'lng':float(dict_curr_comp['lon'])}
	route = get_route_api(coor_from=coor_from, coor_to=coor_to)
	print(route)

	return jsonify(dict_curr_comp)
