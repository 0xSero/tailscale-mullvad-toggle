# Tailscale Mullvad Toggle

A no-cloud, no-VPS toggle for using [Mullvad exit nodes in Tailscale](https://tailscale.com/docs/features/exit-nodes/mullvad-exit-nodes).

It gives you:

- a dependency-free `ts-mullvad` CLI
- a macOS SwiftBar menu-bar toggle
- setup detection that links you to Tailscale's Mullvad flow if your tailnet does not have Mullvad enabled yet
- a public egress verifier using Mullvad's checker

## Quick Start

```sh
curl -fsSL https://raw.githubusercontent.com/0xSero/tailscale-mullvad-toggle/main/install.sh | bash
```

Then click the SwiftBar menu item or run:

```sh
ts-mullvad doctor
ts-mullvad toggle
ts-mullvad verify
```

## Requirements

- Tailscale installed and signed in
- A tailnet with the Mullvad VPN add-on enabled
- For the menu-bar UI: macOS + SwiftBar

If Mullvad is not enabled yet, `ts-mullvad doctor` and the SwiftBar menu will link you to:

- Tailscale admin setup: <https://login.tailscale.com/admin/settings/general>
- Tailscale docs: <https://tailscale.com/docs/features/exit-nodes/mullvad-exit-nodes>

## Usage

```sh
ts-mullvad list --country any
ts-mullvad on --country US
ts-mullvad on --country DE
ts-mullvad on --city "New York"
ts-mullvad on --no-lan
ts-mullvad off
ts-mullvad status
```

Environment knobs:

```sh
export TS_MULLVAD_COUNTRY=US
export TS_MULLVAD_CITY="New York"
export TS_MULLVAD_NODE=us-nyc-wg-501.mullvad.ts.net
```

## How It Works

The tool reads `tailscale status --json`, finds peers that are Mullvad exit nodes, chooses the best online match for your country/city preference, then calls:

```sh
tailscale set --exit-node=<node> --exit-node-allow-lan-access=true
```

To turn off:

```sh
tailscale set --exit-node=
```

Those flags are documented in the [Tailscale CLI reference](https://tailscale.com/docs/reference/tailscale-cli).

## SwiftBar

The installer places one plugin file in:

```sh
~/Library/Application Support/SwiftBar/Plugins
```

SwiftBar expects executable scripts in its plugin folder. See the [SwiftBar project](https://github.com/swiftbar/SwiftBar).

## Troubleshooting

Run:

```sh
ts-mullvad doctor
```

Common states:

- `Tailscale CLI was not found`: install Tailscale from <https://tailscale.com/download>
- `No Mullvad exit nodes are visible`: enable the Mullvad add-on and grant this device access
- `Mullvad exit nodes exist, but none matched`: use `ts-mullvad list --country any`

## Privacy Note

This project does not run a server and does not need a cloud account. It only talks to:

- your local Tailscale CLI
- Mullvad's public checker when you run `verify`
- Tailscale/Mullvad docs links when you click setup links

## Tests

Run `python3 -m unittest discover -s tests -v`. Tests mock Tailscale commands and do not change network settings.
