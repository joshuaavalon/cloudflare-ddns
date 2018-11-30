from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from joshuaavalon.cloudflare_ddns.utils import enforce_types

__all__ = ["Configuration", "SiteConfiguration"]


def default_ip_echo() -> List[str]:
    return [
        "https://ipecho.net/plain",
        "https://icanhazip.com/",
        "https://tnx.nl/ip",
        "http://whatismyip.akamai.com/"
    ]


@enforce_types
@dataclass
class SiteConfiguration:
    email: str
    api_key: str
    zone: str
    domain: str
    ttl: int = 1
    ip: Optional[str] = None
    proxied: bool = True

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SiteConfiguration":
        return SiteConfiguration(**data)


@enforce_types
@dataclass
class Configuration:
    config: List[SiteConfiguration]
    ip_echo: List[str] = field(default_factory=default_ip_echo)
    api_url: str = "https://api.cloudflare.com/client/v4/"

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Configuration":
        return Configuration(
            api_url=data.get("api_url"),
            ip_echo=data.get("ip_echo"),
            config=[SiteConfiguration.from_dict(data.get("config"))]
        )
