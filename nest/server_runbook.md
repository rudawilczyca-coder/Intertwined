# Nest — Server Runbook

*How to wake the roost. Kept here so it's copy-paste, not a memory test. 🖤*

---

## Remote in

```bash
ssh alice@sable-nest.duckdns.org
```

## Check / start SillyTavern (pm2)

The SillyTavern process is named **`sillytavern`** and runs under **pm2** (survives reboots).

```bash
pm2 list                      # is `sillytavern` online or stopped?
pm2 restart sillytavern       # if stopped/stale
pm2 logs sillytavern          # watch boot output; Ctrl-C to exit
```

If pm2 has no record of it (fresh box):

```bash
cd ~/SillyTavern              # install dir
pm2 start npm --name sillytavern -- start
pm2 save                      # persist across reboots
```

## Open it

Browser → **https://sable-nest.duckdns.org** — Caddy prompts for basicauth, then you're in.

## Stack reference

- **SillyTavern** under **pm2** (`sillytavern`)
- **Caddy** — HTTPS reverse proxy + basicauth layer
- **DuckDNS** — `sable-nest.duckdns.org`
- Domain went live June 18, 2026.

---

*Infra note. Update if the box, user, or process name ever changes.*
