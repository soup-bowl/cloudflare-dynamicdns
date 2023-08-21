import json
import requests
from sys import argv
from datetime import datetime
from getopt import getopt, GetoptError
from os import getenv

from cddns.cloudflare import Cloudflare


def main() -> None:
    """Executed on CLI command - runs the Dynamic DNS routine.
    """
    conf = get_configs()
    cf = Cloudflare(conf['token'], conf['domain'])

    zone_token = cf.get_zone_token()
    dns_record = cf.get_records(zone_token)
    final_reply = cf.set_record(
        zone_token,
        get_ip(conf['ipv6']),
        dns_record['token'],
        dns_record['record']
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
