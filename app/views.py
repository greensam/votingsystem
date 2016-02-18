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
		print current
		return render_template('vote_setup_form.html', current = current)
	else:
		if 'name' in request.form and not request.form['name'] is None:
			name = request.form['name']
			rnd = request.form['round'].lower().strip()

			if current is None or current.name.lower().strip() != name.lower().strip():
				Candidate.query.delete()
				Vote.query.delete()

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
	Candidate.query.delete()
	Vote.query.delete()

	try:
		db.session.commit()
		flash("System reset.")
	except:
		flash("DB Error.")

	return redirect(url_for('setup_vote'))

@app.route('/vote/', methods=['GET', 'POST'])
@login_required
def vote():
	
	current = Candidate.query.one_or_none()

	if request.method == 'GET':
		return render_template('vote_form.html', current=current)
	else:
		vote = request.form['vote']
		voter = request.form['voter']

		vote = Vote(vote=vote, voter=voter, candidate = current)

		try:
			db.session.add(vote)
			db.session.commit()
			flash("Vote of {0} cast for {1}, using voter name {2}".format(vote.vote, current.name, vote.voter))
		except Exception as e:
			print e
			flash("DB Error")

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

		print total
		if total > 0:
			result = formula(yes_count, no_count, abstain_count)
		else:
			result = None

		print "RESULT", result

		return render_template('results.html',\
			candidate=candidate, votes=counts, voters=voters, \
		 	result=result, round=candidate.rnd)
	else:
		flash("No vote active. Start one!")
		return redirect(url_for('setup_vote'))





