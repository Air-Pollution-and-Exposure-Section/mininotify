#!/usr/bin/env python3
import requests
import json
from typing import List, Union, Tuple

# CONFIGS
from config import API_KEY as api_key
from config import TEMPLATE_ID as template_id

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, String, Numeric
from sqlalchemy import create_engine, Column, Integer, ForeignKey, String

from skynet.database.tables.Emails import Emails
from skynet.database.tables.Participant import Participant
from skynet.database.tables.Responsibility import Responsibility
from skynet.database.tables.Instrument import Instrument
from skynet.database.tables.Study import Study
from skynet.database.tables.Site import Site
from skynet.database.Base import Base
from skynet.database.tables.Location import Location
from skynet.database.tables.PurpleAirKeys import PurpleAirKeys

from sqlalchemy import func, and_
from datetime import datetime, timedelta, timezone

from skynet.database.tables.Humidity import Humidity
from skynet.database.tables.Temperature import Temperature
from skynet.database.tables.Particulate import Particulate

import typing

from  sqlalchemy import DateTime

from sqlalchemy.exc import IntegrityError

class EmailLogs(Base):
   __tablename__='email_logs'
   date = Column(DateTime, primary_key=True)
   participant_id = Column(Integer, ForeignKey('participant.id'), primary_key=True)
   status_code = Column(Integer)
   error = Column(String)
   message = Column(String)


class Handler():
    def __init__(self, user:str, dbname:str, host:str, password:str, port:str) -> None:
        self.user = user
        self.dbname = dbname
        self.host = host
        self.password = password
        self.port = port
        DATABASE_URI = f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}'
        self.echo_state = True
        self.engine = create_engine(DATABASE_URI, echo=self.echo_state)
        self.session = None

    def start_session(self):
        self.session = sessionmaker(bind=self.engine)()

    def close_session(self):
        if self.session:
            self.session.close()
            self.session = None
        else:
            print("No session to close")


def send_email(email:str, personalisation:dict)->Tuple[str, json]:
  # Define the headers and data
  headers = {
      'Authorization': f'ApiKey-v1 {api_key}',
      'Content-Type': 'application/json',
      'base_url': 'https://notification.canada.ca'
  }

  data = {
      'email_address': email,
      'template_id': template_id,
      'personalisation': personalisation
  }

  # Make the POST request
  response = requests.post(
      'https://api.notification.canada.ca/v2/notifications/email',
      headers=headers,
      json=data
  )

  # Print the response
  print("status code: ", response.status_code)
  print("response: ", response.json())
  return [response.status_code, response.json()]


def record_email_logs(participant_id, status_code, response):
  participant_id = participant_id
  # Get the current date and time in UTC
  current_utc_time = datetime.now(timezone.utc)
  # Format the date and time as a string in the desired format
  date = current_utc_time.strftime('%Y-%m-%d %H:%M:%S')
  status_code = status_code
  response = response
  error = response['errors'][0]['error'] if 'errors' in response else None
  message = response['errors'][0]['message'] if 'errors' in response else None

  dbHandler = Handler(user=user, dbname=dbname, host=host, password=password, port=port)

  dbHandler.start_session()

  dbHandler.session

  record = EmailLogs(
     date=date,
     participant_id=participant_id,
     status_code=status_code,
     error=error,
     message=message
  )

  try:
      dbHandler.session.add(record)
      dbHandler.session.commit()
      print("Email Logs data inserted successfully.")
  except IntegrityError:
      dbHandler.session.rollback()
      print("Failed to insert Email Logs data due to integrity error.")
  except Exception as e:
      dbHandler.session.rollback()
      print(f"Failed to insert Email Logs data: {e}")
  
  dbHandler.close_session()


