from flask import jsonify, request

from app import db
from app.main import bp
from app.models import Tickets

from bs4 import BeautifulSoup
import requests
import json
import math


def find_in_xml(*kwargs):
	with open('data.xml', 'r') as f:
		soup = BeautifulSoup(f)
	companies = soup.findAll('company')
	return_data = []
	param = kwargs[0]
	for i in range(len(companies)):
		for key in param:
			if companies[i].find(key).text == param[key]:
				return_data.append(companies[i])
	return return_data


def find_near(coord):
	min_dist = 10000
	lat = float()
	lon = float()
	for company in find_in_xml({'locality-name': 'город Москва'}):
		dist = math.hypot(companies.coordinates.lat.text - coord[0], companies.coordinates.lon.text - coord[1])
		print('-> ', dist)
		if min_dist > dist:
			min_dist = dist
			lat = companies.coordinates.lat.text
			lon = companies.coordinates.lon.text

	return {'company': company, 'lat': lat, 'lon': lon}



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
	print(args)
	print(find_near([args['lat'], args['lon']]))
	return jsonify(None)
