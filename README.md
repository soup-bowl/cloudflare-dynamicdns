# Cloudflare Dynamic DNS

[![](https://img.shields.io/docker/pulls/soupbowl/cf-dynamicdns?logo=docker&logoColor=white)](https://hub.docker.com/r/soupbowl/cf-dynamicdns)
[![CodeFactor](https://www.codefactor.io/repository/github/soup-bowl/cloudflare-dynamicdns/badge)](https://www.codefactor.io/repository/github/soup-bowl/cloudflare-dynamicdns)
[![Build Container](https://github.com/soup-bowl/cloudflare-dynamicdns/actions/workflows/build.yml/badge.svg)](https://github.com/soup-bowl/cloudflare-dynamicdns/actions/workflows/build.yml)

With a specified Cloudflare DNS API token and a subdomain, this tool will detect your current IP address (using
[ident.me](https://api.ident.me/)) and sets your Cloudflare DNS record to that value. Optionally supports IPv6.

:warning: **ALPHA - NOT PRODUCTION READY**

## Usage

### Docker

Run with arguments:

```bash
docker run ghcr.io/soup-bowl/cf-dynamicdns:edge --domain <your Dynamic DNS domain> --token <Your CF API Token>
```

Run with environments:

```bash
docker run ghcr.io/soup-bowl/cf-dynamicdns:edge --env CF_DOMAIN=<your Dynamic DNS domain> --env CF_TOKEN=<Your CF API Token>
```

Run via Compose:

```yml
services:
  cfdydns:
    image: ghcr.io/soup-bowl/cf-dynamicdns:edge
    environment:
      CF_TOKEN: <token>
      CF_DOMAIN: example.com
```

### Native

```bash
python3 main.py --domain <your Dynamic DNS domain> --token <Your CF API Token>
```

(Arguments can be omitted if you have the values in your environment).

This Python script depends on **Python3** using the **requests** library, which can be installed in the following manners:

Via pip (universal):

```bash
pip install requests
```

Via apt-get (Debian-based):

```bash
sudo apt-get install python3-requests
```

## Getting your Cloudflare Token

Visit the [API Tokens segment of your Cloudflare Profile](https://dash.cloudflare.com/profile/api-tokens). Create an
**API Token** (not an **API Key**), and select to use the Edit Zone DNS template.

How you fill the rest is up to you, but I recommend specifying the **Zone Resource** to **Include**, **Specific zone**,
and specify the domain where your Dynamic DNS will be.

After review, the system will output an **API Token**. This is what the tool wants as either `--token` or `CF_TOKEN`
argument. The `--domain`/`CF_DOMAIN` argument **must match** whatever zone you specified for the token, or at least be
applicable within the scope you set.