def run(participant_id:int)->None:
  dbHandler = Handler(user=user, dbname=dbname, host=host, password=password, port=port)

  dbHandler.start_session()

  # get the participant
  participant = dbHandler.session.query(Participant).filter_by(id=participant_id).first()

  # only query the AQEggs
  manufacturer = 'Wicked Device'
  instrument_id_query = dbHandler.session.query(Responsibility.instrument_id).join(Instrument).filter(
      Responsibility.participant_id == participant_id,
      Instrument.manufacturer == manufacturer
  ).all()

  instrument_ids = [result.instrument_id for result in instrument_id_query]
  instrument_id = instrument_ids[0]

  # get the instrument serial number
  instrument = dbHandler.session.query(Instrument).filter_by(id=instrument_id).first()

  # HUMIDITIES
  # Calculate the time 24 hours ago from now
  # Get the current time in UTC
  current_utc_time = datetime.now(timezone.utc)
  # Calculate the time 24 hours ago from now in UTC
  time_24_hours_ago = current_utc_time - timedelta(hours=24)

  # Perform the query to get the maximum raw_val within the last 24 hours
  hHigh = dbHandler.session.query(func.max(Humidity.raw_val)).filter(
      Humidity.date >= time_24_hours_ago,
      Humidity.instrument_id==instrument_id
  ).scalar()
  print(hHigh)

  # Perform the query to get the min raw_val within the last 24 hours
  hLow = dbHandler.session.query(func.min(Humidity.raw_val)).filter(
      Humidity.date >= time_24_hours_ago,
      Humidity.instrument_id==instrument_id
  ).scalar()
  print(hLow)

  # Perform the query to get the avg raw_val within the last 24 hours
  hAvg = dbHandler.session.query(func.avg(Humidity.raw_val)).filter(
      Humidity.date >= time_24_hours_ago,
      Humidity.instrument_id==instrument_id
  ).scalar()

  # TEMPS
  current_utc_time = datetime.now(timezone.utc)
  # Calculate the time 24 hours ago from now in UTC
  time_24_hours_ago = current_utc_time - timedelta(hours=24)

  # Perform the query to get the maximum raw_val within the last 24 hours
  tHigh = dbHandler.session.query(func.max(Temperature.raw_val)).filter(
      Temperature.date >= time_24_hours_ago,
      Temperature.instrument_id==instrument_id
  ).scalar()

  # Perform the query to get the min raw_val within the last 24 hours
  tLow = dbHandler.session.query(func.min(Temperature.raw_val)).filter(
      Temperature.date >= time_24_hours_ago,
      Temperature.instrument_id==instrument_id
  ).scalar()

  # Perform the query to get the avg raw_val within the last 24 hours
  tAvg = dbHandler.session.query(func.avg(Temperature.raw_val)).filter(
      Temperature.date >= time_24_hours_ago,
      Temperature.instrument_id==instrument_id
  ).scalar()

  # pm2p5s
  # Calculate the time 24 hours ago from now
  time_24_hours_ago = datetime.utcnow() - timedelta(hours=24)

  # Perform the query to get the maximum raw_val within the last 24 hours
  pm2p5High = dbHandler.session.query(func.max(Temperature.raw_val)).filter(
      Temperature.date >= time_24_hours_ago,
      Temperature.instrument_id==instrument_id
  ).scalar()

  # Perform the query to get the min raw_val within the last 24 hours
  tLow = dbHandler.session.query(func.min(Temperature.raw_val)).filter(
      Temperature.date >= time_24_hours_ago,
      Temperature.instrument_id==instrument_id
  ).scalar()

  # Perform the query to get the avg raw_val within the last 24 hours
  tAvg = dbHandler.session.query(func.avg(Temperature.raw_val)).filter(
      Temperature.date >= time_24_hours_ago,
      Temperature.instrument_id==instrument_id
  ).scalar()

  # PM2P5S
  # Subquery to calculate the average of pm2p5_cf1 for channels 'a' and 'b' for a specific instrument_id
  current_utc_time = datetime.now(timezone.utc)
  # Calculate the time 24 hours ago from now in UTC
  time_24_hours_ago = current_utc_time - timedelta(hours=24)
  subquery = dbHandler.session.query(
      Particulate.date,
      func.avg(Particulate.pm2p5_cf1).label('avg_pm2p5_cf1')
  ).filter(
      and_(
          Particulate.date >= time_24_hours_ago,
          Particulate.channel.in_(['a', 'b']),
          Particulate.instrument_id == instrument_id
      )
  ).group_by(
      Particulate.date
  ).subquery()

  # Query to get the maximum average value from the subquery
  pm2p5High = dbHandler.session.query(
      func.max(subquery.c.avg_pm2p5_cf1)
  ).scalar()

  # Query to get the maximum average value from the subquery
  pm2p5Low = dbHandler.session.query(
      func.min(subquery.c.avg_pm2p5_cf1)
  ).scalar()

    # Query to get the maximum average value from the subquery
  pm2p5Avg = dbHandler.session.query(
      func.avg(subquery.c.avg_pm2p5_cf1)
  ).scalar()

  personalisation = {
    'first_name': participant.first_name,
    'last_name': participant.last_name, 
    'serial_number': instrument.serial_number,
    'connection_status': 'online' if Instrument.online else 'offline',
    'hHigh': round(float(hHigh), 2),
    'hLow': round(float(hLow), 2),
    'hAvg': round(float(hAvg), 2),
    'tHigh': round(float(tHigh), 2),
    'tLow': round(float(tLow), 2),
    'tAvg': round(float(tAvg), 2),
    'pm2p5High': round(float(pm2p5High), 2),
    'pm2p5Low': round(float(pm2p5Low), 2),
    'pm2p5Avg': round(float(pm2p5Avg), 2),
  }

  email = participant.emails[0].email

  dbHandler.close_session()

  status_code, response = send_email(email=email, personalisation=personalisation)

  # log the email records in the database
  record_email_logs(participant_id, status_code, response)


if __name__=="__main__":
  # DB Handler configs
  from config import DBNAME as dbname
  from config import USER as user
  from config import PASSWORD as password
  from config import HOST as host
  from config import PORT as port

  participant_ids = [1, 3]

  for id in participant_ids:
    try:
      run(participant_id=id)
    except:
       print(f'Could not send email to participant id {id}')