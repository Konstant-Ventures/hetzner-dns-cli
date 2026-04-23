"""Command-line interface for Hetzner Cloud DNS."""

import argparse
import sys

from hetzner_dns.client import HetznerConfigError, HetznerAPIError, HetznerDNSClient


def cmd_list(args):
    """List all DNS records for a zone."""
    client = HetznerDNSClient()
    zone = client.get_zone(args.domain)
    records = client.list_records(zone["id"])

    if not records:
        print("No records found.")
        return 0

    print(f"\nZone: {zone['name']} (ID: {zone['id']})")
    print(f"{'Name':<30} {'Type':<8} {'TTL':<8} {'Value(s)'}")
    print("-" * 80)

    for r in records:
        name = r.get("name", "")
        rtype = r.get("type", "")
        ttl = r.get("ttl") or "-"
        values = ", ".join([rec["value"] for rec in r.get("records", [])])
        print(f"{name:<30} {rtype:<8} {ttl:<8} {values}")

    print()
    return 0


def cmd_add(args):
    """Add or update a DNS record."""
    client = HetznerDNSClient()
    zone = client.get_zone(args.domain)

    # Check if record already exists
    existing = client.get_record(zone["id"], args.name, args.type)
    if existing:
        old_values = [r["value"] for r in existing.get("records", [])]
        print(f"Updating existing record: {args.name} {args.type} (was: {', '.join(old_values)})")
    else:
        print(f"Creating new record: {args.name} {args.type}")

    client.update_record(zone["id"], args.name, args.type, args.value, args.ttl)
    print(f"  -> {args.value} (TTL: {args.ttl})")
    print("Done.")
    return 0


def cmd_delete(args):
    """Delete a DNS record."""
    client = HetznerDNSClient()
    zone = client.get_zone(args.domain)

    existing = client.get_record(zone["id"], args.name, args.type)
    if not existing:
        print(f"Record not found: {args.name} {args.type}")
        return 1

    old_values = [r["value"] for r in existing.get("records", [])]
    print(f"Deleting: {args.name} {args.type} (was: {', '.join(old_values)})")

    client.delete_record(zone["id"], args.name, args.type)
    print("Done.")
    return 0


def cmd_ensure(args):
    """Idempotent record update — preferred for automation/CI/CD."""
    client = HetznerDNSClient()
    zone = client.get_zone(args.domain)

    existing = client.get_record(zone["id"], args.name, args.type)
    if existing:
        old_values = [r["value"] for r in existing.get("records", [])]
        if args.value in old_values and (existing.get("ttl") or 300) == args.ttl:
            print(f"Record already up-to-date: {args.name} {args.type} -> {args.value}")
            return 0
        print(f"Updating: {args.name} {args.type} (was: {', '.join(old_values)})")
    else:
        print(f"Creating: {args.name} {args.type}")

    client.update_record(zone["id"], args.name, args.type, args.value, args.ttl)
    print(f"  -> {args.value} (TTL: {args.ttl})")
    print("Done.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hetzner-dns",
        description="Manage Hetzner Cloud DNS records",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all records
  hetzner-dns list

  # Add an A record
  hetzner-dns add --name hello --type A --value 104.236.76.53

  # Delete a record
  hetzner-dns delete --name hello --type A

  # Idempotent update (for CI/CD)
  hetzner-dns ensure --name hello --type A --value 104.236.76.53
        """,
    )

    parser.add_argument(
        "--domain",
        default="hectorsanchez.eu",
        help="Domain zone to manage (default: hectorsanchez.eu)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Hetzner Cloud API token (overrides env/file)",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # list
    sub.add_parser("list", help="List all DNS records")

    # add
    add_parser = sub.add_parser("add", help="Add or update a DNS record")
    add_parser.add_argument("--name", required=True, help="Record name (e.g., 'hello' or '@')")
    add_parser.add_argument("--type", required=True, help="Record type (A, AAAA, CNAME, TXT, MX, etc.)")
    add_parser.add_argument("--value", required=True, help="Record value")
    add_parser.add_argument("--ttl", type=int, default=300, help="TTL in seconds (default: 300)")

    # delete
    del_parser = sub.add_parser("delete", help="Delete a DNS record")
    del_parser.add_argument("--name", required=True, help="Record name")
    del_parser.add_argument("--type", required=True, help="Record type")

    # ensure (idempotent)
    ensure_parser = sub.add_parser("ensure", help="Idempotent add/update (for automation)")
    ensure_parser.add_argument("--name", required=True, help="Record name")
    ensure_parser.add_argument("--type", required=True, help="Record type")
    ensure_parser.add_argument("--value", required=True, help="Record value")
    ensure_parser.add_argument("--ttl", type=int, default=300, help="TTL in seconds (default: 300)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "list":
            return cmd_list(args)
        elif args.command == "add":
            return cmd_add(args)
        elif args.command == "delete":
            return cmd_delete(args)
        elif args.command == "ensure":
            return cmd_ensure(args)
        else:
            parser.print_help()
            return 1

    except HetznerConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 2
    except HetznerAPIError as e:
        print(f"API error: {e}", file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
