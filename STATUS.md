# STATUS — hetzner-dns-cli

## Current State
- Workspace created following workspace-control-plane standards
- Package structure set up with `pyproject.toml` for pip installation
- Source code migrated from `infrastructure-management/scripts/hetzner_dns/` to standalone package
- Uses new Hetzner Cloud API (`api.hetzner.cloud/v1`)
- Console script entry point configured: `hetzner-dns`

## Blockers / Questions
- **GitHub repo:** Needs to be created under `konstant-ventures` org and code pushed
- **PyPI:** Not published yet — install only from GitHub
- **Tests:** No automated tests yet

## Next Steps
1. **Create GitHub repo** under `konstant-ventures/hetzner-dns-cli`
2. **Push code** to main branch
3. **Add tests** for client.py and cli.py
4. **Set up GitHub Actions** for CI
5. **Publish to PyPI** (optional — GitHub install works fine)

## Notes
- The old `dns.hetzner.com` API is deprecated (shuts down May 2026). This tool uses the new Cloud API.
- Token location: `HETZNER_DNS_TOKEN` env var or `.env` file
- Default zone: `hectorsanchez.eu` (configurable via `--domain`)

---

*Last updated: 2026-04-23*
