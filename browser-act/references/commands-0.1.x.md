# browser-act CLI Commands (v0.1.x)

Reference snapshot from `browser-act --help`. Note: The upstream SKILL.md claims v2.0.2
but the actual PyPI package is at v0.1.x. This document reflects what's available.

## Global Options

| Option | Description |
|--------|-------------|
| `--session TEXT` | Session name |
| `--intent TEXT` | Caller intent description |
| `--format [text\|json]` | Output format |
| `--no-auto-dialog` | Disable automatic dialog handling |
| `--version` | Show version |
| `-h, --help` | Show help |

## Navigation

| Command | Description |
|---------|-------------|
| `navigate <url>` | Navigate to URL on current page |
| `back` | Go back in history |
| `forward` | Go forward in history |
| `reload` | Reload current page |

## Page State

| Command | Description |
|---------|-------------|
| `state` | Get URL, title, and interactive elements |
| `screenshot [--full-page]` | Take page screenshot |

## Page Interaction

| Command | Description |
|---------|-------------|
| `click <element_index>` | Click element by index |
| `type <text>` | Type text into focused element |
| `input <element_index> <text>` | Click element, then type text |
| `keys <key_sequence>` | Send keyboard keys (Enter, Tab, etc.) |
| `hover <element_index>` | Hover over element |
| `scroll [up\|down\|to\|element\|pixels]` | Scroll page |

## JavaScript

| Command | Description |
|---------|-------------|
| `eval <javascript_code>` | Execute JavaScript and return result |

## Data Extraction (get)

| Command | Description |
|---------|-------------|
| `get links` | Get all links on page |
| `get text` | Get all text content |
| `get html` | Get page HTML |
| `get markdown` | Get markdown version of page |
| `get table <index>` | Get table by index |
| `get form <index>` | Get form fields |
| `get meta` | Get page metadata |

## Browser Management

| Command | Description |
|---------|-------------|
| `browser list` | List configured browsers |
| `browser create [--headless]` | Create new browser |
| `browser switch <name>` | Switch active browser |
| `browser delete <name>` | Delete browser |

## Session Management

| Command | Description |
|---------|-------------|
| `session list` | List sessions |
| `session switch <name>` | Switch session |
| `session delete <name>` | Delete session |

## Tab Management

| Command | Description |
|---------|-------------|
| `tab list` | List open tabs |
| `tab switch <index>` | Switch to tab |
| `tab close <index>` | Close tab |
| `tab new` | Open new tab |

## Wait Conditions

| Command | Description |
|---------|-------------|
| `wait stable [--timeout N]` | Wait for page to be stable |
| `wait --selector <css> --state [attached\|detached\|visible\|hidden]` | Wait for element |
| `wait network` | Wait for network idle |
| `wait <ms>` | Wait N milliseconds |

## Authentication

| Command | Description |
|---------|-------------|
| `auth poll` | Poll for registration status |
| `auth set <API_KEY>` | Set API key |
| `auth status` | Check auth status |
| `auth login <url>` | Login (SSO) |
| `auth logout` | Logout |

## Network Inspection

| Command | Description |
|---------|-------------|
| `network requests [--filter ...]` | List captured requests |
| `network request <id>` | Get request details |
| `network clear` | Clear captured requests |
| `network har start` | Start HAR recording |
| `network har stop` | Stop HAR recording |

## Dialogs

| Command | Description |
|---------|-------------|
| `dialog accept` | Accept alert/confirm/prompt |
| `dialog dismiss` | Dismiss alert/confirm |
| `dialog text <text>` | Set prompt text |

## System

| Command | Description |
|---------|-------------|
| `report-log` | Upload logs to help diagnose issues |
| `feedback` | Send feedback |
