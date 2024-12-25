from confluent_kafka import Consumer, KafkaError
import json
from bs4 import BeautifulSoup
from typing import List

from common.mystery_picture import MysteryPicture, MysteryPictureDict
from settings import KAFKA_CONFIGS, KAFKA_TOPIC_MYSTERY_PICTURE
from common.hockey import HockeyTeamResults, HockeyTeamResultsDict


def mystery_picture_push_to_sqlite():
    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_CONFIGS["bootstrap.servers"],
            "group.id": "sqlite",
            "auto.offset.reset": "earliest",
        }
    )

    def print_assignment(consumer, partitions):
        print("Assignment", partitions)

    consumer.subscribe([KAFKA_TOPIC_MYSTERY_PICTURE], on_assign=print_assignment)
    mystery_picture = MysteryPicture()

    while True:
        msg = consumer.poll(10.0)

        if msg is None:
            print("no more messages")
            # No more messages
            break
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        consumed_data = json.loads(msg.value().decode("utf-8"))
        response_json = json.loads(consumed_data["api_response"])

        # Change this function to parse the API's response and insert into the MysteryPicture table.
        formatted_rows: List[MysteryPictureDict] = []
        for y_idx in range(500):
            formatted_rows.append(
                MysteryPictureDict(
                    X=response_json["row_id"],
                    Y=y_idx,
                    Value=response_json["columns"][y_idx],
                )
            )
        mystery_picture.insert_data(formatted_rows)

    consumer.close()
