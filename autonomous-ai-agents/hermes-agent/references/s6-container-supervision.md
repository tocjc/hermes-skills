# Hermes s6-overlay Container Supervision

This reference covers the s6-overlay supervision tree inside the Hermes Agent Docker image — adding services, debugging profile gateways, understanding the Architecture B main-program pattern.

## Architecture at a Glance

```
/init                                  ← PID 1 (s6-overlay v3.2.3.0)
├── cont-init.d                        ← oneshot setup, runs as root
│   ├── 01-hermes-setup                ← docker/stage2-hook.sh (UID remap, chown, seed)
│   └── 02-reconcile-profiles          ← regenerates s6 slots from persistent profiles
├── s6-rc.d (static services)
│   ├── main-hermes/run                ← exec sleep infinity (no-op slot)
│   └── dashboard/run                  ← if HERMES_DASHBOARD=1
├── /run/service (s6-svscan watches; tmpfs)
│   ├── gateway-<name>/                ← runtime-registered per-profile gateways
│   └── ...
└── CMD                                ← /opt/hermes/docker/main-wrapper.sh
    └── routes user args
```

## Key Files

| Path | Role |
|---|---|
| `docker/stage2-hook.sh` | UID remap, chown, seed, skills sync. Runs as cont-init.d/01 |
| `docker/cont-init.d/02-reconcile-profiles` | Restores profile gateway slots on every boot |
| `docker/main-wrapper.sh` | CMD. Routes user args, drops to hermes via s6-setuidgid |
| `hermes_cli/service_manager.py` | S6ServiceManager: register/start/stop profile gateways |
| `hermes_cli/container_boot.py` | reconcile_profile_gateways() |

## Why Architecture B

Main hermes runs as the CMD, not as an s6-supervised service, because:
1. cont-init.d scripts don't receive CMD args — can't parse `docker run <image> chat -q "hi"`
2. /run/s6/basedir/bin/halt doesn't propagate exit codes (always exits 143)

## Quick Recipes

```sh
# Verify s6 is PID 1
docker exec <c> sh -c 'cat /proc/1/comm; readlink /proc/1/exe'

# Inspect a profile gateway
docker exec <c> /command/s6-svstat /run/service/gateway-<name>

# Bring a service up/down manually
docker exec <c> /command/s6-svc -u /run/service/gateway-<name>

# Watch the cont-init reconciler log
docker exec <c> tail -n 50 /opt/data/logs/container-boot.log
```

## Pitfalls

- **"/command not found" via docker exec** — use absolute `/command/s6-svstat`; docker exec PATH may not include /command/
- **Profile directory ownership** — cont-init runs as hermes; root-owned profile dirs cause PermissionError. Mitigated by chown sweep every boot.
- **Files written by `docker exec` are root-owned** — either pass `--user hermes` or rely on chown sweep next reboot
- **Gateway starts then immediately exits** — profile likely has no model/auth configured. Run `hermes -p <profile> setup` first
- **Container exits 143** — don't invoke `s6-svscanctl -t` or halt; let the CMD (main-wrapper.sh) exit normally