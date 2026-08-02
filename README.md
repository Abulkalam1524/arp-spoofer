# ARP Spoofer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux-orange)

A Python-based ARP cache poisoning tool that performs a Man-in-the-Middle (MITM) attack between a target host and its default gateway on a local network, built using [Scapy](https://scapy.net/).

> ⚠️ **For educational and authorized lab use only.** Only run this against devices and networks you own or have explicit permission to test. Unauthorized use against networks you don't control is illegal in most jurisdictions.

## Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Enabling Traffic Forwarding](#enabling-traffic-forwarding-required-for-the-victim-to-keep-internet-access)
- [Verifying the Attack](#verifying-the-attack)
- [Lab Setup](#lab-setup-used-for-testing)
- [Defenses Against ARP Spoofing](#defenses-against-arp-spoofing)
- [Disclaimer](#disclaimer)
- [License](#license)

## How It Works

ARP (Address Resolution Protocol) maps IP addresses to MAC addresses on a local network, but it has no built-in authentication — any device can claim to own any IP address. This tool exploits that by continuously sending forged ARP replies to both the target and the gateway, telling each one that this machine owns the other's IP address. As a result, all traffic between them flows through the attacking machine first.

## Features

- Resolves MAC addresses once at startup (avoids ARP cache flapping caused by re-resolving on every loop iteration)
- Sends fully-formed Ethernet + ARP frames at Layer 2 (`scapy.sendp`) rather than relying on Scapy's Layer 3 guesswork
- Gracefully restores original ARP mappings on exit (`CTRL+C`)
- CLI arguments for target/gateway IPs — no hardcoding required

## Requirements

- Python 3.9+
- Linux (tested on Kali Linux) with root privileges
- IP forwarding enabled and NAT configured on the attacking machine (see below)

## Installation

```bash
git clone https://github.com/Abulkalam1524/arp-spoofer.git
cd arp-spoofer
pip install -r requirements.txt
```

## Usage

```bash
sudo python arp_spoof.py -t <target_ip> -g <gateway_ip>
```

**Example:**

```bash
sudo python arp_spoof.py -t 192.168.1.50 -g 192.168.1.1
```

Press `CTRL+C` to stop — the script will automatically send corrective ARP replies to restore both hosts' ARP tables before exiting.

## Enabling Traffic Forwarding (required for the victim to keep internet access)

By default, poisoning the ARP cache alone will cut off the target's internet access, since traffic now arrives at your machine but goes nowhere. To forward it transparently:

```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o <your_interface> -j MASQUERADE
```

> **Note:** if Docker is installed on the attacking machine, it may set the default `FORWARD` chain policy to `DROP`, silently blocking all forwarded traffic. If ping/traffic still fails after the steps above, check:
> ```bash
> iptables -L -v -n
> ```
> and look for `Chain FORWARD (policy DROP ...)`. If found, fix with:
> ```bash
> iptables -P FORWARD ACCEPT
> ```

## Verifying the Attack

On the target machine, check its ARP table — the gateway's IP should now resolve to the attacker's MAC address:

```bash
arp -a        # Windows
ip neigh      # Linux
```

On the attacking machine, capture traffic to confirm interception:

```bash
sudo tcpdump -i <interface> host <target_ip>
```

## Lab Setup Used for Testing

This was built and tested in an isolated VMware lab environment consisting of a Kali Linux VM (attacker) and a Windows 10 VM (target) on the same VMware NAT network segment.

## Defenses Against ARP Spoofing

- Dynamic ARP Inspection (DAI) on managed switches
- Static ARP entries for critical hosts (gateway, servers)
- ARP monitoring tools (e.g., arpwatch)
- Network segmentation / VLANs
- Preferring HTTPS/TLS everywhere, since encrypted traffic limits what an on-path attacker can actually read even if interception succeeds

## Disclaimer

This tool was built for a personal cybersecurity learning project. The author is not responsible for misuse. Only use on networks and devices you own or are explicitly authorized to test.

## License

MIT License — see [LICENSE](https://github.com/Abulkalam1524/arp-spoofer/blob/main/LICENSE) for details.
