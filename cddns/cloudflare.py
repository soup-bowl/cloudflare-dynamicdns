import json
import requests
from datetime import datetime


class Cloudflare:
	def __init__(self, token, domain):
		"""
		Initialize a Cloudflare API client.

		Args:
			token (str): Cloudflare API token.
			domain (str): The domain for which DNS records are managed.
		"""
		self.token = token
		self.domain = domain
		self.base_url = "https://api.cloudflare.com/client/v4/"
		self.response_type = "application/json"


	def get_zone_token(self):
		"""
		Get the zone token for the specified domain.

		Returns:
			str: Zone token for the domain.
		
		Raises:
			LogicExeption: If the specified domain is not found in the Cloudflare zones.
		"""
		zone_response = self._get(f"{self.base_url}/zones/")
		main_domain = '.'.join(self.domain.split('.')[-2:])
		zone_token = None

		for main_zone in zone_response['result']:
			if main_zone['name'] == main_domain:
				zone_token = main_zone['id']
		
		if zone_token is None:
			raise LogicExeption(
				(
					"The specified domain wasn't found in the returned response "
					"- does the token have clearance to the DNS?"
				)
			)
		
		return zone_token


	def get_records(self, zone_token:str):
		"""
		Get DNS records for the specified zone token.

		Args:
			zone_token (str): Zone token for which to retrieve DNS records.

		Returns:
			dict: Dictionary containing the token and record information.

		Raises:
			LogicExeption: If the domain is not found in the zone's DNS records.
		"""
		dns_response = self._get(f"{self.base_url}/zones/{zone_token}/dns_records")

		dns_token = None
		dns_record = None

		for dns_zone in dns_response['result']:
			if dns_zone['name'] == self.domain:
				dns_token = dns_zone['id']
				dns_record = dns_zone

		if dns_token is None:
			raise LogicExeption(
				(
					"Got a zone token, but couldn't locate the domain. "
					"Is the subdomain correct?"
				)
			)
		
		return {
			'token': dns_token,
			'record': dns_record
		}


	def new_record(self, zone_token: str, domain: str, new_ip: str, is_ipv6: bool = False, proxy: bool = False) -> dict:
		"""
		Creates a new DNS record.

		Args:
			zone_token (str): Zone token for the DNS record.
			domain (str): The domain to assign an IP to.
			new_ip (str): New IP address to set.
			is_ipv6 (bool): Create AAAA instead of A.
			proxy (bool): Proxy through Cloudflare.

		Returns:
			dict: Response from the API after setting the new IP address.
		"""

		data = {
			'type': "AAAA" if is_ipv6 else "A",
			'name': domain,
			'content': new_ip,
			'comment': f"Automatic by DDNS - Set {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
			'ttl': 3600,
			'proxied': proxy
		}

		response = self._post(f"{self.base_url}/zones/{zone_token}/dns_records", data)

		return response


	def update_record(self, zone_token: str, new_ip: str, record: dict) -> dict:
		"""
		Updates the IP address for a DNS record.

		Args:
			zone_token (str): Zone token for the DNS record.
			new_ip (str): New IP address to set.
			record (dict): DNS record object.

		Returns:
			dict: Response from the API after setting the new IP address.
		"""

		data = {
			'type': record['record']['type'],
			'name': record['record']['name'],
			'content': new_ip,
			'comment': f"Automatic by DDNS - Set {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
			'ttl': record['record']['ttl'],
			'proxied': record['record']['proxied']
		}

		response = self._put(f"{self.base_url}/zones/{zone_token}/dns_records/{record['token']}", data)

		return response


	def _get(self, url: str) -> dict:
		"""
		Make a GET request to the Cloudflare API.

		Args:
			url (str): URL to send the GET request.

		Returns:
			dict: API response object.

		Raises:
			CommunicationException: If the API returns an error.
		"""

		headers = {
			'Authorization': f"Bearer {self.token}",
			'Content-Type': self.response_type
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
			raise CommunicationException(error_message)
	
	def _post(self, url, data):
		"""
		Make a POST request to the Cloudflare API.

		Args:
			url (str): URL to send the POST request.
			data: Data to be sent in the request payload.

		Returns:
			dict: API response object.

		Raises:
			CommunicationException: If the API returns an error.
		"""
		headers = {
			'Authorization': f"Bearer {self.token}",
			'Content-Type': self.response_type
		}

		response = requests.post(url, headers=headers, json=data)

		if response.status_code == 200:
			return json.loads(response.content)
		else:
			deeperr = ''
			if response.status_code == 400:
				deeperr = "\nDetails (%s): %s" % \
				(str(json.loads(response.content)['errors'][0]['code']),
	 			json.loads(response.content)['errors'][0]['message'])

			error_message = f"HTTP error was recieved sending the payload: {response.status_code} {deeperr}"
			raise CommunicationException(error_message)
	
	def _put(self, url, data):
		"""
		Make a PUT request to the Cloudflare API.

		Args:
			url (str): URL to send the PUT request.
			data: Data to be sent in the request payload.

		Returns:
			dict: API response object.

		Raises:
			CommunicationException: If the API returns an error.
		"""
		headers = {
			'Authorization': f"Bearer {self.token}",
			'Content-Type': self.response_type
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
			raise CommunicationException(error_message)

class CFDDNSException(Exception):
    pass

class CommunicationException(CFDDNSException):
    pass

class LogicExeption(CFDDNSException):
    pass

class MissingDomainException(LogicExeption):
	pass

class MissingSubdomainException(LogicExeption):
	pass