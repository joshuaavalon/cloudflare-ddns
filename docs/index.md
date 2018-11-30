# Getting Started

Cloudflare DDNS is a Python program that provides DDNS for Cloudflare via Cloudflare API v4.

## Requirement

* Python 3.7+ / Docker

## Usage
### Using Docker

### Run directly
1. Clone the git repository
```
git clone https://github.com/joshuaavalon/cloudflare-ddns.git
```

2. Setup up your [configuration](#configuration).

3. Run `run.py`
```
python run.py
```

## Configuration

There are two ways to configure: environment variables and JSON.

### Using environment variables

You use environment variables if you want a quick setup and run only 1 DDNS.

* `EMAIL` - *require*: Email of your Cloudflare account (E.g. `foo@bar.com`)
* `API_KEY` - *require*: API key of your Cloudflare account (E.g. `abcdefg123456`)
* `ZONE` - *require*: Root domain of domain that you want to change (E.g. `bar.com`)
* `DOMAIN` - *require*:  Domain that you want to change (E.g. `foo.bar.com`)
* `TTL`:  TTL of the DNS record (default: `1` which is automatic)
* `PROXIED`:  Enable Cloudflare proxy for the DNS record (default: `true`)

### Using JSON configuration file

You use JSON configuration for a more security or multiple DDNS.

* `CONFIG_PATH` - *require*: Location of the configuration file.

**Example configuration**
```json
{
  "api_url": "https://api.cloudflare.com/client/v4/",
  "ip_echo": [
    "https://ipecho.net/plain",
    "https://icanhazip.com/",
    "https://tnx.nl/ip",
    "http://whatismyip.akamai.com/"
  ],
  "config": [
    {
      "email": null,
      "api_key": null,
      "zone": null,
      "domain": null,
      "ip": null,
      "proxied": true,
      "ttl": 1
    }
  ]
}
```

* `api_url` - API endpoint. (Default: See the example above)
* `ip_echo` - Endpoint for ip address echoing  if `ip` is not set. (Default: See the example above)
* `config` - Configuration for each DDNS.
    * `email` - *require*: Email of your Cloudflare account (E.g. `foo@bar.com`)
    * `api_key` - *require*: API key of your Cloudflare account (E.g. `abcdefg123456`)
    * `zone` - *require*: Root domain of domain that you want to change (E.g. `bar.com`)
    * `domain` - *require*:  Domain that you want to change (E.g. `foo.bar.com`)
    * `ip` - Hard code ip address instead of ip address echoing. (E.g. `127.0.0.1`)
    * `proxied` - Enable Cloudflare proxy for the DNS record (default: `true`)
    * `ttl` - TTL of the DNS record (default: `1` which is automatic)
