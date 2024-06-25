#!/usr/bin/env python3
import requests
import json

# api key
from config import API_KEY as api_key
from config import EMAIL_ADDRESS as email_address
from config import TEMPLATE_ID as template_id

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Numeric

from skynet.database.tables.Emails import Emails
from skynet.database.tables.Participant import Participant

import typing

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

if __name__=="__main__":

  from config import DBNAME as dbname
  from config import USER as user
  from config import PASSWORD as password
  from config import HOST as host
  from config import PORT as port

  dbHandler = Handler(user=user, dbname=dbname, host=host, password=password, port=port)
  dbHandler.start_session()

  participant_id = 1
  email_query = dbHandler.session.query(Emails.email).filter(Emails.participant_id==participant_id).first()
  dbHandler.close_session()
  
  for email in email_query:
    print(email)

  # # Define the headers and data
  # headers = {
  #     'Authorization': f'ApiKey-v1 {api_key}',
  #     'Content-Type': 'application/json',
  #     'base_url': 'https://notification.canada.ca'
  # }

  # data = {
  #     'email_address': email_address,
  #     'template_id': template_id
  # }

  # # Make the POST request
  # response = requests.post(
  #     'https://api.notification.canada.ca/v2/notifications/email',
  #     headers=headers,
  #     data=json.dumps(data)
  # )

  # # Print the response
  # print("status code: ", response.status_code)
  # print("response: ", response.json())