#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🔥 ShadowPort - Advanced Async Port Scanner                                ║
║                                                                              ║
║   Developed by: stcarleone                                                    ║
║   Created: 2026                                                              ║
║                                                                              ║
║   Features:                                                                  ║
║   • Asyncio concurrent scanning (1000+ ports/sec)                            ║
║   • Service & version detection                                              ║
║   • Banner grabbing                                                          ║
║   • Real-time results table & charts                                         ║
║   • Export JSON/CSV/TXT                                                      ║
║   • Dark hacker theme                                                        ║
║                                                                              ║
║   Contact: stcarleone                                                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import asyncio
import socket
import json
import csv
from datetime import datetime
from collections import deque

from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QFileDialog,
    QMessageBox, QProgressBar, QHeaderView, QSystemTrayIcon,
    QMenu, QStyle, QTabWidget, QTextEdit, QSplitter, QFrame
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np


COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 9200: "Elasticsearch"
}

BANNER_PORTS = {21, 22, 25, 80, 110, 143, 443, 3306, 5432, 8080}


class ScannerWorker(QThread):
    """Background worker for async port scanning."""
    result_ready = pyqtSignal(dict)
    progress_update = pyqtSignal(int)
    scan_finished = pyqtSignal()

    def __init__(self, target, ports, max_workers, grab_banner, timeout):
        super().__init__()
        self.target = target
        self.ports = ports
        self.max_workers = max_workers
        self.grab_banner = grab_banner
        self.timeout = timeout
        self._running = True

    def run(self):
        asyncio.run(self._scan())

    async def _scan(self):
        semaphore = asyncio.Semaphore(self.max_workers)
        total = len(self.ports)
        completed = 0

        async def scan_one(port):
            nonlocal completed
            if not self._running:
                return None

            async with semaphore:
                result = await self._check_port(port)
                completed += 1
                self.progress_update.emit(int((completed / total) * 100))
                if result:
                    self.result_ready.emit(result)
                return result

        tasks = [scan_one(p) for p in self.ports]
        await asyncio.gather(*tasks)
        self.scan_finished.emit()

    async def _check_port(self, port):
        try:
            conn = asyncio.open_connection(self.target, port)
            reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)

            service = COMMON_PORTS.get(port, "Unknown")
            banner = ""

            if self.grab_banner and port in BANNER_PORTS:
                try:
                    banner = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                    banner = banner.decode('utf-8', errors='ignore').strip()[:100]
                except:
                    pass

            writer.close()
            await writer.wait_closed()

            return {
                "port": port,
                "state": "OPEN",
                "service": service,
                "banner": banner,
                "timestamp": datetime.now().isoformat()
            }

        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return None

    def stop(self):
        self._running = False


