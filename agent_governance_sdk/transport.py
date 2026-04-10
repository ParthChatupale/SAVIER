from __future__ import annotations

import logging
import queue
import threading
from typing import Any

import requests


class AsyncTransport:
    def __init__(
        self,
        backend_url: str,
        *,
        api_key: str | None = None,
        timeout_sec: float = 2.0,
        max_queue_size: int = 1000,
        debug: bool = False,
    ) -> None:
        self.backend_url = backend_url
        self.api_key = api_key
        self.timeout_sec = timeout_sec
        self.debug = debug
        self._log = logging.getLogger("agent_governance_sdk")
        self._queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=max_queue_size)
        self._worker = threading.Thread(target=self._run, daemon=True, name="sdk-sender")
        self._worker.start()

    def enqueue(self, payload: dict[str, Any]) -> None:
        try:
            self._queue.put_nowait(payload)
        except queue.Full:
            if self.debug:
                self._log.warning("agent_governance_sdk queue full; dropping payload")

    def _run(self) -> None:
        while True:
            payload = self._queue.get()
            self._transmit(payload)
            self._queue.task_done()

    def _transmit(self, payload: dict[str, Any]) -> None:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(
                self.backend_url,
                json=payload,
                headers=headers,
                timeout=self.timeout_sec,
            )
            if self.debug:
                self._log.info(
                    "agent_governance_sdk sent payload to %s (status %s)",
                    self.backend_url,
                    response.status_code,
                )
            if self.debug and response.status_code >= 400:
                self._log.warning(
                    "agent_governance_sdk backend responded %s: %s",
                    response.status_code,
                    response.text[:200],
                )
        except requests.exceptions.RequestException as exc:
            if self.debug:
                self._log.warning("agent_governance_sdk transmit failed: %s", exc)
