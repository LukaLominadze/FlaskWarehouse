from datetime import date, time
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    trips = db.relationship('Trip', back_populates='owner', lazy='dynamic')
    memberships = db.relationship('TripMember', back_populates='user', lazy='dynamic')


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    destination = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    is_public = db.Column(db.Boolean, default=False, nullable=False)

    owner = db.relationship('User', back_populates='trips')
    members = db.relationship('TripMember', back_populates='trip', lazy='dynamic')
    itineraries = db.relationship('Itinerary', back_populates='trip', lazy='dynamic')
    expenses = db.relationship('Expense', back_populates='trip', lazy='dynamic')
    packing_items = db.relationship('PackingItem', back_populates='trip', lazy='dynamic')


class TripMember(db.Model):
    __tablename__ = 'trip_members'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(16), nullable=False, default='viewer')

    trip = db.relationship('Trip', back_populates='members')
    user = db.relationship('User', back_populates='memberships')


class Itinerary(db.Model):
    __tablename__ = 'itineraries'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

    trip = db.relationship('Trip', back_populates='itineraries')
    activities = db.relationship('Activity', back_populates='itinerary', lazy='dynamic')


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itineraries.id'), nullable=False)
    time = db.Column(db.Time, nullable=True)
    title = db.Column(db.String(128), nullable=False)
    place_name = db.Column(db.String(128), nullable=True)
    duration_min = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    itinerary = db.relationship('Itinerary', back_populates='activities')


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    description = db.Column(db.String(256), nullable=True)
    date = db.Column(db.Date, nullable=True)

    trip = db.relationship('Trip', back_populates='expenses')


class PackingItem(db.Model):
    __tablename__ = 'packing_items'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(64), nullable=True)
    is_packed = db.Column(db.Boolean, default=False, nullable=False)

    trip = db.relationship('Trip', back_populates='packing_items')
