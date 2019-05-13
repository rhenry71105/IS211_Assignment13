"""
	Author: Rickardo Henry
	Description: IS211-Assignment13
"""


from flask import Flask, g, render_template, redirect, request, url_for, session, flash
from functools import wraps
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "#W$SERX^34ewqdasxD%TCYTFF&*(VIYF&(GVUO9guvosagd80ovag0d83"
app.database = "lab13.db"
app.PROPAGATE_EXCEPTIONS = True


def connect_db():
    return sqlite3.connect(app.database)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login reguired')
            return redirect(url_for('login'))
    return wrap


@app.route('/dashboard', methods = ['GET'])
@login_required
def dashboard():
    # g - flask object that stores temp obj or req, gets reset on refresh
    g.db = connect_db()
    cur = g.db.execute('select * from students')
    students = [dict(id=row[0], fname=row[1], lname=row[2]) for row in cur.fetchall()]

    quizzes = []
    cur = g.db.execute('select * from quizzes')
    quizzes = [dict(id=row[0], subject=row[1], questions=row[2], date=row[3]) for row in cur.fetchall()]

    cur= g.db.execute('select * from results')
    results = [dict(student_id=row[0], quiz_id=row[1], result=row[2]) for row in cur.fetchall()]
    g.db.close()

    return render_template('index.html', students=students, quizzes=quizzes, results=results, title='Home')

@app.route("/")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != 'rickardo.henry' or request.form['password'] != 'admin11230':
            flash("Invalid credentials. Please try again.")
        else:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template('login.html',title='Login')


@app.route('/logout')
def logout():
    session.pop('logged_in', True)
    return redirect(url_for('dashboard'))


@app.route('/student/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']

        if len(fname.strip()) < 1 or len(lname.strip()) < 1 :
            flash("Empty fields. Please try again.")
        else:
            g.db = connect_db()
            g.db.execute('INSERT INTO students (fname, lname) values (?, ?)', (fname, lname))
            g.db.commit()
            return redirect(url_for('dashboard'))

    return render_template('add-student.html', title='Add Student')


@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    if request.method == 'POST':
        day = request.form['day']
        month = request.form['month']
        year = request.form['year']
        subject = request.form['subject']
        questions = request.form['questions']

        if len(subject.strip()) < 1:
            flash("Empty subject. Please try again.")
        elif len(questions.strip()) < 1:
            flash("Empty Number of Questions. Please try again.")
        elif not re.match('^-?[0-9]+$',questions):
            flash("Please enter a valid number for  \"Number of Questions\" field.")
        elif len(day) < 1 or len(month) < 1 or  len(year) < 1 :
            flash("Empty fields in date. Please try again.")

        else:
            if "1" in day and day != "11":
                day = day + "st"
            elif "2" in day:
                day = day + "nd"
            elif "3" in day:
                day = day + "rd"
            else:
                day = day + "th"

            date = month +", " + day + ", "+ year

            g.db = connect_db()
            g.db.execute('INSERT INTO quizzes (subject, questions, date_taken) values (?, ?, ?)', (subject, questions, date))
            g.db.commit()
        return redirect(url_for('dashboard'))

    return render_template('add-quiz.html', months=months, title='Add Quiz')


@app.route('/results/add', methods=['GET', 'POST'])
@login_required
def add_result():
    g.db = connect_db()
    cur = g.db.execute('SELECT id from students')
    students = [row[0] for row in cur.fetchall()]

    cur = g.db.execute('SELECT id from quizzes')
    quizzes = [row[0] for row in cur.fetchall()]

    if request.method == 'POST':
        student = request.form['student']
        quiz = request.form['quiz']
        score = request.form['score']

        if len(student) < 1 or len(quiz) < 1 or len(score) < 1 :
            flash("Empty fields. Please try again.")
        else:
            g.db = connect_db()
            g.db.execute('INSERT INTO results (student_id, quiz_id, score) values (?, ?, ?)', (student, quiz, score))
            g.db.commit()
            return redirect(url_for('dashboard'))

    return render_template('add-result.html', students=students, quizzes=quizzes, title='Add Student')


@app.route('/student/<id>', methods = ['GET'])
@login_required
def quiz_lookup(id):
    g.db = connect_db()
    cur = g.db.execute('SELECT * from students where id = ?',(id))
    student = cur.fetchone()
    student = {'id':student[0], 'fname': student[1], 'lname': student[2]}

    cur = g.db.execute('SELECT quiz_id, score from results where student_id = ?', id)
    results = [dict(quiz_id = row[0], score = row[1]) for row in cur.fetchall()]

    return render_template('results.html', results = results, student = student )


if __name__ == '__main__':
    app.run(debug=True)
