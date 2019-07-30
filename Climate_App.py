import numpy as np
import pandas as pd
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args = {'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()


# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

last_date_qry = session.query(Measurement.date).\
    order_by(Measurement.date.desc()).first()
last_date = last_date_qry[0]
lastDate = dt.datetime.strptime(last_date, '%Y-%m-%d').date()
one_year_ago = lastDate - dt.timedelta(days = 365)
#one_year_ago = dt.datetime.strftime(one_year_ago, '%Y-%m-%d')
#################################################
# Flask Routes
#################################################

@app.route("/")
def Homepage():
    """List all available api routes."""
    return (
        f"Welcome to Surf's Up API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/datesearch/2016-08-01<br/>"
        f"/api/v1.0/datesearch/2016-08-01/2016-08-10<br/>"
    )

@app.route("/api/v1.0/stations")
def stations():
    station = session.query(Station.name).all()
    station_list = list(np.ravel(station))
    return jsonify(station_list)


@app.route("/api/v1.0/precipitation")
def precipitation():

    results = session.query(Measurement.date, Measurement.prcp, Measurement.station)\
            .filter(Measurement.date > one_year_ago).order_by(Measurement.date).all()
    prcp_data = []
    for result in results:
        prcp_dict = {result.date: result.prcp, "Station": result.station}
        prcp_data.append(prcp_dict)
    

    return jsonify(prcp_data)

@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.date, Measurement.tobs, Measurement.station, Station.name)\
            .filter(Measurement.date > one_year_ago).\
            filter(Measurement.station == Station.station).\
                    order_by(Measurement.date).all()
    tobs_data = []
    for result in results:
        tobs_dict = {"Date":result.date, "Temperature (degree F)": result.tobs, "Station":result.station, "Station Name": result.name}
        tobs_data.append(tobs_dict)
    

    return jsonify(tobs_data)

@app.route("/api/v1.0/datesearch/<startDate>")
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)]
    results = session.query(*sel).\
        filter(func.strftime("%Y-%m-%d", Measurement.date)>= startDate).\
        group_by(Measurement.date).all()
    temp = []

    for result in results:
        temp_dict = {}
        temp_dict['Date'] = result[0]
        temp_dict['tmin'] = result[1]
        temp_dict['tavg'] = round(result[2],2)
        temp_dict['tmax']= result[3]
        temp.append(temp_dict)
    return jsonify(temp)

@app.route("/api/v1.0/datesearch/<startDate>/<endDate>")
def start_end(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)]
    results = session.query(*sel).\
        filter(func.strftime("%Y-%m-%d", Measurement.date)>= startDate).\
        filter(func.strftime("%Y-%m-%d", Measurement.date)<= endDate).\
        group_by(Measurement.date).all()
    temp = []

    for result in results:
        temp_dict = {}
        temp_dict['Date'] = result[0]
        temp_dict['tmin'] = result[1]
        temp_dict['tavg'] = round(result[2],2)
        temp_dict['tmax']= result[3]
        temp.append(temp_dict)
    return jsonify(temp)

if __name__ == '__main__':
    app.run(debug=True)
