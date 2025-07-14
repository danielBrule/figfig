import os
from azure.servicebus import (
    ServiceBusClient,
    ServiceBusMessage,
    ServiceBusReceivedMessage,
)
from abc import ABC, abstractmethod
import datetime
from sqlalchemy.orm import Session
from db.models import Error
from db.database import get_engine
from utils.log import logger


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
        self._stage = None
        self._service_bus_queue_source = None
        self._service_bus_queue_destination = None
        self._servicebus_connection_str = os.getenv("SERVICEBUS_CONNECTION_STRING")
        self._servicebus_client = ServiceBusClient.from_connection_string(
            self._servicebus_connection_str
        )
        self._servicebus_source_message = None

    @abstractmethod
    def entry_point(self) -> None:
        # execution steps here
        True

    @abstractmethod
    def _error_recovery(self) -> None:
        # execution steps here
        True

    def send_message(self, messages: list[str]):
        if self._service_bus_queue_destination is None:
            raise ValueError("Queue destination is not set.")

        logger.info(
            f"Sending {len(messages)} messages for {self._stage} to queue: {self._service_bus_queue_destination}"
        )

        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=self._servicebus_connection_str, logging_enable=True
        )

        with servicebus_client:
            sender = servicebus_client.get_queue_sender(
                queue_name=self._service_bus_queue_destination
            )
            with sender:
                # Build a list of ServiceBusMessage objects
                servicebus_messages = [ServiceBusMessage(msg, message_id=msg) for msg in messages]
                sender.send_messages(servicebus_messages)  # ✅ batch send
                logger.info(f"✅ Sent {len(messages)} messages.")

    def get_one_message(self):
        """
        Retrieves one message from the queue. Returns None if no message.
        """
        logger.info("get_one_message")
        if self._service_bus_queue_source is None:
            raise ValueError("Queue source is not set.")
        logger.info(
            f"\t\tRetrieving one message from queue: {self._service_bus_queue_source}"
        )

        with self._servicebus_client:
            receiver = self._servicebus_client.get_queue_receiver(
                queue_name=self._service_bus_queue_source, max_wait_time=5
            )
            with receiver:
                logger.info("\t\tReceiving messages...")
                messages = receiver.receive_messages(max_message_count=1)
                logger.info(f"\t\tReceived {len(messages)} messages.")
                if len(messages):
                    self._servicebus_source_message = messages[0]
                    logger.info(
                        f"\t\tMessage received: {self._servicebus_source_message}"
                    )

    def complete_message(self) -> None:
        """
        Marks a message as successfully processed (removes it from the queue).
        """
        logger.info("complete_message")

        with self._servicebus_client:
            receiver = self._servicebus_client.get_queue_receiver(
                queue_name=self._service_bus_queue_source
            )
            with receiver:
                receiver.complete_message(self._servicebus_source_message)

    def abandon_message(self) -> None:
        """
        Abandons the message so it can be retried later.
        """
        logger.info("abandon_message")
        with self._servicebus_client:
            receiver = self._servicebus_client.get_queue_receiver(
                queue_name=self._service_bus_queue_source
            )
            with receiver:
                receiver.abandon_message(self._servicebus_source_message)

    def log_scraper_error(self, id, error):
        error_entry = Error(
            stage=self._stage,
            data_id=id,
            error_type=type(error).__name__,
            error_message=str(error),
            attempted_at=datetime.datetime.now(datetime.timezone.utc),
        )
        with Session(get_engine()) as session:
            session.add(error_entry)
            session.commit()
