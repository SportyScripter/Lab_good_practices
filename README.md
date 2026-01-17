# 🚗 Automatic License Plate Recognition (ALPR) System

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Queue-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLO-v8-yellow?style=for-the-badge)

A robust, microservices-based system for detecting and reading vehicle license plates. This project leverages **YOLOv8** for object detection and **EasyOCR** for text recognition, orchestrated via **Docker Compose** to ensure scalability and ease of deployment.

---

## 🏗️ System Architecture

The application follows the **Producer-Consumer** pattern to handle heavy ML inference tasks efficiently without blocking the main API.

### Services Overview
1.  **API (FastAPI):** Acts as the gateway. Handles HTTP requests, validates file uploads, and pushes tasks to the Redis queue.
2.  **Redis:** The message broker. Stores the queue of images waiting for processing.
3.  **Worker:** A background service. Pulls tasks from Redis, runs the AI models (YOLO + OCR), and saves results.
4.  **Redis UI (Redis Commander):** Web interface to monitor the job queue in real-time.
5.  **Database UI (SQLite Web):** Web interface to view processed results stored in the database.

### Data Flow
1.  Client uploads an image via `POST /queue-image`.
2.  API saves the file and pushes a task ID to **Redis**.
3.  **Worker** picks up the task asynchronously.
4.  **YOLOv8** detects the license plate bounding box.
5.  **EasyOCR** reads the text from the cropped plate region.
6.  Results are saved permanently in **SQLite**.

---

## 📂 Project Structure

```text
.
├── docker-compose.yml       # Orchestration for API, Redis, Worker, and UI services
├── Dockerfile               # Container build definition for Python environment
├── requirements.txt         # Python dependencies list
├── data.yaml                # YOLOv8 dataset configuration
├── best.pt                  # Trained YOLOv8 model weights for plate detection
├── main.py                  # Local entry point script
├── src/                     # Source code directory
│   ├── api.py               # FastAPI application (Producer)
│   ├── worker.py            # Background worker logic (Consumer)
│   ├── ocr_engine.py        # Core class wrapping YOLO and EasyOCR logic
│   ├── plates.db            # SQLite database file for storing results
│   ├── 1_prepare_data.py    # ETL script: Converts CVAT XML to YOLO format
│   ├── 2_train.py           # Script for training the YOLO model
│   ├── 3_resume.py          # Script to resume interrupted training
│   ├── 4_evaluate_debug.py  # Debugging tool for model evaluation
│   ├── 5_evaluate.py        # Metrics calculation and model testing
│   ├── check_model.py       # Utility to verify model loading
│   ├── check_xml.py         # Utility to validate annotation files
│   └── uploads/             # Shared directory for temporary image storage
├── data/                    # Raw input data (CVAT annotations & original images)
├── datasets/                # Processed dataset ready for YOLO training (train/val split)
├── runs/                    # Training logs, confusion matrices, and model checkpoints
└── tests/                   # Unit and integration tests

```

---

## 🚀 Installation & Setup

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* Git.

### 1. Clone the repository
We are using a specific branch for the final project version. Please use the command below to clone the correct branch directly:

```bash
git clone -b automatic_plate_number_recognition https://github.com/SportyScripter/Lab_good_practices.git

cd Lab_good_practices
```

### 2. Launch the environment

Build and start all containers with a single command:

```bash
docker-compose up -d --build
```

*Note: The first launch might take a few minutes as it downloads Python images, PyTorch libraries, and OCR models.*

---

## 🖥️ Dashboard & Access

Once running, the system exposes the following interfaces:

| Service | URL | Description |
| --- | --- | --- |
| **API Docs (Swagger)** | [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs) | Interactive API documentation and testing tool. |
| **Redis Commander** | [http://localhost:8081](https://www.google.com/search?q=http://localhost:8081) | Visual tool to inspect the Redis queue. |
| **Database Viewer** | [http://localhost:8082](https://www.google.com/search?q=http://localhost:8082) | Browser for the SQLite database results. |

---

## 📡 API Usage

The system supports two modes of operation:

### 1. Asynchronous Mode (Recommended)

Delegates processing to the background worker. Ideal for high loads.

* **Endpoint:** `POST /queue-image`
* **Content-Type:** `multipart/form-data`
* **Response:**
```json
{
  "task_id": "b76e2476-e01c-4477-8256-5dfd08e477f4",
  "status": "queued"
}

```



### 2. Synchronous Mode (Testing)

Blocks the request until inference is complete. Useful for quick debugging.

* **Endpoint:** `POST /predict`
* **Content-Type:** `multipart/form-data`
* **Response:**
```json
{
  "filename": "car_test.jpg",
  "plate_detected": "KR12345"
}

```



---

## 🧠 ML Pipeline Details

The project includes a complete pipeline for training the custom detector:

1. **Data Preparation (`1_prepare_data.py`):**
* Parses XML annotations (CVAT format).
* Normalizes coordinates to YOLO format (0-1 scale).
* Splits data into Training and Validation sets.


2. **Training (`2_train.py`):**
* Fine-tunes the `yolov8n.pt` (nano) model on the custom dataset.
* Uses augmentation and specific hyperparameters defined in the script.


3. **Evaluation (`5_evaluate.py`):**
* Calculates accuracy and visualizes results.



---

## 🛠️ Tech Stack

* **Language:** Python 3.10
* **Web Framework:** FastAPI + Uvicorn
* **Object Detection:** Ultralytics YOLOv8
* **OCR:** EasyOCR + OpenCV
* **Infrastructure:** Docker, Redis (Alpine), SQLite
* **Monitoring:** Redis Commander, SQLite-Web

---

## 👨‍💻 Author

**Adrian**
*Good Practices in Software Engineering Course*
M.Sc. Studies
