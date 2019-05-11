import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation by Date: list of  dictionaries"""

    latest_year = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_year = dt.datetime.strptime(latest_year, "%Y-%m-%d") - dt.timedelta(days = 365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= start_year).all()
    print(f"len(results): {len(results)}")
    print(f"type(results): {type(results)}")

    date_prcp = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        date_prcp.append(precip_dict)

    return jsonify(date_prcp)


@app.route("/api/v1.0/stations")
def stations():
    """JSON list of stations"""

    results = session.query(Measurement.station)\
    .group_by(Measurement.station).all()

    results_list = list(np.ravel(results))

    return jsonify(results_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """dates and temperature observations from a year from the last data point."""

    latest_year = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_year = dt.datetime.strptime(latest_year, "%Y-%m-%d") - dt.timedelta(days = 365)

    results = session.query(Measurement.station,Measurement.tobs)\
    .filter(Measurement.date >= start_year).all()


    tobs_list = []
    for station, tob in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["tob"] = tob
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/start/<start>")
def start(start):
    """Temp_MIN, Temp_AVG, and Temp_MAX for all dates greater than and equal to the start parameter."""

    results = session.query(Measurement.date, func.min(Measurement.tobs),
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()

    temp_stats = []

    for date, tmin, tavg, tmax in results:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["tmin"] = tmin
        temps_dict["tavg"] = tavg
        temps_dict["tmax"] = tmax

        temp_stats.append(temps_dict)

    return jsonify(temp_stats)



if __name__ == "__main__":
    app.run(host= "localhost", port=5000, debug=True)
