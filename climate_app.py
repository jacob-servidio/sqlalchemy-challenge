import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///sqlalchemy-challenge\Resources\hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)


latestdate = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
latestdate = list(np.ravel(latestdate))[0]

latestdate = dt.datetime.strptime(latestdate, '%Y-%m-%d')
latest_year = int(dt.datetime.strftime(latestdate, '%Y'))
latest_month = int(dt.datetime.strftime(latestdate, '%m'))
latest_day = int(dt.datetime.strftime(latestdate, '%d'))

yearBefore = dt.date(latest_year, latest_month, latest_day) - dt.timedelta(days=365)
yearBefore = dt.datetime.strftime(yearBefore, '%Y-%m-%d')




@app.route("/")
def home():
    return (f"Welcome to Surf's Up!: Hawai'i Climate API<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations ~~~~~ a list of all weather observation stations<br/>"
            f"/api/v1.0/precipitaton ~~ the latest year of preceipitation data<br/>"
            f"/api/v1.0/temperature ~~ the latest year of temperature data<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"~~~ datesearch (yyyy-mm-dd)<br/>"
            f"/api/v1.0/datesearch/2015-05-30  ~~~~~~~~~~~ low, high, and average temp for date given and each date after<br/>"
            f"/api/v1.0/datesearch/2015-05-30/2016-01-30 ~~ low, high, and average temp for date given and each date up to and including end date<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"~ data available from 2010-01-01 to 2017-08-23 ~<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())
    
    prcpData = []
    for result in results:
        prcpDict = {result.date: result.prcp, "Station": result.station}
        prcpData.append(prcpDict)

    return jsonify(prcpData)

@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    temp_data = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        temp_data.append(tempDict)

    return jsonify(temp_data)

@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)
