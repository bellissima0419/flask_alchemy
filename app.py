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
    """Convert the query results to a Dictionary using date as the key and prcp as the value.
       Return the JSON representation of your dictionary."""

    latest_year = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_year = dt.datetime.strptime(latest_year, "%Y-%m-%d") - dt.timedelta(days = 365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= start_year).all()
    print(f"="*50)
    print(f"len(results): {len(results)}")
    print(f"type(results): {type(results)}")

    results_list = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        results_list.append(precip_dict)

    return jsonify(results_list)

if __name__ == "__main__":
    app.run(host= "localhost", port=5000, debug=True)
