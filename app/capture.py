import base64
from io import BytesIO
from typing import Optional

from mss import mss
from PIL import Image


class ScreenCapture:
    def __init__(self, monitor_index: int = 1, jpg_quality: int = 65) -> None:
        self.monitor_index = monitor_index
        self.jpg_quality = jpg_quality

    def grab_frame_base64(self) -> Optional[str]:
        with mss() as sct:
            monitors = sct.monitors
            if self.monitor_index >= len(monitors):
                return None
            monitor = monitors[self.monitor_index]
            raw = sct.grab(monitor)

        image = Image.frombytes("RGB", raw.size, raw.rgb)
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=self.jpg_quality)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
