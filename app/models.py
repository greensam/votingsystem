from app import db
from app import app
import json
from sqlalchemy.schema import UniqueConstraint

class Candidate(db.Model):
	__tablename__ = 'candidate'
	id = db.Column(db.Integer, primary_key=True)
	rnd = db.Column(db.String(64))
	name = db.Column(db.String(64), unique=True)
	votes = db.relationship('Vote', backref='candidate', lazy='dynamic')
	active = db.Column(db.Boolean, nullable=False, default=False)
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

class FallVote(db.Model):
	__tablename__ = 'fall'
	id = db.Column(db.Integer, primary_key=True)
	voter = db.Column(db.String(120), unique=True)
	joe = db.Column(db.Boolean, nullable= False)
	nolan  = db.Column(db.Boolean, nullable= False)
	jeremy = db.Column(db.Boolean, nullable= False)
	aidan  = db.Column(db.Boolean, nullable= False)

	def __repr__(self):
		return json.dumps({
			'voter': self.voter,
			'joe' : self.joe,
			'nolan' : self.nolan,
			'jeremy' : self.jeremy,
			'aidan' : self.aidan
		})