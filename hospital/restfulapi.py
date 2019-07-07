from flask import jsonify, abort
from flask_restful import Resource

from hospital.models import User
from hospital import api
import requests


class Doctors(Resource):
    def get(self):
        raw_doctors = User.query.filter_by(checked=True).all()

        doctors = []

        for doctor in raw_doctors:
            doctors.append({'id': doctor.id, 'username': doctor.username, 'firstname': doctor.first_name,
                            'lastname': doctor.last_name, 'specialization': doctor.specialization})

        return jsonify(doctors)


class _User(Resource):
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(404)

        return jsonify({'id': user.id, 'username': user.username, 'firstname': user.first_name,
                        'lastname': user.last_name, 'checked': user.checked})


class Patients(Resource):
    def get(self, username):
        doctor = User.query.filter_by(username=username).first()

        patients = []

        for patient in doctor.assigned_patients:
            patients.append({'id': patient.id, 'email': patient.email, 'username': patient.username})

        return jsonify(patients)


class _Doctor(Resource):
    def get(self, username):
        doctor = User.query.filter_by(username=username).first()

        if doctor is None:
            abort(404)

        patients = requests.get('http://127.0.0.1:5000/' + str(doctor.username) + '/patients').json()

        return jsonify({'id': doctor.id, 'email': doctor.email, 'username': doctor.username,
                        'firstname': doctor.first_name, 'lastname': doctor.last_name,
                        'specialization': doctor.specialization, 'patients': patients})


class _Patient(Resource):
    def get(self, username):
        patient = User.query.filter_by(username=username).first()

        if patient is None:
            abort(404)

        diagnoses = []
        for diagnosis in patient.diagnosis:
            diagnoses.append({'id': diagnosis.id, 'name': diagnosis.name,
                              'explanation': diagnosis.explanation, 'diagnosed_by': diagnosis.diagnosed_by})

        return jsonify({'id': patient.id, 'email': patient.email, 'username': patient.username,
                        'firstname': patient.first_name, 'lastname': patient.last_name,
                        'assigned_doctor': patient.doctor.username, 'diagnoses': diagnoses})


api.add_resource(Doctors, '/doctors', endpoint='doctors')
api.add_resource(_User, '/user/<string:username>', endpoint='user')
api.add_resource(_Doctor, '/doctor/<string:username>', endpoint='doctor')
api.add_resource(Patients, '/<string:username>/patients', endpoint='patients')
api.add_resource(_Patient, '/patient/<string:username>', endpoint='patient')
