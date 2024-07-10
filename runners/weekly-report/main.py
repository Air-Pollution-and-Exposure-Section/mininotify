#!/usr/bin/env python3
import requests
from typing import Tuple
import base64
from datetime import datetime, timedelta, timezone
import pandas as pd
# import GC Notify keys
from mininotify.config import API_KEY as api_key
from mininotify.config import SHMURB_WEEKLY_REPORT_V1_TEMPLATE_ID as template_id
# import database logins
from mininotify.config import DBNAME as DBNAME
from mininotify.config import USER as USER
from mininotify.config import PASSWORD as PASSWORD
from mininotify.config import HOST as HOST
from mininotify.config import PORT as PORT

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from skynet.database.tables.Emails import Emails
from skynet.database.tables.EmailLogs import EmailLogs
from skynet.database.tables.Participant import Participant
from skynet.database.tables.Responsibility import Responsibility
from skynet.database.tables.Instrument import Instrument
from skynet.database.tables.Study import Study
from skynet.database.tables.Site import Site
from skynet.database.Base import Base
from skynet.database.tables.Location import Location
from skynet.database.tables.PurpleAirKeys import PurpleAirKeys

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

def send_email(email:str, personalisation:dict)->Tuple[str, str]:
  # Define the response header
  headers = {
      'Authorization': f'ApiKey-v1 {api_key}',
      'Content-Type': 'application/json',
      'base_url': 'https://notification.canada.ca'
  }
	# Define the repsonse data
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
	# Instantiate a database handler
	dbHandler = Handler(user=USER, dbname=DBNAME, host=HOST, password=PASSWORD, port=PORT)
	# start a database session
	dbHandler.start_session() 
	# build the new record for the email logs table
	record = EmailLogs(
		date=date,
		participant_id=participant_id,
		status_code=status_code,
		error=error,
		message=message
	)
	# try ot insert the new record
	try:
		dbHandler.session.add(record)
		dbHandler.session.commit()
		print("Email Logs data inserted successfully.")
	# catch an integrity error
	except IntegrityError:
		dbHandler.session.rollback()
		print("Failed to insert Email Logs data due to integrity error.")
	# catch all other errors
	except Exception as e:
		dbHandler.session.rollback()
		print(f"Failed to insert Email Logs data: {e}")
	dbHandler.close_session()

# Function to read the file and encode it in base64
def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        file_content = file.read()
    return base64.b64encode(file_content).decode('utf-8')

def encode_to_base64(content:bytes):
	return base64.b64encode(content).decode('utf-8')

def run(participant_id:int):
	# Intantiate a database handler
	dbHandler = Handler(user=USER, dbname=DBNAME, host=HOST, password=PASSWORD, port=PORT)
	# start a database session
	dbHandler.start_session()
	### Query the SHMURB manifest view ans save it as a CSV file
	query = "select * from shmurb_manifest"
	df = pd.read_sql_query(query, con=dbHandler.engine)
	result_csv = df.to_csv(index=False)
	personalisation = {
		"first_name": "Jonathan",
		"last_name": "Levine",
		"application_file": {
			"file": encode_to_base64(result_csv.encode('utf-8')),
			"filename": "weekly_report.csv",
			"sending_method": "attach"
		}
	}
	participant = dbHandler.session.query(Participant).filter_by(id=participant_id).first()
	email = participant.emails[0].email
	# close the database session
	dbHandler.close_session()
	status_code, response = send_email(email=email, personalisation=personalisation)
	# log the email records in the database
	record_email_logs(participant_id, status_code, response)

def main():
	participant_ids=[1]
	for id in participant_ids:
		run(participant_id=id)

if __name__=="__main__":
  main()