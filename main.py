#!/usr/bin/env python3\
import requests
import json

# api key
from config import API_KEY as api_key
from config import EMAIL_ADDRESS as email_address
from config import TEMPLATE_ID as template_id


if __name__=="__main__":
  # Define the headers and data
  headers = {
      'Authorization': f'ApiKey-v1 {api_key}',
      'Content-Type': 'application/json',
      'base_url': 'https://notification.canada.ca'
  }

  data = {
      'email_address': email_address,
      'template_id': template_id
  }

  # Make the POST request
  response = requests.post(
      'https://api.notification.canada.ca/v2/notifications/email',
      headers=headers,
      data=json.dumps(data)
  )

  # Print the response
  print(response.status_code)
  print(response.json())