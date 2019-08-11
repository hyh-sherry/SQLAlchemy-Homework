import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# import Flask
from flask import Flask, jsonify

# Create an app
app = Flask(__name__)


# Home page
@app.route("/")
def home():
    return (f"Welcome to the Climate App Home page!<br/>"
            f"Available Routes:<br/>"
            f"Precipitation Data: /api/v1.0/precipitation<br/>"
            f"Stations Data: /api/v1.0/stations<br/>"
            f"Temperature: /api/v1.0/tobs<br/>"
            f"Temp Calculation with Start Date: /api/v1.0/<start><br/>"
            f"Temp Calculation with Start Date and End Date: /api/v1.0/<start>/<end><br/>"
            f"Start Date and End Date must be in 'yyyy-mm-dd' format"
            )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value.
    Return the JSON representation of your dictionary."""
    
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()

    prcp_lst = [{"date":"prcp"}]
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[str(date)] = prcp
        prcp_lst.append(prcp_dict)
    
    return jsonify(prcp_lst)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    session = Session(engine)
    results = session.query(Station.station, Station.name).all()

    station_lst = [{"id":"name"}]
    for station, name in results:
        station_dict = {}
        station_dict[str(station)] = name
        station_lst.append(station_dict)
    
    return jsonify(station_lst)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""

    session = Session(engine)
    results = session.query(Measurement.date, func.avg(Measurement.tobs)).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.date <= '2017-08-23').group_by(Measurement.date).\
        order_by(Measurement.date).all()

    tobs_lst = [{"date":"temperature observations"}]

    for date, tobs in results:
        tob_dict = {}
        tob_dict[str(date)] = tobs
        tobs_lst.append(tob_dict)
    
    return jsonify(tobs_lst)


@app.route("/api/v1.0/<start>")
def temp_from_start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range.

    When given the start only, calculate TMIN, TAVG, and TMAX for all dates 
    greater than and equal to the start date.

    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates 
    between the start and end date inclusive."""

    session = Session(engine)

    available_dates = list(np.ravel(session.query(Measurement.date).all()))

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
        func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    result_lst = list(np.ravel(results))

    for i in available_dates:
        if i == start:
                return jsonify(result_lst)  

    return jsonify({"error": f"Date {start} not found."}), 404


@app.route("/api/v1.0/<start>/<end>")
def temp_between_dates(start,end):
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range.
    
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates 
    greater than and equal to the start date.
    
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates 
    between the start and end date inclusive."""
    
    session = Session(engine)
    available_dates = list(np.ravel(session.query(Measurement.date).all()))
    
    #if end != "":
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
        func.max(Measurement.tobs)).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    result_lst = list(np.ravel(results))
    
    for i in available_dates:
        if i == start:
            for j in available_dates:
                if j == end:
                    return jsonify(result_lst) 
            return jsonify({"error": f"End date {end} not found."}), 404 
    return jsonify({"error": f"Start date {start} not found."}), 404
    
    #else:
    #    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
    #        func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
        
    #    result_lst = list(np.ravel(results))
    
    #    for i in available_dates:
    #        if i == start:
    #                return jsonify(result_lst)  
    
    #    return jsonify({"error": f"Date {start} not found."}), 404



if __name__ == "__main__":
    app.run(debug=True)
