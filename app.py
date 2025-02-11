# Import the dependencies.
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

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Initiate Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Server recieved request for Home page")
    return(
        f"Module 10 Challenge<br/>"
        f"Precipitation Data...<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Station ID...<br/>"
        f"/api/v1.0/stations<br/>"
        f"Time of Observation Data...<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Temp Stat Data...<br/>"
        f"/api/v1.0/<start><br/>"
        f"Temp Stat Data with End Date<br/>"
        f"/api/v1.0/<start>/<end>")

## Setting a second endpoint, percipitation data
## Returns json version of dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server recieved request for precipitation page")

## Query dates and prcp data
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()

    session.close()
    ## Mapping
    precip = {date: prcp for date, prcp in results}

    return jsonify(precip)


## Setting a third endpoint, station ID
## Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    print("Server recieved request for station page")
    the_stations = session.query(Station.station).all()

    session.close()

# making a list so ravel can be used, step above was a dictionary so ravel couldn't be used since 
# I had two items, but dates and prcp. Only stations here, so ravel can be used to take the list apart.
    station_id = list(np.ravel(the_stations))

    return jsonify(station_id)

## Setting a fourth endpoint, time of observation
## Query the dates and temperature observations of the most-active station for the previous year of data.
## Return a JSON list of temperature observations for the previous year.


@app.route("/api/v1.0/tobs")
def temp():
    print("Server recieved request for time of observation page")
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    most_active_stations = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >=query_date).all()
    
    session.close()

# Ravel flattens object to be a list one on top of the other, verticle list
    station_active = list(np.ravel(most_active_stations))

    return jsonify(station_active)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start = None, end = None):
    print("Server recieved request for time of observation page")

    temp_data = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        temp_query = session.query(*temp_data).filter(Measurement.date >= start).all()
        session.close()

        stats_data = list(np.ravel(temp_query))

        return jsonify(stats_data)
    

    start = dt.datetime.strptime(start, '%m%d%Y')
    end = dt.datetime.strptime(end, '%m%d%Y')
    temp_query = session.query(*temp_data).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    stats_data = list(np.ravel(temp_query))

    return jsonify(stats_data)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum 
# temperature for a specified start or start-end range.

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or 
# equal to the start date.

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates 
# from the start date to the end date, inclusive.





if __name__ =="__main__":
    ## debug=True to restart the app automatically
    app.run(debug=True)