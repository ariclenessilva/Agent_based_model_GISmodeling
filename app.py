from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import random
import string
import json
from datetime import date

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5433/test'

db = SQLAlchemy(app)

class agents(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    full_name = db.Column(db.String(80))
    gender = db.Column(db.String(120))
    birthday = db.Column(db.DateTime,default=datetime.utcnow)
    policy_district = db.Column(db.String(120))
    cases = db.relationship("cases")

    def __repr__(self):
        return '%r>' % self.full_name

class locations(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    street = db.Column(db.String(120))
    apt = db.Column(db.String(80))
    zipcode = db.Column(db.String(80))
    description = db.Column(db.String(120))
    x_coordinate = db.Column(db.String(120))
    y_coordinate = db.Column(db.String(120))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    cases = db.relationship("cases")

    @property
    def serialize(self):
        try:
            return [float(self.longitude), float(self.latitude),self.street]
        except:
            pass

class victims(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    full_name = db.Column(db.String(80))
    phone_number = db.Column(db.Integer)
    bi_or_passport_id = db.Column(db.String(120), db.ForeignKey('bi_or_passport.id'))
    cases = db.relationship("cases")

    @property
    def serialize(self):
        try:
            return {'id':self.id,
                    'full_name':self.full_name,
                    'phone_number':self.phone_number,
                    'bi_or_passport_id':self.bi_or_passport_id,
                    }
        except:
            pass

class criminals(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    full_name = db.Column(db.String(120))
    number_cases = db.Column(db.Integer)
    FBI_code = db.Column(db.String(80))
    bi_or_passport_id = db.Column(db.String(120), db.ForeignKey('bi_or_passport.id'))
    cases = db.relationship("cases")

    @property
    def serialize(self):
        try:
            return {'id':self.id,
                    'full_name':self.full_name,
                    'number_cases':self.number_cases,
                    'bi_or_passport_id':self.bi_or_passport_id,
                    'FBI_code':self.FBI_code,
                    }
        except:
            pass

class bi_or_passport(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    full_name = db.Column(db.String(120))
    gender = db.Column(db.String(80))
    father_name = db.Column(db.String(120))
    mother_name = db.Column(db.String(120))
    birthday = db.Column(db.DateTime, default=datetime.utcnow)
    address = db.Column(db.String(150))
    victims = db.relationship('victims', backref='bi_or_passport', lazy=True)
    criminals = db.relationship('criminals', backref='bi_or_passport', lazy=True)

class crime_primary_types(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    type = db.Column(db.String(80))
    description = db.Column(db.String(120))
    cases = db.relationship("cases")

    @property
    def serialize(self):
        try:
            return {'id':self.id,
                    'type':self.type,
                    'description':self.description,
                    }
        except:
            pass

class cases(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    victim_id = db.Column(db.String(80), db.ForeignKey('victims.id'))
    criminal_id = db.Column(db.String(80), db.ForeignKey('criminals.id'))
    crime_primary_type_id = db.Column(db.String(80), db.ForeignKey('crime_primary_types.id'))
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    updated_on = db.Column(db.DateTime,default=datetime.utcnow)
    agent_id = db.Column(db.String(80), db.ForeignKey('agents.id'))
    arrest = db.Column(db.String(80))
    FBI_code = db.Column(db.String(80))
    location_id = db.Column(db.String(80), db.ForeignKey('locations.id'))

    @property
    def serialize(self):
        try:
            return {'id':self.id,
                    'victim_id':self.victim_id,
                    'criminal_id':self.criminal_id,
                    'crime_primary_type_id':self.crime_primary_type_id,
                    'created_at':self.created_at,
                    'updated_on':self.updated_on,
                    'agent_id':self.agent_id,
                    'arrest':self.arrest,
                    'FBI_code':self.FBI_code,
                    'location_id':self.location_id,
                    }
        except:
            pass

db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    the_cases = []

    for case in cases.query.all():
        victim = victims.query.filter_by(id=case.serialize['victim_id']).first()
        criminal = criminals.query.filter_by(id=case.serialize['criminal_id']).first()
        crime_primary_type = crime_primary_types.query.filter_by(id=case.serialize['crime_primary_type_id']).first()
        location = locations.query.filter_by(id=case.serialize['location_id']).first()
        the_data = {
            "type": "Feature",
            "properties": {
                "name": "Coors Field",
                "amenity": "Baseball Stadium",
                "popupContent": "This is where the Rockies play!"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [location.serialize[0], location.serialize[1]]
            },
            'data':{
            'id':case.serialize['id'],
            'victm':victim.serialize['full_name'],
            'criminal':criminal.serialize['full_name'],
            'crime_primary_type':crime_primary_type.serialize['type'],
            'created_at':str(case.serialize['created_at']),
            'updated_on':case.serialize['updated_on'],
            'location':location.serialize[2]
            }
        }
        the_cases.append(the_data)
    all_reported_Crime_data = [coordinate.serialize for coordinate in locations.query.all()]

    if request.method == 'POST':
        new_id = ''.join((random.choice(string.ascii_letters) for i in range(5)))
        new_FBIcode = ''.join((random.choice(string.ascii_letters) for i in range(10)))

        new_case = cases(id=new_id,victim_id=request.form['victim_id'],criminal_id=request.form['criminal_id'],crime_primary_type_id=request.form['crime_primary_type_id'],
        agent_id=request.form['agent_id'], arrest=request.form['arrest'],FBI_code=new_FBIcode,location_id=request.form['location_id'])

        db.session.add(new_case)
        db.session.commit()

    return render_template('index.html',the_cases=the_cases, all_reported_Crime_data=all_reported_Crime_data)

@app.route('/api/all_reported_crime')
def api_allCrimes():
    return jsonify(geometry=[coordinate.serialize for coordinate in locations.query.all()])

@app.route('/api/crime_by_id/<id>')
def crime_byid(id):
    crime_by_id = {}

    for case in cases.query.all():
        victim = victims.query.filter_by(id=case.serialize['victim_id']).first()
        criminal = criminals.query.filter_by(id=case.serialize['criminal_id']).first()
        crime_primary_type = crime_primary_types.query.filter_by(id=case.serialize['crime_primary_type_id']).first()
        location = locations.query.filter_by(id=case.serialize['location_id']).first()

        crime_by_id[case.serialize['id']] = {
            "type": "Feature",
            "properties": {
                "name": "",
                "amenity": "",
                "popupContent": ""
            },
            "geometry": {
                "type": "Point",
                "coordinates": [location.serialize[0], location.serialize[1]]
            },
            'data':{
            'id':case.serialize['id'],
            'victm':victim.serialize['full_name'],
            'criminal':criminal.serialize['full_name'],
            'crime_primary_type':crime_primary_type.serialize['type'],
            'created_at':case.serialize['created_at'],
            'updated_on':case.serialize['updated_on'],
            'location':location.serialize[2]
            }
        }
    try:
        return jsonify(crime_by_id[id])
    except:
        return 'no value found'


@app.route('/api/search_date/<date>')
def crime_bydate(date):
    crime_by_id = {}

    for case in cases.query.all():
        victim = victims.query.filter_by(id=case.serialize['victim_id']).first()
        criminal = criminals.query.filter_by(id=case.serialize['criminal_id']).first()
        crime_primary_type = crime_primary_types.query.filter_by(id=case.serialize['crime_primary_type_id']).first()
        location = locations.query.filter_by(id=case.serialize['location_id']).first()

        crime_by_id[case.serialize['id']] = {
            "type": "Feature",
            "properties": {
                "name": "",
                "amenity": "",
                "popupContent": ""
            },
            "geometry": {
                "type": "Point",
                "coordinates": [location.serialize[0], location.serialize[1]]
            },
            'data':{
            'id':case.serialize['id'],
            'victm':victim.serialize['full_name'],
            'criminal':criminal.serialize['full_name'],
            'crime_primary_type':crime_primary_type.serialize['type'],
            'created_at':case.serialize['created_at'],
            'updated_on':case.serialize['updated_on'],
            'location':location.serialize[2]
            }
        }
    try:
        return jsonify(crime_by_id)
    except:
        return 'no value found'
