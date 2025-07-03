from abc import ABC, abstractmethod
import datetime

class Scraper(ABC):
    """
    Abstract base class representing a scraping.

    This class defines the interface to the scraping layers and provides 
    helpers for doing data operations and orchestration tasks
    
    Abstract methods:
        entry_point(): must be overridden with specific implementation for 
        orchestration of the scraping.

    """

    # TODO: Add reference to Catalog
    def __init__(self):
        self._now = datetime.datetime.now(datetime.timezone.utc)

    @abstractmethod
    def entry_point(self) -> None:
        # execution steps here
        True
