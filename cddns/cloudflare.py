import json
import requests
from datetime import datetime


class Cloudflare:
	def __init__(self, token, domain):
		self.token = token
		self.domain = domain
		self.base_url = "https://api.cloudflare.com/client/v4/"


	def get_zone_token(self):
		zone_response = self._get(f"{self.base_url}/zones/")
		main_domain = '.'.join(self.domain.split('.')[-2:])
		zone_token = None

		for main_zone in zone_response['result']:
			if main_zone['name'] == main_domain:
				zone_token = main_zone['id']
		
		if zone_token is None:
			raise Exception(
				(
					"The specified domain wasn't found in the returned response "
					"- does the token have clearance to the DNS?"
				)
			)
		
		return zone_token


	def get_records(self, zone_token:str):
		dns_response = self._get(f"{self.base_url}/zones/{zone_token}/dns_records")

		dns_token = None
		dns_record = None

		for dns_zone in dns_response['result']:
			if dns_zone['name'] == self.domain:
				dns_token = dns_zone['id']
				dns_record = dns_zone

		if dns_token is None:
			raise Exception(
				(
					"Got a zone token, but couldn't locate the domain. "
					"Is the subdomain correct?"
				)
			)
		
		return {
			'token': dns_token,
			'record': dns_record
		}


	def set_record(
		self,
		zone_token: str,
		new_ip: str,
		record: dict
	) -> dict:
		"""Calls the DNS zone set API, and provides the returning object.

		Args:
				token (str): API token.
				zone_token (str): Zone token from v4/zones.
				dns_token (str): Record token from v4/zones/<>/dns_records.
				new_ip (str): What the value is to be changed to.
				record (dict): Record object from the Cloudflare dns_records API.

		Returns:
				dict: _description_
		"""

		data = {
			'type': record['record']['type'],
			'name': record['record']['name'],
			'content': new_ip,
			'comment': "Automatic by DDNS - Set %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
			'ttl': 3600,
			'proxied': False
		}

		response = self._put(f"{self.base_url}/zones/{zone_token}/dns_records/{record['token']}", data)

		return response


	def _get(self, url: str) -> dict:
		"""Calls the Cloudflare API.

		Args:
				url (str): The Cloudflare API URL to ping.

		Returns:
				dict: API response object.
		"""

		headers = {
			'Authorization': f"Bearer {self.token}",
			'Content-Type': 'application/json'
		}

		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			return json.loads(response.content)
		else:
			deeperr = ''
			if response.status_code == 400:
				deeperr = "\nDetails (%s): %s (is your token correct?)" % \
				(str(json.loads(response.content)['errors'][0]['code']),
     			json.loads(response.content)['errors'][0]['message'])

			error_message = f"HTTP error was received: {response.status_code} {deeperr}"
			raise Exception(error_message)
	
	def _put(self, url, data):
		headers = {
			'Authorization': f"Bearer {self.token}",
			'Content-Type': 'application/json'
		}

		response = requests.put(url, headers=headers, json=data)

		if response.status_code == 200:
			return json.loads(response.content)
		else:
			deeperr = ''
			if response.status_code == 400:
				deeperr = "\nDetails (%s): %s" % \
				(str(json.loads(response.content)['errors'][0]['code']),
     			json.loads(response.content)['errors'][0]['message'])

			error_message = f"HTTP error was recieved sending the payload: {response.status_code} {deeperr}"
			raise Exception(error_message)
