import threading
from collections import deque
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple, Union

try:
    import gcipuinfo  # type: ignore
except ImportError:
    gcipuinfo = None

import wandb

from .aggregators import aggregate_mean
from .asset_registry import asset_registry
from .interfaces import Interface, Metric, MetricsMonitor

if TYPE_CHECKING:
    from typing import Deque

    from wandb.sdk.internal.settings_static import SettingsStatic


class IPUStats:
    """Stats for Graphcore IPU devices."""

    name = "ipu.{}.{}"
    samples: "Deque[dict]"

    # The metrics that change over time.
    # Only these are returned on each invocation
    # to avoid sending a load of unnecessary data.
    variable_metric_keys = {
        "average board temp",
        "average die temp",
        "clock",
        "ipu power",
        "ipu utilisation",
        "ipu utilisation (session)",
    }

    def __init__(self, pid: int, gc_ipu_info: Optional[Any] = None) -> None:
        self.samples: Deque[dict] = deque()

        if gc_ipu_info is None:
            if not gcipuinfo:
                raise ImportError(
                    "Monitoring IPU stats requires gcipuinfo to be installed"
                )

            self._gc_ipu_info = gcipuinfo.gcipuinfo()
        else:
            self._gc_ipu_info = gc_ipu_info
        self._gc_ipu_info.setUpdateMode(True)

        self._pid = pid
        self._devices_called: Set[str] = set()

    @staticmethod
    def parse_metric(key: str, value: str) -> Optional[Tuple[str, Union[int, float]]]:
        metric_suffixes = {
            "temp": "C",
            "clock": "MHz",
            "power": "W",
            "utilisation": "%",
            "utilisation (session)": "%",
            "speed": "GT/s",
        }

        for metric, suffix in metric_suffixes.items():
            if key.endswith(metric) and value.endswith(suffix):
                value = value[: -len(suffix)]
                key = f"{key} ({suffix})"

        try:
            float_value = float(value)
            num_value = int(float_value) if float_value.is_integer() else float_value
        except ValueError:
            return None

        return key, num_value

    def sample(self) -> None:
        """This function samples the IPU stats and logs the metrics for the devices. It first gets the devices and their metrics. Then, it filters the metrics based on the user process id and logs the metrics for the devices that have not been called before or have variable metric keys. An exception will be thrown if any errors occur.
        Input-Output Arguments
        :param self: IPUStats. An instance of the IPUStats class.
        :return: None. No return value.
        """

    def clear(self) -> None:
        self.samples.clear()

    def aggregate(self) -> dict:
        if not self.samples:
            return {}
        stats = {}
        for key in self.samples[0].keys():
            samples = [s[key] for s in self.samples if key in s]
            aggregate = aggregate_mean(samples)
            stats[key] = aggregate
        return stats


@asset_registry.register
class IPU:
    def __init__(
        self,
        interface: "Interface",
        settings: "SettingsStatic",
        shutdown_event: threading.Event,
    ) -> None:
        self.name = self.__class__.__name__.lower()
        self.metrics: List[Metric] = [
            IPUStats(settings._stats_pid),
        ]
        self.metrics_monitor = MetricsMonitor(
            self.name,
            self.metrics,
            interface,
            settings,
            shutdown_event,
        )

    @classmethod
    def is_available(cls) -> bool:
        return gcipuinfo is not None

    def start(self) -> None:
        self.metrics_monitor.start()

    def finish(self) -> None:
        self.metrics_monitor.finish()

    def probe(self) -> dict:
        device_data = self.metrics[0]._gc_ipu_info.getDevices()  # type: ignore
        device_count = len(device_data)
        devices = []
        for i, device in enumerate(device_data):
            device_metrics: Dict[str, str] = dict(device)
            devices.append(
                {
                    "id": device_metrics.get("id") or i,
                    "board ipu index": device_metrics.get("board ipu index"),
                    "board type": device_metrics.get("board type") or "unknown",
                }
            )

        return {
            self.name: {
                "device_count": device_count,
                "devices": devices,
                "vendor": "Graphcore",
            }
        }