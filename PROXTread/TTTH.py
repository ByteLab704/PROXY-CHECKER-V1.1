import threading
from PySide6.QtCore import QObject, Signal
from CHECKS.check_proxy import check_user_proxy


class ProxyCheckerWorker(QObject):
    checked = Signal(str, bool, object)
    progress = Signal(int)
    finished = Signal()

    def __init__(self, proxies, proxy_type, stop_event):
        super().__init__()

        self.proxies = proxies
        self.proxy_type = proxy_type
        self.stop_event = stop_event

    def run(self):
        total = len(self.proxies)

        if total == 0:
            self.finished.emit()
            return

        for index, proxy in enumerate(self.proxies):

            # Stop requested?
            if self.stop_event.is_set():
                break

            try:
                working, response_time = check_user_proxy(
                    self.proxy_type,
                    proxy,
                    True
                )

            except Exception:
                working = False
                response_time = None

            # Stop requested while checking
            if self.stop_event.is_set():
                break

            self.checked.emit(
                proxy,
                working,
                response_time
            )

            percent = int(((index + 1) / total) * 100)
            self.progress.emit(percent)

        self.finished.emit()