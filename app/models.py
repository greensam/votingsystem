from app import db
from app import app

from sqlalchemy.schema import UniqueConstraint

class Candidate(db.Model):
	__tablename__ = 'candidate'
	id = db.Column(db.Integer, primary_key=True)
	rnd = db.Column(db.String(64))
	name = db.Column(db.String(64), unique=True)
	votes = db.relationship('Vote', backref='candidate', lazy='dynamic')

	__table_args__ = (UniqueConstraint('name'),)

	def __repr__(self):
		return '<Candidate {0}>'.format(self.name)

class Vote(db.Model):
	__tablename__ = 'vote'
	id = db.Column(db.Integer, primary_key=True)
	cname = db.Column(db.String(64), db.ForeignKey('candidate.name'))
	voter = db.Column(db.String(64))
	vote = db.Column(db.String(10))

	def __repr__(self):
		return '<Vote of {0} for {1}, cast by {2}'\
				.format(self.vote, self.candidate, self.voter)

