"""Hetzner Cloud DNS API client."""

import os
from pathlib import Path

import requests

API_BASE = "https://api.hetzner.cloud/v1"


class HetznerConfigError(Exception):
    """Raised when configuration is missing or invalid."""


class HetznerAPIError(Exception):
    """Raised when the Hetzner API returns an error."""


class HetznerDNSClient:
    """Client for the Hetzner Cloud DNS API.

    Usage:
        client = HetznerDNSClient()
        zone = client.get_zone("hectorsanchez.eu")
        client.update_record(zone["id"], "hello", "A", "104.236.76.53")
    """

    def __init__(self, token: str | None = None):
        self.token = token or self._load_token()
        if not self.token:
            raise HetznerConfigError(
                "HETZNER_DNS_TOKEN not found. "
                "Set it as an environment variable or in scripts/.env:\n"
                '  HETZNER_DNS_TOKEN="your-token-here"'
            )

    @staticmethod
    def _load_token() -> str | None:
        """Load token from environment or .env file."""
        token = os.environ.get("HETZNER_DNS_TOKEN")
        if token:
            return token

        # Search for .env in common locations
        search_paths = [
            Path(__file__).parent.parent / ".env",
            Path.cwd() / ".env",
            Path.home() / ".hetzner-dns" / ".env",
        ]

        for env_path in search_paths:
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("HETZNER_DNS_TOKEN="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")

        return None

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs) -> dict | None:
        """Make an API request and handle errors."""
        url = f"{API_BASE}{path}"
        resp = requests.request(method, url, headers=self._headers(), **kwargs)

        if not resp.ok:
            try:
                err = resp.json()
                msg = err.get("error", {}).get("message", resp.text)
            except Exception:
                msg = resp.text
            raise HetznerAPIError(f"API error ({resp.status_code}): {msg}")

        if resp.status_code == 204:
            return None
        return resp.json()

    # ------------------------------------------------------------------
    # Zones
    # ------------------------------------------------------------------

    def list_zones(self) -> list[dict]:
        """List all DNS zones."""
        data = self._request("GET", "/zones")
        return data.get("zones", []) if data else []

    def get_zone(self, name: str) -> dict:
        """Get a zone by domain name."""
        zones = self.list_zones()
        for zone in zones:
            if zone.get("name") == name:
                return zone
        raise HetznerAPIError(f"Zone '{name}' not found.")

    # ------------------------------------------------------------------
    # Records (RRSets)
    # ------------------------------------------------------------------

    def list_records(self, zone_id: str) -> list[dict]:
        """List all record sets (RRSets) in a zone."""
        data = self._request("GET", f"/zones/{zone_id}/rrsets")
        return data.get("rrsets", []) if data else []

    def get_record(self, zone_id: str, name: str, rtype: str) -> dict | None:
        """Get a specific record set by name and type."""
        records = self.list_records(zone_id)
        for rec in records:
            if rec.get("name") == name and rec.get("type") == rtype:
                return rec
        return None

    def update_record(
        self,
        zone_id: str,
        name: str,
        rtype: str,
        value: str,
        ttl: int = 300,
    ) -> dict:
        """Add or update a DNS record.

        If the record already exists, it is replaced with the new value.
        If it does not exist, a new RRSet is created.
        """
        # Check if record exists
        existing = self.get_record(zone_id, name, rtype)

        if existing:
            # Update existing record
            payload = {
                "records": [
                    {
                        "value": value,
                        "ttl": ttl,
                    }
                ]
            }
            return self._request(
                "POST",
                f"/zones/{zone_id}/rrsets/{name}/{rtype}/actions/update_records",
                json=payload,
            )
        else:
            # Create new RRSet
            payload = {
                "name": name,
                "type": rtype,
                "ttl": ttl,
                "records": [
                    {
                        "value": value,
                    }
                ],
            }
            return self._request(
                "POST",
                f"/zones/{zone_id}/rrsets",
                json=payload,
            )

    def delete_record(self, zone_id: str, name: str, rtype: str) -> None:
        """Delete a DNS record (RRSet) entirely."""
        self._request(
            "DELETE",
            f"/zones/{zone_id}/rrsets/{name}/{rtype}",
        )

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------

    def ensure_record(
        self,
        domain: str,
        name: str,
        rtype: str,
        value: str,
        ttl: int = 300,
    ) -> dict:
        """Ensure a DNS record exists with the given value.

        This is the preferred method for deployment scripts — it is idempotent.
        """
        zone = self.get_zone(domain)
        return self.update_record(zone["id"], name, rtype, value, ttl)
