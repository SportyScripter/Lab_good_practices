import requests
import time

url = "http://localhost:5000/analyze_img"
payload = {"url": "https://images.pexels.com/photos/7148443/pexels-photo-7148443.jpeg"}

print("--- Startujemy masowe wysyłanie zadań ---")

for i in range(1, 201):
    try:
        response = requests.post(url, json=payload)
        print(f"Zadanie {i}: Kod {response.status_code}")
    except Exception as e:
        print(f"Zadanie {i}: BŁĄD {e}")

print("--- Wysłano wszystkie. Sprawdź logi workera! ---")
