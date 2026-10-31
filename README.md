# Minecraft server player logger

Pings a Minecraft server every 10 minutes using GitHub Actions and appends the result to `logs/player_log.csv`, which is committed back to the repo.

## Setup

1. Create a new GitHub repo and push these files (`ping.py`, `requirements.txt`, `.github/workflows/ping.yml`, this README).
2. Go to **Settings > Secrets and variables > Actions > Variables** and add:
   - `MC_HOST`: your server address, e.g. `play.example.com` or `play.example.com:25565`
   - `MC_EDITION` (optional): `java` (default) or `bedrock`
3. Go to **Settings > Actions > General > Workflow permissions** and choose **Read and write permissions**.
4. Open the **Actions** tab, pick *Ping Minecraft server* and click **Run workflow** to test it. After that it runs on its own.

## Log columns

| Column | Meaning |
|---|---|
| `timestamp_utc` | When the ping happened |
| `online` | 1 if the server answered, 0 if not |
| `players_online` / `players_max` | Current and maximum player count |
| `latency_ms` | Round trip time to the server |
| `version` | Server version string |
| `motd` | Message of the day |
| `player_sample` | Some player names, `;` separated (many servers hide or truncate this) |
| `error` | Reason for failure when `online` is 0 |

## Things to know

- GitHub's scheduler is best effort. Runs can be delayed or skipped during busy periods, so expect gaps and drift of a few minutes. Cron is in UTC.
- Scheduled workflows are disabled automatically on public repos after 60 days without repo activity. The log commits count as activity, so it should keep itself alive, but check if it ever stops.
- Each run adds one commit, which is about 4,300 a month. If that bothers you, change the log step to push to a separate `data` branch.
- The server must be reachable from the public internet. A LAN-only or firewalled server will just log as offline.
- To run locally: `pip install -r requirements.txt && MC_HOST=your.server.address python ping.py`

## Other cloud options

The script is plain Python configured by environment variables, so it also works as a cron job on any VPS, a Render or Railway cron service, or a scheduled Cloudflare/Lambda function. Swap the CSV writer for a database insert if you need persistent storage there, since those filesystems are usually temporary.