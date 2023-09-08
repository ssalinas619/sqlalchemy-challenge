# Import the dependencies.
from flask import Flask, jsonify

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from pathlib import Path


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Stations = Base.classes.station
Measurment = Base.classes.measurment

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """List precipitation totals"""
    #Query precipitation
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session.query(Measurment.date, Measurment.prcp).filter(Measurment.date >= year_ago)

    session.close()

    #Convert query to dictionary
    precipitation_dict= {"date": "prcp"}

    #Return json of dictionary
    def jsonified():
        return jsonify(precipitation_dict)


   
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """List stations"""
    #Query Stations
    most_active_stations=session.query(Measurment.station, func.count(Measurment.date)).\
                        group_by(Measurment.station).\
                        order_by(func.count(Measurment.date).desc()).all()
    
    session.close()
    
    #Return a JSON list of stations
    all_stations = []
    for station, date in most_active_stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["date"] = date
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """List the dates and temperature observations of the most-active station for the previous year of data"""
    #Query dates and temperatures
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    year_temps = session.query(Measurment.date, Measurment.tobs).\
            filter(Measurment.date >= year_ago, Measurment.station == 'USC00519281').\
            group_by(Measurment.date).\
            order_by(Measurment.date).all()

    session.close()

    #Return a JSON list of temperature observations
    all_year_temps = []
    for date, tobs in year_temps:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        all_year_temps.append(temp_dict)

    return jsonify(all_year_temps)

@app.route("/api/v1.0/<start>")
def start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """List min temp, avg temp, and max temp for all dates greater than or equal to start date"""
    #Query temperatures
    start_temps = session.query(func.min(Measurment.tobs), func.avg(Measurment.tobs), func.max(Measurment.tobs)).\
            filter(Measurment.date >= start_date).all()
          
    session.close()

    #Return a JSON list of the min, avg, and max temp for specified start
    start_range_temps = []
    for min, avg, max in start_temps:
        date_dict = {}
        date_dict["min"] = min
        date_dict["avg"] = avg
        date_dict["max"] = max
        start_range_temps.append(date_dict)

    return jsonify(start_range_temps)

@app.route("/api/v1.0/<start>/<end>")
def startend(start_date,end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """List min temp, avg temp, and max temp from start to end date"""
    #Query temperatures
    startend_temps = session.query(func.min(Measurment.tobs), func.avg(Measurment.tobs), func.max(Measurment.tobs)).\
            filter(Measurment.date >= start_date).\
            filter(Measurment.date <= end_date).all()

    session.close()

    #Return a JSON list of the min, avg, and max temp for specified start-end
    startend_range_temps = []
    for min, avg, max in startend_temps:
        date_dict = {}
        date_dict["min"] = min
        date_dict["avg"] = avg
        date_dict["max"] = max
        startend_range_temps.append(date_dict)

    return jsonify(startend_range_temps)