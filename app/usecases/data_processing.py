import math
from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


class AgentDataProcessor:
    def __init__(self, height=1000) -> None:
        self.capacity: int = 3
        self.z_values: list = []
        self.height: int = abs(height)

    def _add_value(self, data):
        if len(self.z_values) == self.capacity:
            del self.z_values[0]
            self.z_values.append(data)
            return
        self.z_values.append(data)

    def _is_bump(self):
        """Checks if there is a bump on the road."""
        if len(self.z_values) < self.capacity:
            return False  # Don't check if there are fewer than 3 elements in the list

        # Extract accelerometer values
        previous_value = self.z_values[0].accelerometer.z
        current_value = self.z_values[1].accelerometer.z
        next_value = self.z_values[2].accelerometer.z

        # filtering of small fluctuations
        is_valid_delta = (current_value - previous_value) > self.height and self.height < (current_value - next_value)

        # Condition for detecting a bump
        return previous_value < current_value and current_value > next_value and is_valid_delta

    def _is_pothole(self):
        """Checks if there is a pothole on the road."""
        if len(self.z_values) < self.capacity:
            return False  # Don't check if there are fewer than 3 elements in the list

        # Extract accelerometer values
        previous_value = self.z_values[0].accelerometer.z
        current_value = self.z_values[1].accelerometer.z
        next_value = self.z_values[2].accelerometer.z

        # filtering of small fluctuations
        is_valid_delta = (previous_value - current_value) > self.height and self.height < (next_value - current_value)

        # Condition for detecting a pothole
        return previous_value > current_value and current_value < next_value and is_valid_delta

    def process(self, data: AgentData):
        self._add_value(data)
        if len(self.z_values) < self.capacity:
            return None

        road_state = "smooth"
        if self._is_bump():
            road_state = "bump"
        elif self._is_pothole():
            road_state = "pothole"
        print(road_state)
        return ProcessedAgentData(road_state=road_state, agent_data=self.z_values[1])
