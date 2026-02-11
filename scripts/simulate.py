import requests
import random
import time
import threading
import sys

API_BASE_URL = "http://localhost:8000/api/leaderboard"

def submit_score():
    try:
        user_id = random.randint(1, 1000000)
        score = random.randint(10, 1000)
        payload = {
            "user_id": user_id,
            "score": score,
            "game_mode": "survival"
        }
        response = requests.post(f"{API_BASE_URL}/submit", json=payload)
        # print(f"Submitted score for user {user_id}: {response.status_code}")
    except Exception as e:
        print(f"Error submitting score: {e}")

def get_top_players():
    try:
        response = requests.get(f"{API_BASE_URL}/top")
        # print(f"Top players: {response.status_code}")
    except Exception as e:
        print(f"Error getting top players: {e}")

def get_user_rank():
    try:
        user_id = random.randint(1, 1000000)
        response = requests.get(f"{API_BASE_URL}/rank/{user_id}")
        # print(f"Rank for user {user_id}: {response.status_code}")
    except Exception as e:
        print(f"Error getting rank: {e}")

def worker():
    while True:
        action = random.choice(['submit', 'top', 'rank'])
        if action == 'submit':
            submit_score()
        elif action == 'top':
            get_top_players()
        elif action == 'rank':
            get_user_rank()
        time.sleep(random.uniform(0.1, 0.5))

def run_simulation(num_threads=10):
    print(f"Starting simulation with {num_threads} threads...")
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        threads.append(t)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping simulation...")

if __name__ == "__main__":
    run_simulation()
