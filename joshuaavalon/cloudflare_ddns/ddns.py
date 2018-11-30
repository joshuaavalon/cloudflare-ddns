import json
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

from joshuaavalon.cloudflare_ddns.configuration import Configuration, \
    SiteConfiguration
from joshuaavalon.cloudflare_ddns.utils import get_str

logger = getLogger(__name__)
__all__ = ["CloudflareDDNS"]


class CloudflareDDNS:
    def __init__(self, config: Configuration):
        self.config = config

    def update(self):
        logger.info(f"Start DDNS Update")
        for config in self.config.config:
            self.update_site(config)

    def update_site(self, config: SiteConfiguration):
        logger.info(f"Start update for {config.domain}")
        ip = config.ip
        if ip is None:
            logger.debug("ip is not set in config")
            ip = self.get_ip()
        logger.debug(f"ip: {ip}")
        if ip is None:
            logger.error("Ip cannot be found")
            return

        zone_id = self.get_zone_id(config)
        if zone_id is None:
            logger.error("Fail to get zone id")
            return
        logger.debug(f"zone_id: {zone_id}")

        record = self.get_record(zone_id, config)
        if record is None:
            logger.error("Fail to get dns record")
            return
        record_id = get_str(record, "id")
        logger.debug(f"record_id: {record_id}")
        prev_ip = get_str(record, "content")
        if prev_ip == ip:
            logger.info("Ip does not change, skipping")
            return

        success = self.update_record(zone_id, record_id, ip, config)

        if success:
            logger.info("Update success")
        else:
            logger.info("Update fail")

    def get_ip(self) -> Optional[str]:
        ip_echo = self.config.ip_echo
        logger.debug("Get ip from outside")
        for echo in ip_echo:
            try:
                response = requests.get(echo)
                if response.status_code == 200:
                    ip = response.text
                    logger.info(f"Get {ip} from {echo}")
                    return ip
                logger.info(f"Fail to get ip from {echo}")
            except IOError:
                logger.exception("IOError in get_ip")
                continue
        return None

    def get_zone_id(self, config: SiteConfiguration) -> Optional[str]:
        zone = config.zone
        logger.debug(f"zone: {zone}")
        try:
            response = requests.get(
                urljoin(self.config.api_url, "zones"),
                headers=self.headers(config),
                params={"name": zone}
            )
            if not is_response_success(response):
                return None
            data: Dict[str, Any] = response.json()
            results = data.get("result", [])
            if len(results) != 1:
                print(f"Your zone return {len(results)} results.")
                return None
            return get_str(results[0], "id")
        except IOError:
            logger.exception("IOError in get_zone_id")
            return None

    def get_record(self, zone_id: str,
                   config: SiteConfiguration) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                urljoin(self.config.api_url, f"zones/{zone_id}/dns_records"),
                headers=self.headers(config),
                params={"name": config.domain}
            )
            if not is_response_success(response):
                return None
            data: Dict[str, Any] = response.json()
            results = data.get("result", [])
            # Get A record only
            results = [result for result in results if
                       result.get("type") == "A"]
            if len(results) != 1:
                print(f"{config.domain} have {len(results)} A record(s).")
                return None
            return results[0]
        except IOError:
            logger.exception("IOError in get_ip")
            return None

    def update_record(self,
                      zone_id: str,
                      record_id: str,
                      ip: str,
                      config: SiteConfiguration) -> bool:
        try:

            response = requests.put(
                urljoin(self.config.api_url,
                        f"zones/{zone_id}/dns_records/{record_id}"),
                headers=self.headers(config),
                json={
                    "type": "A",
                    "name": config.domain,
                    "content": ip,
                    "ttl": config.ttl,
                    "proxied": config.proxied
                }
            )
            return is_response_success(response)
        except IOError:
            logger.exception("IOError in update_record")
            return False

    def url(self, path: str) -> str:
        return urljoin(self.config.api_url, path)

    @staticmethod
    def from_file(path: Path) -> "CloudflareDDNS":
        # noinspection PyTypeChecker
        with open(path, "r", encoding="utf-8") as file:
            config = json.load(file)
        return CloudflareDDNS(config)

    @staticmethod
    def headers(config: SiteConfiguration) -> Dict[str, Any]:
        logger.debug(f"email: {config.email}")
        return {
            "X-Auth-Email": config.email,
            "X-Auth-Key": config.api_key,
            "Content-Type": "application/json"
        }


def is_response_success(response: requests.Response) -> bool:
    if not response.ok:
        return False
    try:
        data: Dict[str, Any] = response.json()
        if not data.get("success"):
            logger.error(
                json.dumps(data.get("errors"), ensure_ascii=False, indent=2)
            )
            return False
        return True
    except ValueError:
        logger.exception("ValueError in is_response_success")
        return False
