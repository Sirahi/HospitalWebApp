from flask import render_template, redirect, request, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import requests

from hospital import app, db
from hospital.forms import LoginForm, RegistrationForm, ChangeDoctorForm, AddDiagnosisForm
from hospital.models import User, Diagnosis


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def _doctors():
    return requests.get('http://127.0.0.1:5000/doctors').json()


def _user(username):
    return requests.get('http://127.0.0.1:5000/user/' + username).json()


def _doctor(username):
    return requests.get('http://127.0.0.1:5000/doctor/' + username).json()


def _patient(username):
    return requests.get('http://127.0.0.1:5000/patient/' + username).json()


@app.route('/')
@app.route('/home')
def home():
    doctors = _doctors()
    return render_template('home.html', title='Home', doctors=doctors)


@app.route('/home/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    doctors = _doctors()

    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return render_template('login.html', title='Sign In', form=form, doctors=doctors)

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        else:
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('profile', username=user.username)
            return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, doctors=doctors)


@app.route('/home/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    doctors = _doctors()
    choices = []
    for doctor in doctors:
        choices.append((doctor['username'], doctor['firstname']))
    form.doc.choices = choices
    if request.method == 'GET':
        return render_template('register.html', title='Registration', form=form, doctors=doctors)

    if form.validate_on_submit():
        if form.checked.data:
            doctor = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                          last_name=form.last_name.data, specialization=form.specialization.data,
                          checked=form.checked.data)
            doctor.set_password(form.password.data)
            db.session.add(doctor)
            db.session.commit()
            login_user(doctor)
        else:
            print(form.doc.data)
            doctor = User.query.filter_by(username=form.doc.data).first()
            patient = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                           last_name=form.last_name.data, checked=form.checked.data, doctor=doctor)
            patient.set_password(form.password.data)
            db.session.add(patient)
            db.session.commit()
            login_user(patient)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('home'))
    flash_errors(form)
    return render_template('register.html', title='Registration', form=form, doctor=doctors)


@app.route('/home/<string:username>')
@login_required
def profile(username):
    doctors = _doctors()
    user = _user(username)

    if user['checked']:
        doctor = _doctor(username)
        patients = []
        for patient in doctor['patients']:
            patients.append(_patient(patient['username']))
        return render_template('doctor.html', title='Doctor', doctors=doctors, doctor=doctor, patients=patients)

    patient = _patient(username)
    doctor = _doctor(patient['assigned_doctor'])
    return render_template('patient.html', title='Patient', doctors=doctors, patient=patient, doctor=doctor)


@app.route('/home/<string:username>/changedoctor', methods=['GET', 'POST'])
def change_doctor(username):
    form = ChangeDoctorForm()
    doctors = _doctors()

    choices = []
    for doctor in doctors:
        choices.append((doctor['username'], doctor['firstname']))

    form.doc.choices = choices
    if request.method == 'GET':
        return render_template('change_doctor.html', title='Change Doctor', form=form, doctors=doctors)
    if form.validate_on_submit():
        patient = User.query.filter_by(username=username).first()
        doctor = User.query.filter_by(username=form.doc.data).first()
        patient.doctor = doctor
        db.session.commit()
        return redirect(url_for('profile', username=patient.username))
    return render_template('change_doctor.html', title='Change Doctor', form=form, doctors=doctors)


@app.route('/home/<string:doc_username>/<string:pat_username>', methods=['GET', 'POST'])
@login_required
def add_diagnosis(doc_username, pat_username):
    form = AddDiagnosisForm()
    doctors = _doctors()

    if request.method == 'GET':
        return render_template('add_diagnosis.html', title='Add Diagnosis', form=form, doctors=doctors)
    if form.validate_on_submit():
        doctor = _doctor(doc_username)
        diagnosed_by = str(doctor['firstname']) + ' ' + str(doctor['lastname'])
        diagnosis = Diagnosis(name=form.name.data, explanation=form.explanation.data, diagnosed_by=diagnosed_by)
        db.session.add(diagnosis)
        patient = User.query.filter_by(username=pat_username).first()
        patient.diagnosis.append(diagnosis)
        db.session.commit()
        return redirect(url_for('profile', username=doc_username))
    return render_template('add_diagnosis.html', title='Add Diagnosis', form=form, doctors=doctors)


@app.route('/home/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
