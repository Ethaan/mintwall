# Mintwall deploy checklist

Steps to run when putting the server on a public host. The tooling for each is already built and tested
(see the notes); this is the "do it at deploy" list. Fuller background is in `docs/production-plan.md`.

## Before anyone can connect (security)

- [ ] **Clean the database and set real credentials from `.env`.** Server stopped, backup first.
      `tools/provision-from-env.py` reads `.env` (gitignored): removes the test accounts, sets the God
      account password, creates the main account. See `.env.example` for the keys. Also handled locally as
      tasks 1/2/3 in task.md.
- [ ] **Confirm the quest-testing account 8 is gone** and `server/config.local.lua` is never deployed
      (its InfiniteItemPlayers names; gitignored).
- [ ] **Check a real password types in the client.** Create an account with `tools/create-account.py`
      (or the `.env` main account) and log in with the 7.4 client to confirm the password length is accepted.
- [ ] **(Optional) TLS.** 7.4 sends passwords unencrypted. Players are already warned in the MOTD/login
      message. To encrypt: hook the client's Winsock calls in `mintwall.dll` (SChannel) with a TLS terminator
      in front of the server (stunnel locally, an AWS NLB TLS listener in production). Spike first: does hooking
      the 7.4 client's connect/send/recv from the DLL work, and what latency does it add?

## Hosting

- [ ] **Public IP + patched client.** Patch the client for players with `tools/patch-client.ps1 -Ip <public ip>`
      (also applies the www.mintwalling.com text patch). Distribute `Tibia-mintwall.exe`.

## Run as a service / auto-restart

- [ ] **Windows:** `tools/install-service.ps1` (NSSM). Run the `-DryRun` first, then install elevated.
      Restarts on exit 10 (daily server save) and on crash (with back-off).
- [ ] **Linux (AWS host):** `deploy/mintwall.service` (systemd). Needs a Linux build of the server.
- [ ] Set `ServerSaveEnabled = true` only once a supervisor is in place (otherwise the daily save leaves the
      server down). Pick `ServerSaveHour` (currently 6, server local time; a UTC host needs 8 for 09:00 CET).

## Backups

- [ ] **Schedule `tools/backup-db.py`** (hourly). It takes a consistent online snapshot while the server runs,
      keeps 48 hourly / 14 daily, and can upload to S3 via `--upload-cmd` / `MINTWALL_BACKUP_UPLOAD`.
      A Windows scheduled-task and a cron example are in `docs/production-plan.md` §3b.
- [ ] **Restore drill:** follow the 6-step checklist in `docs/production-plan.md` §3b with `tools/restore-db.py`.
- [ ] Daily EBS snapshot of the volume (AWS).

## Observability (at deploy)

- [ ] CloudWatch agent for the logs and host metrics.
- [ ] A status-protocol health check against the game port.
- [ ] Alarms to Slack: server down, backup older than 2 h, crash-loop (the service stops after 5 crashes in
      15 min), disk full.

## Infra

- [ ] Terraform for the AWS host, security group (game port + SSH), the EBS volume and the S3 backup bucket
      (see `docs/production-plan.md`).
