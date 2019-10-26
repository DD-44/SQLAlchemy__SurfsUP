# Import Dependencies
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify
import datetime as dt
import numpy as np
from pprint import pprint


# Create an engine for the hawaii.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the invoices and invoice_items tables
Measurement = Base.classes.measurement
Station = Base.classes.station

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
         f"Avalable Routes:<br/>"
         
         f"/api/v1.0/precipitation<br/>"
         f"- Dates and Temperature Observations from last year<br/>"
         
         f"/api/v1.0/stations<br/>"
         f"- List of weather stations from the dataset<br/>"

         f"/api/v1.0/tobs<br/>"
         f"- List of temperature observations (tobs) from the previous year<br/>"

         f"/api/v1.0/start date<br/>"
         f"- List of min, avg, and max temperature for a given start date between 2016-08-22 and 2017-08-23<br/>"
        
         f"/api/v1.0/start date/end date<br/>"
         f"- List of min, avg, and max temperature for a given start/end range between 2016-08-22 and 2017-08-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of Dates and precipitation from last year"""
    # Query for the last 12months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date <= '2017-08-23').\
        filter(Measurement.date >= '2016-08-24').all()
    session.close()
    # Convert the query results into a dictionary using date as the key and precipitation as the value
    all_prcp = []
    for result in results:
        prcp_dict = {}
        prcp_dict["date"] = result[0]
        prcp_dict["prcp"] = result[1]

        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of weather stations from the dataset """
    # Query all stations
    results = session.query(Station.station).all()
    session.close()
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observations from the previous year """
    # Query for all temperature observations from previous year
    results = session.query(Measurement.date, Measurement.tobs).\
        group_by(Measurement.date).\
        filter(Measurement.date <= '2017-08-23').\
        filter(Measurement.date >= '2016-08-22').all()
    session.close()
    tobs_list=[]
    for tobs in results:
        tobs_dict = {}
        tobs_dict["station"] = tobs[0]
        tobs_dict["tobs"] = float(tobs[1])
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_only(start):
    """Return a list of min, avg, max for specific dates"""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
   
    results= session.query(*sel).filter(Measurement.date >= start).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)



@app.route("/api/v1.0/<start>/<end>")

def start_end(start, end):
    """Return a list of min, avg, max for specific dates"""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
     
    results2 = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    temps2 = list(np.ravel(results2))
    return jsonify(temps2)


# when there are code changes
if __name__ == '__main__':
	app.run(debug=True)