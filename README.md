# hetzner-dns-cli

> Standalone CLI for managing Hetzner Cloud DNS records. Installable as a Python package.

## Taxonomy

- **Domain:** coding
- **Type:** ongoing-development
- **Visibility:** professional
- **Lifecycle:** active

## What This Is

A command-line tool and Python library for managing DNS records on Hetzner Cloud.
Built because the old Hetzner DNS Console API (`dns.hetzner.com`) is deprecated and shuts down in May 2026.

This tool uses the **new Hetzner Cloud API** (`api.hetzner.cloud/v1`) and supports:
- Listing DNS zones and records
- Adding, updating, and deleting records
- **Idempotent `ensure` command** — perfect for CI/CD pipelines

## Installation

### From GitHub (recommended)

```bash
pip install git+https://github.com/konstant-ventures/hetzner-dns-cli.git
```

### For Development (editable)

```bash
git clone https://github.com/konstant-ventures/hetzner-dns-cli.git
cd hetzner-dns-cli
pip install -e ".[dev]"
```

### Verify Installation

```bash
hetzner-dns --version
```

## Quick Start

### 1. Get an API Token

1. Go to https://console.hetzner.cloud
2. Select your project → **Security** → **API Tokens**
3. Click **Generate API Token**
4. Copy the token

### 2. Configure Authentication

Set the token as an environment variable:

```bash
export HETZNER_DNS_TOKEN="your-token-here"
```

Or create a `.env` file in your working directory:

```env
HETZNER_DNS_TOKEN="your-token-here"
```

### 3. Use the CLI

```bash
# List all records for a zone
hetzner-dns list

# Add an A record
hetzner-dns add --name hello --type A --value 104.236.76.53

# Update a record (same command, overwrites if exists)
hetzner-dns add --name hello --type A --value 104.236.76.53

# Delete a record
hetzner-dns delete --name hello --type A

# Verify deletion
hetzner-dns list

# Add it back
hetzner-dns add --name hello --type A --value 104.236.76.53

# Idempotent ensure (won't touch if already correct — best for automation)
hetzner-dns ensure --name hello --type A --value 104.236.76.53
```

## Usage as a Library

```python
from hetzner_dns import HetznerDNSClient

client = HetznerDNSClient()
zone = client.get_zone("hectorsanchez.eu")

# List records
records = client.list_records(zone["id"])

# Ensure a record exists (idempotent)
client.ensure_record(
    domain="hectorsanchez.eu",
    name="myapp",
    rtype="A",
    value="104.236.76.53",
    ttl=300,
)
```

## CI/CD Integration

Add DNS provisioning to your deployment pipeline:

```bash
# After deploying your app, ensure DNS is set
hetzner-dns ensure \
  --name myapp \
  --type A \
  --value $(cat /tmp/server-ip.txt)
```

## Commands

| Command | Purpose | Idempotent? |
|---------|---------|-------------|
| `list` | Show all records in the zone | — |
| `add` | Add or overwrite a record | No |
| `delete` | Remove a record | No |
| `ensure` | Add/update only if changed | **Yes** |

## Configuration

The CLI looks for your API token in this order:

1. `--token` flag
2. `HETZNER_DNS_TOKEN` environment variable
3. `.env` file in current directory
4. `~/.hetzner-dns/.env` file

## Requirements

- Python 3.10+
- `requests`

## Project Structure

```
hetzner-dns-cli/
├── src/
│   └── hetzner_dns/
│       ├── __init__.py      # Package exports
│       ├── client.py        # Reusable API client
│       └── cli.py           # CLI commands
├── pyproject.toml           # Package metadata & dependencies
├── README.md
├── LICENSE
└── ...
```

## Status & Tasks

- Current state: [STATUS.md](STATUS.md)
- Task list: [TODO.md](TODO.md)

---

*Created: 2026-04-23*  
*Maintained by: Konstant Ventures*
