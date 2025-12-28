import pika
import time
import os
import sys
import requests
import numpy as np
import cv2
from ultralytics import YOLO

rabbit_host = os.environ.get("RABBIT_HOST", "localhost")
rabbit_user = os.environ.get("RABBIT_USER", "guest")
rabbit_pass = os.environ.get("RABBIT_PASS", "guest")

print(" [i] Loading YOLO model...")
model = YOLO("yolov8n.pt")


def analyze_image_yolo(image_url):
    try:
        resp = requests.get(image_url, stream=True)
        resp.raise_for_status()
        image_array = np.asarray(bytearray(resp.content), dtype="uint8")
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            print(" [!] Error: Could not decode image.")
            return 0

        results = model(image, verbose=False)

        person_count = 0
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if cls == 0 and conf > 0.4:
                    person_count += 1

        return person_count
    except Exception as e:
        print(f" [!] Error analyzing image: {e}")
        return 0


def callback(ch, method, properties, body):
    try:
        message = eval(body.decode())
        url = message.get("url")
        print(f"[x] Received URL: {url}")
        count = analyze_image_yolo(url)
        print(f" [V] Task complete. YOLO detected: {count} people.")
    except Exception as e:
        print(f" [!] Error processing message: {e}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    print(f" [*] Connecting to {rabbit_host} as {rabbit_user}...")

    credentials = pika.PlainCredentials(rabbit_user, rabbit_pass)
    parameters = pika.ConnectionParameters(
        host=rabbit_host, credentials=credentials, heartbeat=600
    )

    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.queue_declare(queue="image_analysis_queue", durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue="image_analysis_queue", on_message_callback=callback
            )

            print(" [*] Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            print(" [!] Connection failed, retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            print(f" [!] Unexpected error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    try:
        start_worker()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
