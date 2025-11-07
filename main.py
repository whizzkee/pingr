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

STATUS_CACHE = {}

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
        previous_status = STATUS_CACHE.get(url)
        
        if status == 200:
            log(f"{url} is UP - {info}s", Fore.GREEN)
        else:
            log(f"{url} is DOWN - {info}", Fore.RED)
            
        #Only send alert if status has changed
        if previous_status != status:
            STATUS_CACHE[url] = status
            if CONFIG["alert"]["method"] == "discord":
                send_discord_alert(url, status, info)
            
def send_discord_alert(url, status, info):
    webhook_url = CONFIG["alert"]["webhook_url"]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if status == 200:
        title = "✅ Site is BACK UP"
        color = 0x00FF00
        description = f"The site is back up"
    else:
        title = "⚠️ Site is DOWN"
        color = 0xFF0000
        description = f"The site failed to respond or returned an error"
    
    embed = {
        "title": title,
        "color": color, 
        "fields": [
            {"name": "URL", "value": url, "inline": False},
            {"name": "Time", "value": timestamp, "inline": False},
            {"name": "Details", "value": str(info), "inline": False},
        ],
        "footer": {"text": "Pingr Status Monitor"},
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            log(f"Discord embed alert sent for {url}", Fore.YELLOW)
        else:
            log(f"Discord alert failed with status code {response.status_code}", Fore.RED)
    except Exception as e:
        log(f"Failed to send Discord embed alert: {e}", Fore.RED)

schedule.every(INTERVAL).seconds.do(job)

log(f"Monitoring {len(URLS)} URLS every {INTERVAL} seconds...", Fore.CYAN)

while True:
    schedule.run_pending()
    time.sleep(1)