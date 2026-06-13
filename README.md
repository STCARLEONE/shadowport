# 🔥 ShadowPort - Advanced Async Port Scanner

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0%2B-green)](https://riverbankcomputing.com)
[![License](https://img.shields.io/badge/License-MIT-red)](LICENSE)

> A high-performance asynchronous port scanner built for security professionals and network enthusiasts. Scans thousands of ports in seconds with real-time results, service detection, and banner grabbing.

![Screenshot](screenshots/app-preview.png)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ⚡ **Asyncio Concurrent** | Scan 1000+ ports in under 2 seconds |
| 🎯 **Service Detection** | Auto-identify 17+ common services |
| 📡 **Banner Grabbing** | Retrieve service banners from open ports |
| 📊 **Real-time Results** | Live table updates as ports are found |
| 📁 **Multi-format Export** | Save results as JSON, CSV, or TXT |
| 🎨 **Dark Hacker Theme** | Eye-friendly terminal-inspired UI |
| ⚙️ **Configurable** | Custom port ranges, timeouts, workers |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/stcarleone/shadowport.git
cd shadowport

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

---

## 📖 Usage

1. **Enter Target**: IP address or hostname (e.g., `scanme.nmap.org`)
2. **Set Port Range**: `1-1000` or `80,443,8080`
3. **Configure**: Adjust timeout, workers, and banner grabbing
4. **Click START**: Watch real-time results appear in the table
5. **Export**: Save findings as JSON, CSV, or TXT

---

## 🛠️ Development

### Project Structure

```
shadowport/
├── src/
│   └── main.py              # Main application
├── screenshots/
│   └── app-preview.png      # App screenshots
├── docs/
│   └── USAGE.md             # Detailed usage guide
├── tests/
│   └── test_scanner.py      # Unit tests
├── requirements.txt         # Dependencies
├── LICENSE                  # MIT License
└── README.md                # This file
```

---

## ⚠️ Legal Disclaimer

This tool is intended for **authorized security testing only**. Always obtain proper permission before scanning any network or system you do not own. The developer assumes no liability for misuse.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**stcarleone**

- GitHub: [@stcarleone](https://github.com/stcarleone)
- Created: 2026

---

## 🙏 Acknowledgments

- [PyQt6](https://riverbankcomputing.com/software/pyqt) - GUI Framework
- [matplotlib](https://matplotlib.org) - Visualization
- [asyncio](https://docs.python.org/3/library/asyncio.html) - Async I/O
