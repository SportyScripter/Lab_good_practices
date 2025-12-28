from flask import Flask, request, jsonify
import pika
import json
import os

rabbit_host = os.environ.get("RABBIT_HOST", "localhost")
rabbit_user = os.environ.get("RABBIT_USER", "guest")
rabbit_pass = os.environ.get("RABBIT_PASS", "guest")
app = Flask(__name__)


def send_to_queue(message_body):
    credentials = pika.PlainCredentials(rabbit_user, rabbit_pass)
    parameters = pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="image_analysis_queue", durable=True)

    if isinstance(message_body, dict):
        body = json.dumps(message_body)
    else:
        body = str(message_body)

    channel.basic_publish(exchange="", routing_key="image_analysis_queue", body=body)
    connection.close()


@app.route("/", methods=["GET"])
def index():
    return "<h1>API działa! </h1><p>Wyślij POST na /analyze_img</p>"


@app.route("/analyze_img", methods=["POST"])
def analyze_async():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    task = {"url": url}

    send_to_queue(task)

    return jsonify({"message": "Task submitted", "url": url}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
