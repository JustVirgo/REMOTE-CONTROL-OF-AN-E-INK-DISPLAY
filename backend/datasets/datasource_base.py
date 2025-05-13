from abc import ABC, abstractmethod
import time

class DataSource(ABC):
    def __init__(self, inputs: dict, uid : int):
        self.inputs = inputs
        self.uid = uid
        self.last_updated = 0  # UNIX timestamp
        self.cached_data = None

    @abstractmethod
    def fetch_data(self):
        """Fetch new data from the source and update cache."""
        pass

    @abstractmethod
    def get_data(self) -> dict:
        """Return cached data with type annotations."""
        pass

    @abstractmethod
    def get_update_interval(self) -> int:
        """Return update interval in seconds."""
        pass

    @abstractmethod
    def get_name(self) -> int:
        """Return update interval in seconds."""
        pass
    def get_uid(self) -> int:
        """Return the unique identifier for this data source."""
        return self.uid

    def update_data(self, force=False):
        """Fetch new data if update interval has passed, or force fetch."""
        now = time.time()
        if force or (now - self.last_updated) >= self.get_update_interval():
            self.fetch_data()
            self.last_updated = now
            return True
        return False
