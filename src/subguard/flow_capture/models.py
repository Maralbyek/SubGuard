"""Data models for ordered flow evidence."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CapturedScreen:
    """Evidence captured from one ordered browser screen."""

    order: int
    url: str
    dom_path: str
    visible_text_path: str
    screenshot_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapturedFlow:
    """The ordered evidence bundle for one public flow."""

    source_url: str
    flow_type: str
    output_dir: str
    screens: tuple[CapturedScreen, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_url": self.source_url,
            "flow_type": self.flow_type,
            "output_dir": self.output_dir,
            "screen_count": len(self.screens),
            "screens": [screen.to_dict() for screen in self.screens],
        }

    @property
    def path(self) -> Path:
        return Path(self.output_dir)

