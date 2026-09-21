from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
import requests
import re
import random


COUNTRY_MAP = {
    "Any Country": "",
    "United States": "US",
    "United Kingdom": "GB",
    "Germany": "DE",
    "France": "FR",
    "Canada": "CA",
    "Japan": "JP",
    "Singapore": "SG",
    "India": "IN",
    "Bangladesh": "BD",
}


class GetProxy:

    def __init__(self, userdata=None):
        self.userData = userdata or {}

    def start(self):
        proxy_type_raw = self.userData.get("type", "HTTP")
        country_raw = self.userData.get("country", "Any Country")
        amount = int(self.userData.get("amount", 50))
        custom_source = self.userData.get("source", "").strip()

        type_map = {
            "HTTP": "http",
            "HTTPS": "https",
            "SOCKS4": "socks4",
            "SOCKS5": "socks5",
            "Any Type": "http",
        }
        proxy_type = type_map.get(proxy_type_raw, "http")
        country_code = COUNTRY_MAP.get(country_raw, "")

        # Only working sources
        PROXY_APIS = [
            {
                "name": "Proxifly",
                "url": f"https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/{proxy_type}/data.txt",
                "params": {},
                "format": "txt",
            },
            {
                "name": "ProxyScrape",
                "url": "https://api.proxyscrape.com/v4/free-proxy-list/get",
                "params": {
                    "request": "display_proxies",
                    "protocol": proxy_type,
                    "proxy_format": "ipport",
                    "format": "text",
                    "limit": "300",
                },
                "format": "txt",
            },
            {
                "name": "TheSpeedX",
                "url": f"https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/{proxy_type}.txt",
                "params": {},
                "format": "txt",
            },
            {
                "name": "HProxy",
                "url": "https://hproxy.com/api/proxy-list",
                "params": {
                    "format": "txt",
                    "protocol": proxy_type,
                    "limit": "300",
                },
                "format": "txt",
            },
            {
                "name": "proxmint",
                "url": "https://proxmint.com/api/free-proxies",
                "params": {
                    "protocol": proxy_type,
                    "format": "txt",
                    "limit": "300",
                },
                "format": "txt",
            },
            {
                "name": "GeoNode",
                "url": "https://proxylist.geonode.com/api/proxy-list",
                "params": {
                    "limit": "300",
                    "page": "1",
                    "sort_by": "lastChecked",
                    "sort_type": "desc",
                    "protocols": proxy_type,
                },
                "format": "json",
            },
            {
                "name": "Stormsia",
                "url": "https://raw.githubusercontent.com/stormsia/proxy-list/main/working_proxies.txt",
                "params": {},
                "format": "txt",
            },
        ]

        if country_code:
            for api in PROXY_APIS:
                if api["name"] in ("ProxyScrape", "HProxy", "proxmint", "GeoNode"):
                    api["params"]["country"] = country_code

        total_proxy = []
        seen = set()

        # Custom source first
        if custom_source:
            print(f"Custom source → {custom_source}")
            try:
                r = requests.get(custom_source, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                self._extract_proxies(r.text, total_proxy, seen, amount)
            except Exception as e:
                print(f"Custom source failed: {e}")

        # =============================================
        # RANDOM ORDER + LIMIT PER API
        # =============================================
        random.shuffle(PROXY_APIS)

        # Max proxies we take from ONE single API
        # This forces using multiple different sources
        max_per_api = max(8, amount // 4)   # e.g. 50 → max 12 per source

        for api in PROXY_APIS:
            if len(total_proxy) >= amount:
                break

            print(f"Trying → {api['name']}")

            try:
                response = requests.get(
                    api["url"],
                    params=api.get("params", {}),
                    timeout=12,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                response.raise_for_status()

                before = len(total_proxy)

                if api.get("format") == "json":
                    try:
                        data = response.json()
                        items = data.get("data", data) if isinstance(data, dict) else data
                        text = ""
                        for item in items:
                            if isinstance(item, dict):
                                ip = item.get("ip") or item.get("host")
                                port = item.get("port")
                                if ip and port:
                                    text += f"{ip}:{port}\n"
                        self._extract_proxies(text, total_proxy, seen, amount, max_per_api)
                    except Exception:
                        self._extract_proxies(response.text, total_proxy, seen, amount, max_per_api)
                else:
                    self._extract_proxies(response.text, total_proxy, seen, amount, max_per_api)

                added = len(total_proxy) - before
                print(f"  ✓ {api['name']} added {added}  |  total: {len(total_proxy)}")

            except Exception as e:
                print(f"  ✗ {api['name']} failed: {e}")
                continue

        print(f"Finished. Unique proxies: {len(total_proxy)}")
        return total_proxy[:amount] if total_proxy else None

    def _extract_proxies(self, text, total_proxy, seen, amount, max_from_this=9999):
        """Extract valid ip:port. Stop after max_from_this from current API."""
        pattern = re.compile(
            r"(?:(?:https?|socks[45])://)?(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})"
        )

        added_from_this = 0

        for match in pattern.finditer(text):
            if len(total_proxy) >= amount:
                return
            if added_from_this >= max_from_this:
                return

            proxy = f"{match.group(1)}:{match.group(2)}"

            if proxy in seen:
                continue

            try:
                ip_parts = match.group(1).split(".")
                if len(ip_parts) != 4:
                    continue
                if not all(0 <= int(x) <= 255 for x in ip_parts):
                    continue
                port = int(match.group(2))
                if not (1 <= port <= 65535):
                    continue
            except:
                continue

            seen.add(proxy)
            total_proxy.append(proxy)
            added_from_this += 1


class FreeProxyUi(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Free ProxY v1.3")
        self.resize(520, 650)
        self.setMinimumSize(480, 600)

        self.user_requests = None
        self.proxy_user_type = None

        self.setStyleSheet("""
            QWidget {
                background-color: #0D0D0D;
                color: #EAEAEA;
                font-family: "Segoe UI";
                font-size: 13px;
            }
            QFrame#card {
                background-color: #151515;
                border: 1px solid #292929;
                border-radius: 14px;
            }
            QLabel#title {
                font-size: 26px;
                font-weight: 700;
                color: #FFFFFF;
            }
            QLabel#subtitle {
                font-size: 13px;
                color: #777777;
            }
            QLabel#section {
                font-size: 12px;
                font-weight: 600;
                color: #AFAFAF;
            }
            QComboBox, QLineEdit, QSpinBox {
                background-color: #1D1D1D;
                border: 1px solid #303030;
                border-radius: 8px;
                padding: 10px 12px;
                color: #F5F5F5;
                selection-background-color: #3A3A3A;
            }
            QComboBox:hover, QLineEdit:hover, QSpinBox:hover {
                border-color: #4A4A4A;
            }
            QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
                border-color: #777777;
            }
            QComboBox QAbstractItemView {
                background-color: #1B1B1B;
                color: white;
                border: 1px solid #333333;
                selection-background-color: #333333;
                padding: 5px;
            }
            QCheckBox {
                spacing: 9px;
                color: #B8B8B8;
                padding: 3px 0;
            }
            QCheckBox:hover {
                color: #FFFFFF;
            }
            QPushButton#getButton {
                background-color: #EAEAEA;
                color: #111111;
                border: none;
                border-radius: 9px;
                padding: 12px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton#getButton:hover {
                background-color: #FFFFFF;
            }
            QPushButton#getButton:pressed {
                background-color: #CFCFCF;
            }
            QLabel#hint {
                color: #606060;
                font-size: 11px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(0)

        title = QLabel("Free Proxy")
        title.setObjectName("title")
        subtitle = QLabel("Choose the proxy configuration you want to receive.")
        subtitle.setObjectName("subtitle")

        main_layout.addWidget(title)
        main_layout.addSpacing(5)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(24)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(10)

        type_label = QLabel("Proxy Type")
        type_label.setObjectName("section")
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["HTTP", "HTTPS", "SOCKS4", "SOCKS5", "Any Type"])
        card_layout.addWidget(type_label)
        card_layout.addWidget(self.proxy_type)
        card_layout.addSpacing(7)

        country_label = QLabel("Country")
        country_label.setObjectName("section")
        self.country = QComboBox()
        self.country.addItems([
            "Any Country", "United States", "United Kingdom", "Germany",
            "France", "Canada", "Japan", "Singapore", "India", "Bangladesh"
        ])
        card_layout.addWidget(country_label)
        card_layout.addWidget(self.country)
        card_layout.addSpacing(7)

        amount_label = QLabel("Number of Proxies")
        amount_label.setObjectName("section")
        self.amount = QSpinBox()
        self.amount.setRange(1, 2000)
        self.amount.setValue(50)
        card_layout.addWidget(amount_label)
        card_layout.addWidget(self.amount)
        card_layout.addSpacing(7)

        source_label = QLabel("Custom Source")
        source_label.setObjectName("section")
        self.source = QLineEdit()
        self.source.setPlaceholderText("Optional proxy source URL...")
        card_layout.addWidget(source_label)
        card_layout.addWidget(self.source)

        hint = QLabel("Leave empty to use random free proxy sources.")
        hint.setObjectName("hint")
        card_layout.addWidget(hint)
        card_layout.addSpacing(10)

        self.anonymous = QCheckBox("Anonymous proxies only")
        self.https_only = QCheckBox("HTTPS supported only")
        card_layout.addWidget(self.anonymous)
        card_layout.addWidget(self.https_only)
        card_layout.addSpacing(14)

        self.get_proxy_btn = QPushButton("GET PROXIES")
        self.get_proxy_btn.setObjectName("getButton")
        self.get_proxy_btn.setCursor(Qt.PointingHandCursor)
        self.get_proxy_btn.clicked.connect(self.get_proxy_settings)
        card_layout.addWidget(self.get_proxy_btn)

        main_layout.addWidget(card)
        main_layout.addStretch()

    def get_proxy_settings(self):
        settings = {
            "type": self.proxy_type.currentText(),
            "country": self.country.currentText(),
            "amount": self.amount.value(),
            "source": self.source.text().strip(),
            "anonymous": self.anonymous.isChecked(),
            "https_only": self.https_only.isChecked()
        }

        self.get_proxy_btn.setEnabled(False)
        self.get_proxy_btn.setText("Fetching...")

        try:
            get_prox = GetProxy(settings)
            prox = get_prox.start()

            if not prox:
                QMessageBox.warning(
                    self, "No Proxies",
                    "Could not fetch any proxies.\nTry again later."
                )
                self.get_proxy_btn.setEnabled(True)
                self.get_proxy_btn.setText("GET PROXIES")
                return

            self.user_requests = prox
            self.proxy_user_type = self.proxy_type.currentText()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get proxies:\n{e}")
            self.get_proxy_btn.setEnabled(True)
            self.get_proxy_btn.setText("GET PROXIES")