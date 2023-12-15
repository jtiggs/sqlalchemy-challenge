# Import the dependencies.
import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base= automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Base.classes.keys()
Measurement= Base.classes.measurement
Station=Base.classes.station
# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    """List all available api routes."""
    return(
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/start_date/%Y-%m-%d<br/>' 
        f'/api/v1.0/start_date/%Y-%m-%d/end-date/%Y-%m-%d'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    try:
        recent_date=session.query(func.max(Measurement.date)).scalar()
        ref_date=dt.datetime.strptime(recent_date,'%Y-%m-%d')
        last_12_months=ref_date-dt.timedelta(days=365)
    
        results=session.query(Measurement).filter(
            Measurement.date >= last_12_months).all()
    
        dates=[]
        prcp=[]
    
        for result in results:
            dates.append(result.date),
            prcp.append(result.prcp)
    
        precipitation_dict={date:value for date, value in zip(dates, prcp)}
    
        return jsonify(precipitation_dict)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1.0/stations')
def stations():
    try:
        results=session.query(Station.station).all()
        station_list = list(np.ravel(results))

        return jsonify(station_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1.0/tobs')
def tobs():
    try:
        recent_date=session.query(func.max(Measurement.date)).scalar()
        ref_date=dt.datetime.strptime(recent_date,'%Y-%m-%d')
        last_12_months=ref_date-dt.timedelta(days=365)
        year_temps=session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station=='USC00519281').\
            filter(Measurement.date>= last_12_months).all()
    
        temperature_observations = [{'date': result.date, 'tobs': result.tobs} for result in year_temps]

        return jsonify(temperature_observations)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1.0/start_date/%Y-%m-%d')
def tobs_start(start):
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')

        results = session.query(func.min(Measurement.tobs).label('min_temp'),
                                func.avg(Measurement.tobs).label('avg_temp'),
                                func.max(Measurement.tobs).label('max_temp')).\
            filter(Measurement.date >= start_date).all()

        temperature_stats = {
            'min_temp': results[0].min_temp,
            'avg_temp': results[0].avg_temp,
            'max_temp': results[0].max_temp
        }

        return jsonify(temperature_stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1.0/start_date/%Y-%m-%d/end-date/%Y-%m-%d')
def tobs_start_end(start, end):
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')

        results = session.query(func.min(Measurement.tobs).label('min_temp'),
                                func.avg(Measurement.tobs).label('avg_temp'),
                                func.max(Measurement.tobs).label('max_temp')).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()

        temperature_stats = {
            'min_temp': results[0].min_temp,
            'avg_temp': results[0].avg_temp,
            'max_temp': results[0].max_temp
        }

        return jsonify(temperature_stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__=='__main__':
    app.run(debug=True)