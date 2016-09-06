from flask import render_template, flash,\
					redirect, session,\
					request, url_for,\
					abort\

from functools import wraps
from app import app, db
from app.models import Candidate, Vote
from helpers import get_formula

"""
Require that users be logged in as admins
"""
def admin_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if not 'admin' in session \
			or not session['admin']:
			return redirect(url_for('index'))
		return f(*args, **kwargs)
	return decorated

@app.route('/')
def index():
	return render_template('index.html')

"""
Require that users be logged in, as admins or regular
"""
def login_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if (not 'admin' in session or not session['admin']) \
			and (not 'logged_in' in session or not session['logged_in']):
			return redirect(url_for('index'))
		return f(*args, **kwargs)
	return decorated


def check_login():
	if 'admin' in session and session['admin']:
		flash("Logged in as Admin")
		return True
	elif 'logged_in' in session and session['logged_in']:
		flash("Logged in as User")
		return True
	else:
		return False

@app.route('/login/', methods=['GET', 'POST'])
def login():
	if not check_login():
		if request.method == 'GET':
			return render_template('login.html')
		else:
			if request.form['password'] == app.config['BROTHER_PW']:
				session['logged_in'] = True
				flash('Logged in')
			else:
				flash('Incorrect Password')
				return redirect(url_for('login'))

	return redirect(url_for('vote'))

@app.route('/adminlogin/', methods=['GET', 'POST'])
def admin_login():
	if not check_login():
		if request.method == 'GET':
			return render_template('admin_login.html')
		else:
			if request.form['password'] == app.config['ADMIN_PW']:
				session['admin'] = True
				flash('Logged in as Admin')
			else:
				flash('Incorrect Password')
				return redirect(url_for('admin_login'))

	return redirect(url_for('vote'))

from models import FallVote
@app.route('/fall/',methods=['GET', 'POST'])
@login_required
def fall_vote():

	if request.method == 'POST':

		v = FallVote(voter=request.form.get('voter'),
					joe=(request.form.get('joe') == 'on'),
					nolan=(request.form.get('nolan') == 'on'),
					jeremy=(request.form.get('jeremy') == 'on'),
					aidan=(request.form.get('aidan') == 'on'))
		try:
			db.session.add(v)
			db.session.commit()
			flash("Thanks for voting. Your vote has been received.")
		except Exception as e:
			print e
			flash("Your vote failed. Have you already voted?")
			db.session.rollback()

	return render_template('fall_vote.html')

@app.route('/fall_results/', methods=['GET'])
@admin_required
def fall_results():

	votes = FallVote.query.all()
	jeremy = sum(map(lambda s : s.jeremy, votes))
	nolan = sum(map(lambda s : s.nolan, votes))
	joe = sum(map(lambda s : s.joe, votes))
	aidan = sum(map(lambda s : s.aidan, votes))

	return render_template('fall_results.html', n=len(votes), votes=votes, jeremy=jeremy, joe=joe, nolan=nolan, aidan=aidan)


@app.route('/logout/',methods=['GET'])
def logout():
	session['admin'] = False
	session['logged_in'] = False
	flash("Logged out. Thanks!")
	return redirect(url_for('index'))

@app.route('/setvote/', methods=['GET', 'POST'])
@admin_required
def setup_vote():

	current = Candidate.query.one_or_none()

	if request.method == 'GET':
		return render_template('vote_setup_form.html', current = current)
	else:
		if 'name' in request.form and not request.form['name'] is None:
			name = request.form['name']
			rnd = request.form['round'].lower().strip()

			if current is None or current.name.lower().strip() != name.lower().strip():
				Candidate.query.delete()
				Vote.query.delete()

				# TODO
				# FIX SO THAT UPDATES WITHOUT RESETS DON'T CRASH THE DB.

				new_c = Candidate(name=name, rnd=rnd)

				try:
					db.session.add(new_c)
					db.session.commit()
					flash("New Candidate. Previous Votes Destroyed")
				except:
					flash("Database Error.")
			else:
				flash("Candidate Name Re-entered. Change Name or Continue Vote.")
		else:
			flash("Invalid Input")
	
	return redirect(url_for('setup_vote'))

@app.route('/resetvote/', methods=['GET'])
@admin_required
def reset_vote():
	Vote.query.delete()
	Candidate.query.delete()
	FallVote.query.delete()

	try:
		db.session.commit()
		flash("System reset.")
	except:
		flash("DB Error.")

	return redirect(url_for('setup_vote'))

@app.route('/activate/')
@admin_required
def activate():
	current = Candidate.query.one_or_none()

	if current is None:
		flash("Create a vote first.")
		return redirect(url_for('setup_vote'))

	else:
		current.active = True
		try:
			db.session.commit()
			flash("Vote now active.")
		except:
			flash("Database error.")

	return redirect(url_for('vote'))

@app.route('/deactivate')
@admin_required
def deactivate():
	current = Candidate.query.one_or_none()

	if current is None:
		flash("No vote is currently active.")
		return redirect(url_for('setup_vote'))
	else:
		current.active = False
		try:
			db.session.commit()
			flash("Vote now paused.")
		except:
			flash("Database error.")

	return redirect(url_for('results'))

@app.route('/vote/', methods=['GET', 'POST'])
@login_required
def vote():
	
	current = Candidate.query.one_or_none()

	if request.method == 'GET':
		return render_template('vote_form.html', current=current)
	else:
		if current.active:
			vote = request.form['vote']
			voter = request.form['voter']

			vote = Vote(vote=vote, voter=voter, candidate = current)

			try:
				db.session.add(vote)
				db.session.commit()
				flash("Vote of {0} cast for {1}, using voter name {2}".format(vote.vote, current.name, vote.voter))
			except Exception as e:
				flash("DB Error")
		else:
			flash("No vote was active when your vote was received. Tell someone about this if this was an error.")

	return redirect(url_for('vote'))

@app.route('/results/')
@admin_required
def results():
	candidate = Candidate.query.one_or_none()

	if not candidate is None:
		total = candidate.votes.count()
		yes_count = sum([1 for v in candidate.votes if v.vote == 'Yes'])
		no_count = sum([1 for v in candidate.votes if v.vote == 'No'])
		abstain_count = sum([1 for v in candidate.votes if v.vote == 'Abstain'])
		counts = dict(yes=yes_count,no=no_count, abstain = abstain_count,total=total)

		voters = map(lambda i : i.voter, candidate.votes)

		formula = get_formula(candidate.rnd)

		if total > 0:
			result = formula(yes_count, no_count, abstain_count)
		else:
			result = None

		return render_template('results.html',\
			candidate=candidate, votes=counts, voters=voters, \
		 	result=result, round=candidate.rnd)
	else:
		flash("No vote active. Start one!")
		return redirect(url_for('setup_vote'))





