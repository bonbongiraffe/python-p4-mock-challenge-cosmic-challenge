#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET','POST'])
def scientists():
    if request.method == 'GET':
        scientists_serialized = [s.to_dict() for s in Scientist.query.all()]
        return make_response(scientists_serialized, 200)

    if request.method == 'POST':
        data = request.get_json()
        try:
            new_scientist = Scientist(
                name = data["name"],
                field_of_study = data["field_of_study"]
            )
        except ValueError as v_error:
            return make_response({"errors": [str(v_error)]}, 400)
        db.session.add(new_scientist)
        db.session.commit()
        return make_response(new_scientist.to_dict(), 201)

@app.route('/scientists/<int:id>', methods=["DELETE", "GET", "PATCH"])
def scientists_by_id(id):
    scientist = Scientist.query.filter_by(id=id).first()
    if not scientist:
        return make_response({"error": "Scientist not found"}, 200)

    if request.method == "DELETE":
        db.session.delete(scientist)
        db.commit()
        return make_response("", 200)
    
    if request.method == 'PATCH':
        data = request.get_json()
        try:
            for attr in data:
                setattr(scientist, attr, data[attr])
        except ValueError as v_error:
            return make_response({"errors": [str(v_error)]}, 400)
        db.session.commit()
        return make_response(scientist.to_dict(), 202)

    if request.method == "GET":
        missions = [m.to_dict() for m in scientist.missions]
        output_dict = {**scientist.to_dict(), "missions": missions}
        return make_response( output_dict, 200 )

@app.route('/planets', methods=["GET"])
def planets():
    if request.method == "GET":
        planets_serialized = [p.to_dict() for p in Planet.query.all()]
        return make_response(planets_serialized, 200)

@app.route('/missions', methods=["POST"])
def missions():
    if request.method == "POST":
        data = request.get_json()
        try: 
            new_mission = Mission(
                name = data["name"],
                scientist_id = data["scientist_id"],
                planet_id = data["planet_id"]
            )
        except ValueError as v_error:
            return make_response({"errors": [str(v_error)]}, 400)
        db.session.add(new_mission)
        db.session.commit()
        return make_response(new_mission.to_dict(), 201)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
