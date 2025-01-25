import requests
from sys import argv, exit
from getopt import getopt, GetoptError
from os import getenv

from cddns.cloudflare import Cloudflare, CommunicationException, LogicExeption


def main() -> None:
    """
    Executed on CLI command - runs the Dynamic DNS routine.
    """

    conf = get_configs()
    cf = Cloudflare(conf['token'], conf['domain'])

    zone_token = None
    dns_record = None
    final_reply = None

    try:
        zone_token = cf.get_zone_token()
        print_debug(f"Fetched zone token {zone_token}", conf['debug'])
    except LogicExeption as e:
        print(f"{string_colour('Error', 'R')}: {e}")
        exit(3)
    except CommunicationException as e:
        print(f"{string_colour('Error', 'R')}: {e}")
        exit(3)
    
    try:
        dns_record = cf.get_records(zone_token)
        print_debug(f"Fetched DNS record ({dns_record['record']['name']}/{dns_record['record']['content']})", conf['debug'])
    except LogicExeption as e:
        print_debug("No record was found. Creating a new one...", conf['debug'])
        try:
            final_reply = cf.new_record(zone_token, conf['domain'], get_ip(conf['ipv6']), conf['ipv6'], conf['proxy'])
            print_debug(f"Created new DNS record ({final_reply['result']['name']}/{final_reply['result']['content']})", conf['debug'])
        except CommunicationException as e:
            print(f"{string_colour('Error', 'R')}: {e}")
            exit(4)
    
    if final_reply is None:
        try:
            final_reply = cf.update_record(zone_token, get_ip(conf['ipv6']), dns_record)
            print_debug(f"Updated DNS record ({final_reply['result']['name']}/{final_reply['result']['content']})", conf['debug'])
        except CommunicationException as e:
            print(f"{string_colour('Error', 'R')}: {e}")
            exit(4)

    print(f"{string_colour('Success', 'G')}: Your address {final_reply['result']['name']} has been changed to the IP {final_reply['result']['content']}")
    exit(0)


def get_configs() -> dict:
    """
    Gets the configuration from env. Failing that, it checks for specified
    execution arguments.

    Returns:
        dict: Configuration object.
    """

    conf = {
        'token': getenv("CF_TOKEN", None),
        'domain': getenv("CF_DOMAIN", None),
        'ipv6': getenv("CF_IPV6", False),
        'proxy': getenv("CF_PROXY", False),
        'debug': False
    }

    if not all([conf['token'], conf['domain']]):
        try:
            opts, _ = getopt(argv[1::], "hvpd:t:", [
                "help", "version", "debug", "ipv6", "domain=", "token=", "proxy"
            ])
        except GetoptError:
            pass

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print_help()
                exit(0)
            if opt in ('-v', '--version'):
                print_version()
                exit(0)
            if opt in ('--debug'):
                conf['debug'] = True
            if opt in ('--ipv6'):
                conf['ipv6'] = True
            if opt in ('-t', '--token'):
                conf['token'] = arg
            if opt in ('-d', '--domain'):
                conf['domain'] = arg
            if opt in ('-p', '--proxy'):
                conf['proxy'] = True

        if not all([conf['token'], conf['domain']]):
            print(f"{string_colour('Error', 'R')}: You're missing either the token, or the version\n")
            print_help()
            exit(2)

    return conf


def get_ip(v6: bool = False) -> str:
    """
    Gets the public API of the current machine.

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
        print(f"{string_colour('Error', 'R')}: Failure retrieving IP address: {str(ip.status_code)}")
        exit(7)

def string_colour(str: str, colour: str) -> str:
    """
    Modifies the input string to use terminal output colour codes.

    Args:
        str (str): The string to be colourised.
        colour (str): The initial of a supported colour.

    Returns:
        str: The coloured string, or the str input if the colour is invalid.
    """

    if colour == "R":
        return f"\033[91m{str}\033[00m"
    if colour == "G":
        return f"\033[92m{str}\033[00m"
    if colour == "B":
        return f"\033[94m{str}\033[00m"
    if colour == "Y":
        return f"\033[93m{str}\033[00m"
    else:
        return str

def pad_string(input_string: str, desired_length: int) -> str:
    """
    Pads the input out with spaces (or truncates if too long).

    Args:
        input_string (str): The string to be modified.
        desired_length (int): The length it should be.

    Returns:
        str: The modified string.
    """

    if len(input_string) >= desired_length:
        return input_string[:desired_length]
    else:
        padding = ' ' * (desired_length - len(input_string))
        return input_string + padding

def print_debug(message: str, debug: bool):
    if debug:
        print(f"{string_colour('Debug', 'B')}: {message}")

def print_help():
    """
    Prints help text to the screen.
    """

    pad = 17

    print("Specify a Cloudflare Access Token and a desired (sub)domain, and the application will assign ", end='')
    print("the record with your IP address.")
    print("")
    print(string_colour('Options:', 'Y'))
    print(f"{string_colour(pad_string('-t, --token', pad), 'G')} Your Cloudflare API token.")
    print(f"{pad_string('', pad)} You can get them from {string_colour('https://dash.cloudflare.com/profile/api-tokens', 'Y')}")
    print(f"{pad_string('', pad)} Assign {string_colour('Zone.DNS', 'Y')} permission to the domain you wish to modify.")
    print(f"{string_colour(pad_string('-d, --domain', pad), 'G')} The FQDN you wish to create/update with the IP address.")
    print(f"{string_colour(pad_string('-p, --proxy', pad), 'G')} Use Cloudflare Proxy for the domain")
    print(f"{pad_string('', pad)} Only impacts record {string_colour('creation', 'Y')}, not {string_colour('update', 'Y')}.")
    print(f"{string_colour(pad_string('    --ipv6', pad), 'G')} Assigns and updates an AAAA record with IPv6 instead.")
    print(f"{pad_string('', pad)} Will crash if the destination record is IPv4, and vice versa.")
    print(f"{string_colour(pad_string('    --debug', pad), 'G')} Enables a verbose output.")
    print("")
    print(f"{string_colour(pad_string('-v, --version', pad), 'G')} Display script version.")
    print(f"{string_colour(pad_string('-h, --help', pad), 'G')} Displays this help information.")

def print_version():
    """
    Prints version text to the screen.
    """

    print("Cloudflare Dynamic DNS (CDDNS) by soup-bowl (code@soupbowl.io) - pre-alpha.")
    print("Source: https://github.com/soup-bowl/cloudflare-dynamicdns/")
