import os
import threading
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QProgressBar,
    QTableWidget,
    QLabel,
    QPushButton,
    QHeaderView,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem
)
from PySide6.QtCore import QObject, QThread, Signal
from ProxHendel.GetFreeProxy import FreeProxyUi
from CHECKS.check_proxy import check_user_proxy
from Save.SaveData import save_working_proxy
from PROXTread.TTTH import ProxyCheckerWorker


class AppUi(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PROXY CHECK")
        self.resize(1100, 720)

        self.user_proxies = None
        self.steart = False
        self.proxy_type = None

        self.setup_ui()
        self.apply_style()
        self.set__connections()

    def setup_ui(self):
        # =========================
        # Central Widget
        # =========================
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # =========================
        # Header
        # =========================
        header = QHBoxLayout()

        title = QLabel("ProxY Check")
        title.setObjectName("title")

        version = QLabel("V1.1")
        version.setObjectName("version")

        header.addWidget(title)
        header.addWidget(version)
        header.addStretch()

        main_layout.addLayout(header)

        # =========================
        # Buttons
        # =========================
        button_layout = QHBoxLayout()

        self.impt_button = QPushButton("Import Proxies")
        self.srt_button = QPushButton("Start Checking")
        self.stop_but = QPushButton("Stop Checking")
        self.freeproxy = QPushButton("Get Online Proxies")
        self.save_button = QPushButton("Save Working")      # <-- new button
        self.clr = QPushButton("Clear Proxies")

        self.srt_button.setObjectName("startButton")
        self.stop_but.setObjectName("stopButton")
        self.freeproxy.setObjectName("freeButton")
        self.save_button.setObjectName("saveButton")       # optional style hook

        button_layout.addWidget(self.impt_button)
        button_layout.addWidget(self.srt_button)
        button_layout.addWidget(self.stop_but)
        button_layout.addWidget(self.freeproxy)
        button_layout.addWidget(self.save_button)           # <-- added to layout
        button_layout.addWidget(self.clr)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # =========================
        # Statistics
        # =========================
        stats_layout = QHBoxLayout()

        self.total_card = self.create_card("TOTAL", "0")
        self.working_card = self.create_card("WORKING", "0")
        self.dead_card = self.create_card("DEAD", "0")
        self.success = self.create_card("SUCCESS RATE", "0%")

        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.working_card)
        stats_layout.addWidget(self.dead_card)
        stats_layout.addWidget(self.success)

        main_layout.addLayout(stats_layout)

        # =========================
        # Proxy Table
        # =========================
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Proxy",
            "Status",
            "Response Time",
            "Details"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        main_layout.addWidget(self.table)

        # =========================
        # Progress Bar
        # =========================
        process_layout = QHBoxLayout()

        self.status_label = QLabel("Ready")
        self.process = QProgressBar()
        self.process.setValue(0)

        process_layout.addWidget(self.status_label)
        process_layout.addWidget(self.process)

        main_layout.addLayout(process_layout)

    def create_card(self, name, value):
        frame = QFrame()
        frame.setObjectName("statCard")

        layout = QVBoxLayout(frame)

        label = QLabel(name)
        label.setObjectName("statName")

        value_label = QLabel(value)
        value_label.setObjectName("statValue")

        layout.addWidget(label)
        layout.addWidget(value_label)

        frame.value_label = value_label
        return frame

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d0d0d;
            }

            QWidget {
                color: #eeeeee;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: bold;
            }

            QLabel#version {
                background-color: #222222;
                padding: 5px 10px;
                border-radius: 6px;
                color: #aaaaaa;
            }

            QPushButton {
                background-color: #1c1c1c;
                border: 1px solid #333333;
                border-radius: 7px;
                padding: 10px 18px;
                min-height: 18px;
            }

            QPushButton:hover {
                background-color: #292929;
            }

            QPushButton:pressed {
                background-color: #111111;
            }

            QPushButton#startButton {
                background-color: #eeeeee;
                color: #111111;
                font-weight: bold;
            }

            QPushButton#startButton:hover {
                background-color: #ffffff;
            }

            QPushButton#stopButton {
                color: #ff7777;
            }

            QPushButton#stopButton:hover {
                background-color: #321818;
            }

            QPushButton#freeButton {
                color: #dddddd;
            }

            QPushButton#saveButton {
                color: #7dffb3;
            }

            QPushButton#saveButton:hover {
                background-color: #1a2e22;
            }

            QFrame#statCard {
                background-color: #151515;
                border: 1px solid #292929;
                border-radius: 10px;
            }

            QLabel#statName {
                color: #888888;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#statValue {
                font-size: 24px;
                font-weight: bold;
            }

            QTableWidget {
                background-color: #121212;
                alternate-background-color: #171717;
                border: 1px solid #292929;
                gridline-color: #252525;
                border-radius: 8px;
                selection-background-color: #292929;
                selection-color: #ffffff;
            }

            QTableWidget::item {
                padding: 8px;
            }

            QHeaderView::section {
                background-color: #1b1b1b;
                color: #aaaaaa;
                padding: 10px;
                border: none;
                font-weight: bold;
            }

            QProgressBar {
                background-color: #191919;
                border: none;
                border-radius: 6px;
                height: 12px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #eeeeee;
                border-radius: 6px;
            }
        """)

    def set__connections(self):
        self.impt_button.clicked.connect(self.import_proxy)
        self.stop_but.clicked.connect(self.stop_cheacking)
        self.srt_button.clicked.connect(self.start_cheacking)
        self.freeproxy.clicked.connect(self.get_free_proxy)
        self.save_button.clicked.connect(self.save_working)   # <-- new connection
        self.clr.clicked.connect(self.clearprox)

    def get_free_proxy(self):
        self.proxy_ui = FreeProxyUi()
        if not self.proxy_ui.exec():
            return

        data = getattr(self.proxy_ui, "user_requests", None)
        types = getattr(self.proxy_ui, "proxy_user_type", None)

        self.proxy_type = types

        if not data:
            return

        try:
            proxies = list(dict.fromkeys(data))
            self.table.setRowCount(0)

            for prox in proxies:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(prox))
                self.table.setItem(row, 1, QTableWidgetItem("WAITING"))
                self.table.setItem(row, 2, QTableWidgetItem("-"))
                self.table.setItem(row, 3, QTableWidgetItem("Not checked"))

            self.total_card.value_label.setText(str(len(proxies)))
            self.working_card.value_label.setText("0")
            self.dead_card.value_label.setText("0")
            self.success.value_label.setText("0%")

            self.process.setValue(0)
            self.status_label.setText(f"{len(proxies)} proxies loaded")

        except Exception as e:
            print(f"Error {e}")

    def stop_cheacking(self):
        if hasattr(self, "stop_event"):
            self.stop_event.set()

        self.steart = False
        self.status_label.setText("Stopping...")
        self.srt_button.setEnabled(False)
        self.stop_but.setEnabled(False)

    def start_cheacking(self):
        if self.table.rowCount() == 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("No Proxies")
            msg.setText("Please import proxies first.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                }
                QMessageBox QLabel {
                    color: #ffffff;
                    font-size: 14px;
                }
                QMessageBox QPushButton {
                    background-color: #252525;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 6px;
                    padding: 8px 22px;
                    min-width: 60px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #333333;
                }
            """)
            msg.exec()
            return

        self.steart = True
        self.status_label.setText("Checking started...")
        self.srt_button.setEnabled(False)
        self.stop_but.setEnabled(True)

        proxies = []
        for row in range(self.table.rowCount()):
            prox_item = self.table.item(row, 0)
            if prox_item:
                prox = prox_item.text().strip()
                if prox:
                    proxies.append(prox)

        if not proxies:
            self.status_label.setText("No valid proxies.")
            self.srt_button.setEnabled(True)
            self.stop_but.setEnabled(False)
            return

        self.stop_event = threading.Event()

        self.check_thread = QThread()
        self.check_worker = ProxyCheckerWorker(
            proxies,
            self.proxy_type,
            self.stop_event
        )
        self.check_worker.moveToThread(self.check_thread)

        self.check_thread.started.connect(self.check_worker.run)

        self.check_worker.checked.connect(self.on_proxy_checked)
        self.check_worker.progress.connect(self.update_progress)
        self.check_worker.finished.connect(self.on_check_finished)

        self.check_worker.finished.connect(self.check_thread.quit)
        self.check_worker.finished.connect(self.check_worker.deleteLater)
        self.check_thread.finished.connect(self.check_thread.deleteLater)

        self.check_thread.start()

    def on_proxy_checked(self, proxy, working, response_time):
        try:
            response_time = float(response_time) / 1000.0
        except (TypeError, ValueError):
            response_time = 0.0

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text().strip() == proxy:
                if working:
                    self.table.setItem(row, 1, QTableWidgetItem("WORKING"))
                    self.table.setItem(row, 2, QTableWidgetItem(f"{response_time:.3f}s"))
                else:
                    self.table.setItem(row, 1, QTableWidgetItem("DEAD"))
                    self.table.setItem(row, 2, QTableWidgetItem("-"))

                self.table.setItem(row, 3, QTableWidgetItem("Checked"))
                break

    def on_check_finished(self):
        was_stopped = (
            hasattr(self, "stop_event") and self.stop_event.is_set()
        )

        self.steart = False

        if was_stopped:
            self.status_label.setText("Checking stopped.")
        else:
            self.status_label.setText("Checking completed.")
            self.update_progress(100)

        self.srt_button.setEnabled(True)
        self.stop_but.setEnabled(False)

        working_proxies = []
        dead_proxies = []

        for row in range(self.table.rowCount()):
            proxy_item = self.table.item(row, 0)
            status_item = self.table.item(row, 1)

            if not proxy_item or not status_item:
                continue

            proxy = proxy_item.text().strip()
            status = status_item.text().strip().upper()

            if status == "WORKING":
                if proxy not in working_proxies:
                    working_proxies.append(proxy)
            elif status == "DEAD":
                if proxy not in dead_proxies:
                    dead_proxies.append(proxy)

        self.working_card.value_label.setText(str(len(working_proxies)))
        self.dead_card.value_label.setText(str(len(dead_proxies)))

        total_checked = len(working_proxies) + len(dead_proxies)
        if total_checked > 0:
            success_rate = (len(working_proxies) / total_checked) * 100
        else:
            success_rate = 0.0

        self.success.value_label.setText(f"{success_rate:.1f}%")

    def update_progress(self, value):
        self.process.setValue(value)

    def import_proxy(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Proxy File",
            "",
            "Text Files (*.txt)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]

            proxies = list(dict.fromkeys(proxies))
            self.table.setRowCount(0)

            for proxy in proxies:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(proxy))
                self.table.setItem(row, 1, QTableWidgetItem("WAITING"))
                self.table.setItem(row, 2, QTableWidgetItem("-"))
                self.table.setItem(row, 3, QTableWidgetItem("Not checked"))

            self.total_card.value_label.setText(str(len(proxies)))
            self.working_card.value_label.setText("0")
            self.dead_card.value_label.setText("0")
            self.success.value_label.setText("0%")

            self.process.setValue(0)
            self.status_label.setText(f"{len(proxies)} proxies loaded")

        except Exception as error:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Could not load proxy file:\n\n{error}"
            )

    def clearprox(self):
        self.table.setRowCount(0)

        self.total_card.value_label.setText("0")
        self.working_card.value_label.setText("0")
        self.dead_card.value_label.setText("0")
        self.success.value_label.setText("0%")

        self.process.setValue(0)
        self.status_label.setText("Ready")

    # =========================
    # NEW: Save Working Proxies
    # =========================
    def save_working(self):
        working_data = []   # list of (proxy, response_time_ms)

        for row in range(self.table.rowCount()):
            proxy_item = self.table.item(row, 0)
            status_item = self.table.item(row, 1)
            time_item = self.table.item(row, 2)

            if not proxy_item or not status_item:
                continue

            if status_item.text().strip().upper() == "WORKING":
                proxy = proxy_item.text().strip()
                if not proxy:
                    continue

                # Convert displayed seconds back to milliseconds
                time_text = time_item.text().strip() if time_item else "0"
                try:
                    seconds = float(time_text.replace("s", "").strip())
                    ms = seconds * 1000
                except:
                    ms = 0.0

                working_data.append((proxy, ms))

        if not working_data:
            self._show_msg("No Working Proxies", "There are no working proxies to save.")
            return

        try:
            for proxy, ms in working_data:
                save_working_proxy(
                    proxy,
                    self.proxy_type or "unknown",
                    ms
                )

            self.status_label.setText(f"Saved {len(working_data)} working proxies")
            self._show_msg("Saved", f"Successfully saved {len(working_data)} working proxies.")

        except Exception as e:
            self._show_msg("Save Error", f"Could not save working proxies:\n\n{e}", critical=True)


    def _show_msg(self, title, text, critical=False):
        """Helper for consistent dark message boxes"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical if critical else QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e1e;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 8px 22px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #333333;
            }
        """)
        msg.exec()