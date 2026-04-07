from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
import re

from src.core.phase2_contracts import InboundMessage

OCRDetector = Callable[[str], str | None]
FilterPredicate = Callable[[InboundMessage], bool]


@dataclass(slots=True)
class ListenerConfig:
    source: str = "file_tail"
    channel: str = "ocr"
    priority: int = 100


class InboxListener:
    """OCR + file-tail listener with real-time filtering and normalized output."""

    def __init__(
        self,
        ocr_detector: OCRDetector,
        *,
        message_filter: FilterPredicate | None = None,
        config: ListenerConfig | None = None,
    ) -> None:
        self.ocr_detector = ocr_detector
        self.message_filter = message_filter or self._default_filter
        self.config = config or ListenerConfig()
        self._offsets: dict[Path, int] = {}

    def poll_file(self, path: Path) -> list[InboundMessage]:
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        start = self._offsets.get(path, 0)
        self._offsets[path] = len(lines)
        return self._consume_lines(lines[start:], source=str(path))

    def consume_stream(self, lines: Iterable[str], source: str = "stream") -> list[InboundMessage]:
        return self._consume_lines(lines, source=source)

    def _consume_lines(self, lines: Iterable[str], source: str) -> list[InboundMessage]:
        normalized: list[InboundMessage] = []
        for line in lines:
            detected = self.ocr_detector(line)
            if not detected:
                continue
            message = InboundMessage(
                source=source,
                text=detected,
                channel=self.config.channel,
                priority=self.config.priority,
                metadata={"raw": line, "listener_source": self.config.source},
            )
            if self.message_filter(message):
                normalized.append(message)
        return normalized

    @staticmethod
    def simple_ocr_detector(line: str) -> str | None:
        match = re.search(r"@(?P<agent>[\w-]+)\s+(?P<command>\w+)(?:\s+(?P<args>.*))?", line)
        if not match:
            return None
        args = (match.group("args") or "").strip()
        base = f"@{match.group('agent')} {match.group('command')}".strip()
        return f"{base} {args}".strip()

    @staticmethod
    def _default_filter(message: InboundMessage) -> bool:
        return message.text.startswith("@")
