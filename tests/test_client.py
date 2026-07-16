from hetzner_dns.client import HetznerDNSClient


def test_list_records_reads_every_page() -> None:
    client = object.__new__(HetznerDNSClient)
    calls: list[dict] = []

    def request(method: str, path: str, **kwargs):
        calls.append({"method": method, "path": path, **kwargs})
        page = kwargs["params"]["page"]
        return {
            "rrsets": [{"name": f"record-{page}", "type": "A"}],
            "meta": {"pagination": {"last_page": 2}},
        }

    client._request = request  # type: ignore[method-assign]

    assert [record["name"] for record in client.list_records("zone-1")] == [
        "record-1",
        "record-2",
    ]
    assert [call["params"] for call in calls] == [
        {"page": 1, "per_page": 100},
        {"page": 2, "per_page": 100},
    ]
