import requests, schedule, time, json, datetime, os
from colorama import Fore, Style, init

init(autoreset=True, convert=True)

# Load config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

URLS = CONFIG["urls"]
INTERVAL = CONFIG["interval_seconds"]

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/status.log"

def log(message: str, color=Fore.WHITE):
    """Write messages to both console and log file with color support."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {message}"
    print(color + line + Style.RESET_ALL)
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

def job():
    for url in URLS:
        url, status, info = check_url(url)
        if status == 200:
            log(f"{url} is UP - {info}s", Fore.GREEN)
        else:
            log(f"{url} is DOWN - {info}", Fore.RED)
            if CONFIG["alert"]["method"] == "discord":
                send_discord_alert(url, info)
            
def send_discord_alert(url, info):
    webhook_url = CONFIG["alert"]["webhook_url"]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = {
        "content": (
            f"⚠️ **Site is DOWN**\n"
            f"**URL:** {url}\n"
            f"**Time:** {timestamp}\n"
            f"**Details:** `{info}`"
        )
    }

    try:
        requests.post(webhook_url, json=message)
        log(f"Discord alert sent for {url}", Fore.YELLOW)
    except Exception as e:
        log(f"Failed to send Discord alert: {e}", Fore.RED)


schedule.every(INTERVAL).seconds.do(job)

log(f"Monitoring {len(URLS)} URLS every {INTERVAL} seconds...", Fore.CYAN)

while True:
    schedule.run_pending()
    time.sleep(1)