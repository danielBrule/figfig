from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient
import os

load_dotenv()
from utils.db import create_tables, init_tables
from utils.log import logger
from utils.constants import ServiceQueue

SB_CONNECTION_STRING = os.getenv("SERVICEBUS_CONNECTION_STRING")


def clean_servicebus(queue_name: str):
    """_summary_
    Cleans the specified Azure Service Bus queue by deleting all messages.

    Args:
        queue_name (str): _description_
    """

    with ServiceBusClient.from_connection_string(SB_CONNECTION_STRING) as client:
        receiver = client.get_queue_receiver(queue_name=queue_name)

        with receiver:
            while True:
                messages = receiver.receive_messages(
                    max_message_count=50, max_wait_time=5
                )
                if not messages:
                    print(f"Queue {queue_name} is empty.")
                    break
                for msg in messages:
                    receiver.complete_message(msg)
                    print(f"Deleted: {msg.message_id}")


logger.info("initialise data base")
create_tables()
init_tables()

logger.info("Clreaning Service Bus Queues")
for sb in ServiceQueue:
    clean_servicebus(queue_name=sb.value)
