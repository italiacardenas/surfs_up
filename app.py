# Import datetime, Numpy, and Pandas & assign them alias 
import datetime as dt
import numpy as np
import pandas as pd

# SQLAlchemy dependencies to help access data in SQLite database
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# add code to import depndencies form Flask
from flask import Flask, jsonify

# Access and query  the SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect the database into our classes 
Base = automap_base()

# reflect the tables 
Base.prepare(engine, reflect=True)

# save our references to each table with a variable
Measurement = Base.classes.measurement
Station = Base.classes.station 

# create a session link from Python to our database
session = Session(engine)

# define our app for our Flask application called "app"
# note we are not using any other file to run this code
app = Flask(__name__)

# We want our welcome route to be the ROOT 
# (in this case essentially the homepage)

# deifne welcome route
# welcome function with a return statement 
# add the other routes using f-strings to display them for investors
# naming convention /api/v1.0/ followed by name of the route signifies that this is verison 1 of our application
@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

# create a new route for precipitation
# add the function and calculate the date from one year ago to the most recent date in database
# .\ is used to signify that we want our query to continue to the next line 
# "precipation ="" is a query to get the date and precipitation for the previous year  
# Jsonify() converts dictionary to a json file

@app.route("/api/v1.0/precipitation")

def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)

# create route for stations 
# use np.ravel() to unravel results into a one dimensional array 
# then convert unraveled results into a list using the function list()
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# Monthly temperature route
# Define the route, create a function
#calculate the day one year ago from the last date in db 
# query the primary station for all the temperature observations from previous year 
# unravel results and convert to list then jsonify
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# route for summary statistics, diff bc we are providing both a start and end date
# create function called stats(), add start and end parameters
# create a query to select the min, avg, max temps from SQLite DB by creating list "sel"
# add if-not statement to determine the starting and end date
# query db using a th elist then unravel results, then convert them to a list, then jsonify
# * asterisk next to *sel is used to indicate there will be multiple results for the query 
# lastlyt query which will get our statistics data
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)