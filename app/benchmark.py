import time
import requests
import statistics


URL = "http://127.0.0.1:8000/recommend"

queries = [
    "BlackBerry smartphone business",
    "artificial intelligence and machine learning",
    "US presidential election",
    "technology companies and smartphones",
    "sports championship and athletes"
]

latencies = []

for query in queries:

    start = time.perf_counter()

    response = requests.post(
        URL,
        json={
            "query": query,
            "k": 5
        }
    )

    end = time.perf_counter()

    latency = (end - start) * 1000

    latencies.append(latency)

    print(f"{latency:.2f} ms | {query}")


print("\n" + "=" * 50)
print("BENCHMARK RESULTS")
print("=" * 50)

print(f"Requests: {len(latencies)}")
print(f"Average:  {statistics.mean(latencies):.2f} ms")
print(f"Minimum:  {min(latencies):.2f} ms")
print(f"Maximum:  {max(latencies):.2f} ms")