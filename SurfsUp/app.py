# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.dialects.mssql import DATE
from datetime import datetime, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base() 

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)


# # Assign the measurement class to a variable called `Measurement` and
# # the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station


# # Create a session
session = Session(engine)


# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)



# #################################################
# # Flask Routes
# #################################################
@app.route("/")

### define routes
def welcome():
    return (
        f"Aloha!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start]<br/>"
        f"/api/v1.0/[start]/[end]"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a list last 12 months of precipitation day
    last_12 = session.query(Measurement.date, Measurement.prcp) \
            .where(Measurement.date >= (dt.date(2017, 8, 23) - dt.timedelta(days=365))) \
            .order_by(Measurement.date.desc())

    session.close()

    all_prcp = []
    # Create a dictionary from the row data and append to a list of last_12_list
    for date, prcp in last_12:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        all_prcp.append(precip_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # return list of all station names 
    stations = session.query(Station.station, Station.name)

    session.close()

    all_stations = []
    # Create a dictionary from the row data and append to a list of last_12_list
    for station, name in stations:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    temperature_data = (
        session.query(Measurement.date, Measurement.prcp, Measurement.tobs)
        .filter(Measurement.station == 'USC00519281')
        .all()
)

    session.close

    all_temp_data = []
    # Create a dictionary from the row data and append to a list of last_12_list
    for date, prcp, tobs in temperature_data:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Precipitation"] = prcp
        temp_dict["Tobs"] = tobs
        all_temp_data.append(temp_dict)

    return jsonify(all_temp_data)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_date_tobs = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start).all()
    session.close()

    start_tobs = []
    for min, max, avg in start_date_tobs:
        start_dict = {}
        start_dict['min_temp'] = min
        start_dict['max_temp'] = max
        start_dict['avg_temp'] = avg

        start_tobs.append(start_dict)

    return jsonify (f"Start date:{start}", (start_tobs))

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_end_date_tobs = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date<= end).all()
    session.close()

    start_end_tobs = []
    for min, max, avg in start_end_date_tobs:
        start_dict = {}
        start_dict['min_temp'] = min
        start_dict['max_temp'] = max
        start_dict['avg_temp'] = avg

        start_end_tobs.append(start_dict)

    return jsonify (f"Start date:{start} // End date:{end}", (start_end_tobs))

if __name__ == "__main__":
    app.run(debug=True)