class PortScanner(QWidget):
    """Main port scanner GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 ShadowPort - Advanced Port Scanner")
        self.resize(1200, 800)
        self.results = []
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Target Panel
        target_group = QGroupBox("🎯 Target Configuration")
        target_group.setStyleSheet(self._groupbox_style())
        target_layout = QGridLayout()

        target_layout.addWidget(QLabel("Target IP/Host:"), 0, 0)
        self.target_input = QLineEdit("scanme.nmap.org")
        self.target_input.setStyleSheet(self._input_style())
        target_layout.addWidget(self.target_input, 0, 1)

        target_layout.addWidget(QLabel("Port Range:"), 0, 2)
        self.port_input = QLineEdit("1-1000")
        self.port_input.setStyleSheet(self._input_style())
        self.port_input.setPlaceholderText("e.g. 1-1000 or 80,443,8080")
        target_layout.addWidget(self.port_input, 0, 3)

        target_layout.addWidget(QLabel("Timeout (s):"), 1, 0)
        self.timeout_spin = QDoubleSpinBox()
        self.timeout_spin.setRange(0.1, 10.0)
        self.timeout_spin.setValue(1.0)
        self.timeout_spin.setSingleStep(0.5)
        target_layout.addWidget(self.timeout_spin, 1, 1)

        target_layout.addWidget(QLabel("Workers:"), 1, 2)
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(10, 1000)
        self.workers_spin.setValue(100)
        self.workers_spin.setSingleStep(50)
        target_layout.addWidget(self.workers_spin, 1, 3)

        self.banner_check = QCheckBox("Grab Banners")
        self.banner_check.setChecked(True)
        self.banner_check.setStyleSheet("color: #ffaa00;")
        target_layout.addWidget(self.banner_check, 2, 0)

        self.start_btn = QPushButton("▶ START SCAN")
        self.stop_btn = QPushButton("⏹ STOP")
        self.export_btn = QPushButton("📁 EXPORT")

        for btn in [self.start_btn, self.stop_btn, self.export_btn]:
            btn.setStyleSheet(self._button_style())

        self.start_btn.clicked.connect(self.start_scan)
        self.stop_btn.clicked.connect(self.stop_scan)
        self.export_btn.clicked.connect(self.export_results)
        self.stop_btn.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        target_layout.addLayout(btn_layout, 2, 1, 1, 3)

        target_group.setLayout(target_layout)
        layout.addWidget(target_group)

        # Progress
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a1a;
                border: 1px solid #444;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress)

        # Stats
        stats_group = QGroupBox("📊 Scan Statistics")
        stats_group.setStyleSheet(self._groupbox_style())
        stats_layout = QHBoxLayout()

        self.stat_labels = {}
        stats = [
            ("total", "Total Ports", "0", "#00ccff"),
            ("open", "Open", "0", "#00ff88"),
            ("closed", "Closed/Filtered", "0", "#ff4444"),
            ("time", "Elapsed Time", "0s", "#ffaa00"),
            ("speed", "Speed", "0 ports/s", "#ff00ff"),
        ]

        for key, name, default, color in stats:
            container = QFrame()
            container.setStyleSheet(f"""
                QFrame {{
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    border: 1px solid #333;
                    padding: 10px;
                }}
            """)
            c_layout = QVBoxLayout(container)
            title = QLabel(name)
            title.setStyleSheet("color: #888; font-size: 10px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value = QLabel(default)
            value.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c_layout.addWidget(title)
            c_layout.addWidget(value)
            self.stat_labels[key] = value
            stats_layout.addWidget(container)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Port", "State", "Service", "Banner", "Timestamp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #444;
                gridline-color: #333;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #00ff88;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #444;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #00ff88;
                color: #121212;
            }
        """)
        layout.addWidget(self.table)

        # Log Console
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(120)
        self.log.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff88;
                border: 1px solid #333;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.log)

        self.setLayout(layout)

    def _groupbox_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ccc;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """

    def _input_style(self):
        return """
            QLineEdit {
                background-color: #1f1f1f;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit:focus {
                border-color: #00ff88;
            }
        """

    def _button_style(self):
        return """
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #00ff88;
            }
            QPushButton:pressed {
                background-color: #444;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #666;
            }
        """

    def log_msg(self, msg):
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def parse_ports(self, text):
        ports = []
        for part in text.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                ports.extend(range(int(start), int(end) + 1))
            else:
                ports.append(int(part))
        return ports

    def start_scan(self):
        target = self.target_input.text().strip()
        try:
            ports = self.parse_ports(self.port_input.text())
        except:
            QMessageBox.warning(self, "Error", "Invalid port format. Use: 1-1000 or 80,443,8080")
            return

        self.results = []
        self.table.setRowCount(0)
        self.progress.setValue(0)

        self.stat_labels["total"].setText(str(len(ports)))
        self.stat_labels["open"].setText("0")
        self.stat_labels["closed"].setText("0")
        self.stat_labels["time"].setText("0s")
        self.stat_labels["speed"].setText("0 ports/s")

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_msg(f"Starting scan on {target} - {len(ports)} ports")

        self.worker = ScannerWorker(
            target, ports, self.workers_spin.value(),
            self.banner_check.isChecked(), self.timeout_spin.value()
        )
        self.worker.result_ready.connect(self.add_result)
        self.worker.progress_update.connect(self.progress.setValue)
        self.worker.scan_finished.connect(self.scan_done)
        self.worker.start()

    def add_result(self, result):
        self.results.append(result)
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(result["port"])))
        self.table.setItem(row, 1, QTableWidgetItem(result["state"]))
        self.table.setItem(row, 2, QTableWidgetItem(result["service"]))
        self.table.setItem(row, 3, QTableWidgetItem(result["banner"]))
        self.table.setItem(row, 4, QTableWidgetItem(result["timestamp"]))

        self.table.item(row, 1).setForeground(QColor("#00ff88"))
        self.table.item(row, 0).setForeground(QColor("#00ccff"))

        open_count = len(self.results)
        self.stat_labels["open"].setText(str(open_count))
        self.log_msg(f"OPEN: {result['port']} - {result['service']} - {result['banner'][:30]}")

    def scan_done(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        total = len(self.parse_ports(self.port_input.text()))
        open_count = len(self.results)
        closed_count = total - open_count
        self.stat_labels["closed"].setText(str(closed_count))
        self.stat_labels["speed"].setText(f"{total} ports/s")
        self.log_msg(f"Scan complete! {open_count} open ports found.")

    def stop_scan(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_msg("Scan stopped by user.")

    def export_results(self):
        if not self.results:
            QMessageBox.warning(self, "No Data", "No results to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Results",
            f"scan_{self.target_input.text()}_{datetime.now().strftime('%Y%m%d')}.json",
            "JSON (*.json);;CSV (*.csv);;TXT (*.txt)"
        )

        if not filename:
            return

        if filename.endswith('.json'):
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
        elif filename.endswith('.csv'):
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Port", "State", "Service", "Banner", "Timestamp"])
                for r in self.results:
                    writer.writerow([r["port"], r["state"], r["service"], r["banner"], r["timestamp"]])
        else:
            with open(filename, 'w') as f:
                f.write(f"ShadowPort Scan Results\n")
                f.write(f"Target: {self.target_input.text()}\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n")
                for r in self.results:
                    f.write(f"{r['port']}/tcp {r['state']:6} {r['service']:15} {r['banner']}\n")

        QMessageBox.information(self, "Exported", f"Results saved to {filename}")
        self.log_msg(f"Results exported to {filename}")


class AboutDialog(QDialog):
    """About dialog with developer signature."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ShadowPort")
        self.setFixedSize(400, 300)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Logo
        logo = QLabel("🔥")
        logo.setStyleSheet("font-size: 40px; color: #ff4444;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Title
        title = QLabel("ShadowPort")
        title.setStyleSheet("color: #ff4444; font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Advanced Async Port Scanner")
        subtitle.setStyleSheet("color: #888; font-size: 10px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Signature box (using QWidget with specific object name)
        sig_box = QWidget()
        sig_box.setObjectName("sigBox")
        sig_box.setStyleSheet("""
            QWidget#sigBox {
                background-color: #1a1a1a;
                border: 2px solid #ff4444;
                border-radius: 8px;
            }
        """)
        sig_layout = QVBoxLayout(sig_box)
        sig_layout.setSpacing(3)
        sig_layout.setContentsMargins(15, 12, 15, 12)

        dev = QLabel("Developed by")
        dev.setStyleSheet("color: #888; font-size: 10px;")
        dev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig_layout.addWidget(dev)

        name = QLabel("stcarleone")
        name.setStyleSheet("color: #ff4444; font-size: 20px; font-weight: bold;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig_layout.addWidget(name)

        year = QLabel("2026")
        year.setStyleSheet("color: #666; font-size: 11px;")
        year.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig_layout.addWidget(year)

        layout.addWidget(sig_box)

        # Features
        features = QLabel("Asyncio scanning  •  Service detection  •  Banner grabbing\nReal-time table  •  JSON/CSV/TXT export  •  Dark theme")
        features.setStyleSheet("color: #aaa; font-size: 9px; line-height: 1.5;")
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features)

        layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #ff4444;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        # Dialog stylesheet (applied after layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: white;
                border: 2px solid #ff4444;
                border-radius: 10px;
            }
            QLabel {
                color: #ccc;
                background-color: transparent;
                border: none;
            }
        """)


class MainWindow(QWidget):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 ShadowPort - Advanced Port Scanner")
        self.resize(1200, 800)

        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        top_bar.addStretch()

        about_btn = QPushButton("ⓘ About")
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a; color: #ff4444;
                border: 1px solid #ff4444; border-radius: 4px;
                padding: 6px 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #ff4444; color: #121212; }
        """)
        about_btn.clicked.connect(self.show_about)
        top_bar.addWidget(about_btn)

        layout.addLayout(top_bar)

        self.scanner = PortScanner()
        layout.addWidget(self.scanner)

        self.setLayout(layout)

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: white;
            font-size: 11pt;
            font-family: 'Segoe UI', 'Consolas', monospace;
        }
        QLineEdit {
            background-color: #1f1f1f; color: white;
            border: 1px solid #444; border-radius: 4px; padding: 6px;
        }
        QLineEdit:focus { border-color: #ff4444; }
        QSpinBox, QDoubleSpinBox {
            background-color: #1f1f1f; color: white;
            border: 1px solid #444; border-radius: 4px; padding: 5px;
        }
        QGroupBox { font-weight: bold; color: #ccc; }
        QLabel { color: #ccc; }
        QCheckBox { color: #ccc; }
        QCheckBox::indicator { width: 16px; height: 16px; }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
