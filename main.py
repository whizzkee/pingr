import requests, schedule, time, json, datetime, os

# Load config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

URLS = CONFIG["urls"]
INTERVAL = CONFIG["interval_seconds"]

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/status.log"

def log(message: str):
    """Write messages to both console and log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def check_url(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        duration = time.time() - start
        return (url, response.status_code, round(duration, 2))
    except Exception as e:
        return (url, None, str(e))
    