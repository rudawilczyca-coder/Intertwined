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

## RP shim and model roster

The OpenAI-compatible RP shim lives at `~/st-shim/`, binds to
`127.0.0.1:8790`, and runs as the user service `st-shim.service`.

```bash
systemctl --user status st-shim.service
systemctl --user restart st-shim.service
curl -fsS http://127.0.0.1:8790/health
curl -fsS http://127.0.0.1:8790/v1/models
```

`gemini-pro-3.1` maps to Antigravity CLI's `gemini-3.1-pro-high`. This route
does not ask Antigravity to execute canon-search tools in headless mode.
Instead, the shim performs a two-pass exchange: Pro first returns focused RAG
queries; the shim runs the appropriate Intertwined or ATOSAS index locally;
then Pro receives that evidence and writes the final canon-audited reply.

Use this model for general/canon-dense prose, not explicit scenes. Antigravity
currently refuses the explicit-fiction ceiling used in the Model Arena.

---

*Infra note. Update if the box, user, or process name ever changes.*
