# Usage Guide

## Quick Start

1. Launch: `python src/main.py`
2. Enter target IP or hostname
3. Set port range (e.g., `1-1000`)
4. Click **START SCAN**

## Port Range Formats

- `1-1000` - Range
- `80,443,8080` - Specific ports
- `1-100,443,8080-8090` - Mixed

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| Timeout | Connection timeout (seconds) | 1.0 |
| Workers | Concurrent connections | 100 |
| Banner Grab | Retrieve service banners | Enabled |

## Export Formats

- **JSON**: Structured data with all fields
- **CSV**: Spreadsheet-compatible format
- **TXT**: Human-readable plain text

## Keyboard Shortcuts

None currently implemented.
