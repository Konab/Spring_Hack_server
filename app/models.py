from app import db


class Tickets(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
