import json
import requests
from sys import argv
from getopt import getopt, GetoptError
from os import getenv


def main() -> None:
    """Executed on CLI command - runs the Dynamic DNS routine.
    """
    conf = get_configs()

    zone_response = call_api(
        'https://api.cloudflare.com/client/v4/zones/', conf['token'])

    main_domain = '.'.join(conf['domain'].split('.')[-2:])
    zone_token = None

    for main_zone in zone_response['result']:
        if main_zone['name'] == main_domain:
            zone_token = main_zone['id']

    if zone_token is None:
        print(
            (
                "The specified domain wasn't found in the returned response "
                "- does the token have clearance to the DNS?"
            )
        )
        exit(4)

    dns_response = call_api(
        "https://api.cloudflare.com/client/v4/zones/%s/dns_records"
        % zone_token, conf['token']
    )

    dns_token = None
    dns_record = None

    for dns_zone in dns_response['result']:
        if dns_zone['name'] == conf['domain']:
            dns_token = dns_zone['id']
            dns_record = dns_zone

    if dns_token is None:
        print(
            (
                "Got a zone token, but couldn't locate the domain. "
                "Is the subdomain correct?"
            )
        )
        exit(4)

    final_reply = set_ip(
        conf['token'],
        zone_token,
        dns_token,
        get_ip(conf['ipv6']),
        dns_record
    )

    print(
        "Success: Your address %s has been changed to the IP %s" %
        (final_reply['result']['name'], final_reply['result']['content'])
    )
    exit(0)


def get_configs() -> dict:
    """Gets the configuration from env. Failing that, it checks for specified
        execution arguments.

    Returns:
            dict: Configuration object.
    """

    conf = {
        'token': getenv("CF_TOKEN", None),
        'domain': getenv("CF_DOMAIN", None),
        'ipv6': getenv("CF_IPV6", False)
    }

    if not all([conf['token'], conf['domain']]):
        try:
            opts, args = getopt(argv[1::], "6d:t:", [
                "ipv6", "domain=", "token="
            ])
        except GetoptError:
            pass

        for opt, arg in opts:
            if opt in ('-6', '--ipv6'):
                conf['ipv6'] = True
            if opt in ('-t', '--token'):
                conf['token'] = arg
            if opt in ('-d', '--domain'):
                conf['domain'] = arg

        if not all([conf['token'], conf['domain']]):
            print(
                (
                    "Please specify a Cloudflare token using -t/--token and "
                    "a domain using -d/--domain."
                    "\n"
                    "Alternatively, specify in the system env using CF_TOKEN "
                    "and CF_DOMAIN."
                    "\n\n"
                    "This tool uses the Clouflare 'API Token', you can get "
                    "one by visiting this URL:"
                    "\n"
                    "https://dash.cloudflare.com/profile/api-tokens"
                    "\n\n"
                    "Ensure the token is given 'Zone.DNS' permissions. This "
                    "is *all that is needed*, so don't give it more."
                )
            )
            exit(2)

    return conf


def call_api(url: str, token: str) -> dict:
    """Calls the Cloudflare API.

    Args:
            url (str): The Cloudflare API URL to ping.
            token (str): _description_

    Returns:
            dict: API response object.
    """

    headers = {
        'Authorization': "Bearer %s" % token,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        print("HTTP error was recieved: %s" % str(response.status_code))
        exit(5)


def set_ip(
        token: str,
        zone_token: str,
        dns_token: str,
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

    request = (
        "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s"
        % (zone_token, dns_token)
    )

    headers = {
        'Authorization': "Bearer %s" % token,
        'Content-Type': 'application/json'
    }

    data = {
        'type': record['type'],
        'name': record['name'],
        'content': new_ip,
        'ttl': 3600,
        'proxied': False
    }

    response = requests.put(request, headers=headers, json=data)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        print(
            "HTTP error was recieved sending the payload: %s"
            % str(response.status_code)
        )

        if response.status_code == 400:
            print(
                str(json.loads(response.content)['errors'][0]['code']) +
                ': ' +
                json.loads(response.content)['errors'][0]['message']
            )
        exit(6)


def get_ip(v6: bool = False) -> str:
    """Gets the public API of the current machine.

    Args:
            v6 (bool, optional): Whether to return an IPv6 address.
            Defaults to False (IPv4).

    Returns:
            str: IP address.
    """

    if v6:
        ip = requests.get('https://6.ident.me/')
    else:
        ip = requests.get('https://4.ident.me/')

    if ip.status_code == 200:
        return ip.text
    else:
        print("Failure retrieving IP address: %s" % str(ip.status_code))
        exit(7)


main()
