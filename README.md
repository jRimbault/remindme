# remindme

Schedule desktop notifications from the command line.

## Installation

```bash
uv tool install .
```

or

```bash
uv tool install git+https://github.com/jRimbault/remindme.git
```

## Usage

```bash
# Remind me in 30 minutes
remindme in 30m "Take a break"

# Remind me at 3pm today
remindme at 3pm "Meeting with team"

# Remind me tomorrow at 9am
remindme at "2026-01-16 09:00" "Review pull requests"
```

## Backends

**systemd** (recommended): Persistent reminders that survive reboots. Precise timing (~1s). Linux only.

**at**: Portable across Unix systems. Lost on reboot. Good timing (~1min). Requires `atd` service.

**auto**: Automatically selects systemd if available, falls back to at.

```bash
# Use specific backend
remindme --backend systemd in 1h "Check deployment"

# View detailed backend info
remindme --help
```

## Time Formats

**Relative**: `30s`, `5m`, `2h`, `1d`

**Absolute**: `3pm`, `15:00`, `2026-01-16 09:00`

## Development

```bash
# Install dev dependencies
uv sync

# Run checks
uv run ruff format main.py
uv run ruff check main.py
uv run pyright main.py
```
