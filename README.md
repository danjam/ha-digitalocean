# DigitalOcean for Home Assistant

Custom Home Assistant integration for DigitalOcean droplet monitoring and control.

## Features

- **Binary sensor**: Droplet online/offline status
- **Sensors**: vCPUs, memory, disk, region, image, IPv4 address, monthly cost
- **Switch**: Power on/off (graceful shutdown)
- **Buttons**: Reboot, power cycle

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Search for "DigitalOcean" and install
3. Restart Home Assistant
4. Add the integration via Settings > Devices & Services

### Manual

Copy `custom_components/ha_digitalocean` to your HA `custom_components` directory.

## Configuration

You'll need a [DigitalOcean API token](https://cloud.digitalocean.com/account/api/tokens) with read and write permissions.

## Entities

Each droplet creates:

| Entity | Type | Description |
|--------|------|-------------|
| Status | Binary sensor | Online/offline |
| Power | Switch | Graceful shutdown / power on |
| Reboot | Button | Reboot droplet |
| Power cycle | Button | Hard power cycle |
| vCPUs | Sensor | Number of vCPUs |
| Memory | Sensor | RAM in MB |
| Disk | Sensor | Disk in GB |
| Region | Sensor | Datacenter region |
| Image | Sensor | OS distribution and version |
| IPv4 | Sensor | Public IPv4 address |
| Monthly cost | Sensor | Price in USD |
