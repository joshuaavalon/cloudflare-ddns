import json
from logging import getLogger
from logging.config import dictConfig
from os import environ
from pathlib import Path
from typing import Optional

from cloudflare_ddns import CloudflareDDNS, Configuration, SiteConfiguration

log_level = environ.get("LOG_LEVEL", "INFO")
dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)-8s] %(name)-12s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "NOTSET",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": True
        },
        "joshuaavalon": {
            "handlers": ["default"],
            "level": log_level,
            "propagate": False
        },
        "__main__": {
            "handlers": ["default"],
            "level": log_level,
            "propagate": False
        }
    }
})

logger = getLogger(__name__)


def main():
    config: Optional[Configuration] = load_from_file()
    if config is None:
        config = load_from_env()
    if config is None:
        logger.error("Fail to any configs")
        return
    CloudflareDDNS(config).update()


def load_from_file() -> Optional[Configuration]:
    config_path = environ.get("CONFIG_PATH")
    if config_path is None:
        logger.debug("CONFIG_PATH is not set")
        return None
    path = Path(config_path)
    if path.is_file():
        with open(path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return Configuration.from_dict(data)
            except (TypeError, ValueError, IOError):
                logger.exception("Fail to load from file")
    else:
        logger.warning(f"{path.absolute()} is not a file")
    return None


def load_from_env() -> Optional[Configuration]:
    try:
        site = SiteConfiguration(
            proxied=environ.get("PROXIED", "").lower() in ("yes", "true", "1"),
            ttl=int(environ.get("TTL")),
            email=environ.get("EMAIL"),
            api_key=environ.get("API_KEY"),
            zone=environ.get("ZONE"),
            domain=environ.get("DOMAIN"),
        )
        return Configuration(config=[site])
    except (TypeError, ValueError):
        logger.exception("Fail to load from environment")
        return None


if __name__ == "__main__":
    main()
