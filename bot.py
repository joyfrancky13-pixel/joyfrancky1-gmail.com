import requests
from datetime import datetime

# --- METS TES CODES ICI ---
TELEGRAM_BOT_TOKEN = "8845238869:AAGZsQmuz-Dq7zYVspSILM8w_lht4N5Ecow"
TELEGRAM_CHAT_ID = "6009299818"
RAPIDAPI_KEY = "2be02ee8f8mshcd607db0595c057p1e06e5jsnd65eb69b4d0a"
# --------------------------

def get_matches():
    """Récupère matchs via SportAPI7 sur RapidAPI"""
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://sportapi7.p.rapidapi.com/api/v1/category/1/scheduled-events/{today}"
    
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "sportapi7.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        matches = []
        events = data.get("events", data.get("data", []))
        
        if not events:
            return [{"home": "Aucun match", "away": "aujourd'hui", "league": "Test", "time": "20:00"}]
        
        for event in events[:5]: # 5 matchs max
            home = event["homeTeam"]["name"]
            away = event["awayTeam"]["name"]
            league = event["tournament"]["name"]
            time = event["startTime"][11:16]
            
            matches.append({
                "home": home,
                "away": away, 
                "league": league,
                "time": time
            })
        return matches
    
    except Exception as e:
        print(f"Erreur SportAPI7: {e}")
        return [{"home": "Arsenal", "away": "Chelsea", "league": "Test", "time": "20:00"}]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    r = requests.post(url, data=data)
    print(f"Status Telegram: {r.status_code}")

def main():
    matches = get_matches()
    msg = f"⚽ *Matchs du jour {datetime.now().strftime('%d/%m/%Y')}*\n\n"
    
    for m in matches:
        msg += f"*{m['home']}* vs *{m['away']}*\n"
        msg += f"🏆 {m['league']} | ⏰ {m['time']}\n\n"
    
    send_telegram(msg)
    print("Message Telegram envoyé")

if __name__ == "__main__":
    main()
