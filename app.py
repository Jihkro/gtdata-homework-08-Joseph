import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#import flask_sqlalchemy
#from flask_sqlalchemy import SQLAlchemy

from flask import Flask, jsonify



#################################################
# Flask Setup
#################################################
app = Flask(__name__)



engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)



def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1>Routes</h1><br />"
        f"<ul><li>/api/v1.0/precipitation<br />"
        f"Query for the dates and temperature observations from the last year.</li>"
        f"<li>/api/v1.0/stations<br />"
        f"Return a JSON list of stations from the dataset.</li>"
        f"<li>/api/v1.0/tobs<br />"
        f"Return a JSON list of Temperature Observations (tobs) for the previous year.</li>"
        f"<li>/api/v1.0/&lt; start&gt; and /api/v1.0/&lt; start&gt;/&lt; end&gt; <br />"
        f"Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.<br />"
        f"When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.<br />"
        f"When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.</li></ul>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data about the most recent year."""
    finaldate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    startingdate=str(int(finaldate[0:4])-1) + finaldate[4:]
    result = session.query(Measurement.date, func.avg(Measurement.prcp),).filter(Measurement.date > startingdate).order_by(Measurement.date).group_by(Measurement.date).all()
    raindf = pd.DataFrame(result, columns=['date','prcp'])
    raindf.set_index('date',inplace=True)
    return raindf.to_json(orient='table')

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    result = session.execute('Select * from station')
    results = [r for r in result]

    stationsdf = pd.DataFrame({'id':[r[0] for r in results], 'station':[r[1] for r in results], 'name':[r[2] for r in results],
                          'latitude':[r[3] for r in results], 'longitude':[r[4] for r in results], 'elevation':[r[5] for r in results]})
    stationsdf.set_index('id',inplace=True)
    return stationsdf.to_json(orient='table')

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature data about the most recent year."""
    finaldate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    startingdate=str(int(finaldate[0:4])-1) + finaldate[4:]
    result = session.query(Measurement.date, func.avg(Measurement.tobs),).filter(Measurement.date > startingdate).order_by(Measurement.date).group_by(Measurement.date).all()
    raindf = pd.DataFrame(result, columns=['date','tobs'])
    raindf.set_index('date',inplace=True)
    return raindf.to_json(orient='table')

@app.route("/api/v1.0/<start>")
def singledate(start):
    end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    result = calc_temps(start,end)[0]
    return jsonify({'tmin':result[0],'tavg':result[1],'tmax':result[2]})
    
@app.route("/api/v1.0/<start>/<end>")
def doubledate(start,end):
    result = calc_temps(start,end)[0]
    return jsonify({'tmin':result[0],'tavg':result[1],'tmax':result[2]})


if __name__ == '__main__':
    app.run(debug=True)