from flask import Flask, request, jsonify
from detector import count_people_on_image
import time

app = Flask(__name__)


@app.route("/count_people", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Received URL: {url}")

    count = count_people_on_image(url)
    return jsonify({"url": url, "people_count": count})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
