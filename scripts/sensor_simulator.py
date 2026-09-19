import asyncio
from typing import Dict, Any

class SensorSimulator:
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.cycle_count = 0
        self.states: Dict[str, Any] = {}

    def init_sensors(self):
        for i in range(1, 15):
            sensor_code = f"S-RN-{i:03d}"
            self.states[sensor_code] = {
                "sensor_code": sensor_code,
                "rainfall_rate": 4.5,
                "water_level": 1.2,
                "battery": 95.0,
                "status": "NORMAL"
            }

    async def step(self, force_cloudburst: bool = False):
        self.cycle_count += 1
        for sensor_code, state in self.states.items():
            if force_cloudburst:
                state["rainfall_rate"] += 15.0
                state["water_level"] += 0.5
                state["status"] = "CRITICAL"
            else:
                state["rainfall_rate"] = max(0.0, state["rainfall_rate"] + 0.1)
                state["water_level"] = max(0.5, state["water_level"] + 0.02)
