"""Hetzner Cloud DNS CLI package."""

__version__ = "1.0.0"

from hetzner_dns.client import HetznerDNSClient, HetznerAPIError, HetznerConfigError

__all__ = ["HetznerDNSClient", "HetznerAPIError", "HetznerConfigError"]
