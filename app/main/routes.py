from flask import jsonify, request

from app import db
from app.main import bp
from app.models import Tickets

from bs4 import BeautifulSoup
import requests
import json
import math
from dataclasses import dataclass


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
		'company-id': curr_comp.company-id.text,
		'name': curr_comp.name.text,
		'address': curr_comp.address.text,
		'info-page': curr_comp.info-page.text,
		'working-time': curr_comp.working-time.text,
		'lat': ans_curr_comp['lat'],
		'lat': ans_curr_comp['lon'],
	}
	print(dict_curr_comp)

	return jsonify(dict_curr_comp)
