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
        # SportAPI7 renvoie "events" ou "data" selon le plan
        events = data.get("events", data.get("data", []))
        
        for event in events[:5]: # 5 matchs max
            home = event["homeTeam"]["name"]
            away = event["awayTeam"]["name"]
            league = event["tournament"]["name"]
            time = event["startTime"][11:16] # HH:MM
            
            matches.append({
                "home": home,
                "away": away, 
                "league": league,
                "time": time
            })
        return matches if matches else []
    
    except Exception as e:
        print(f"Erreur SportAPI7: {e}")
        return [{"home": "Arsenal", "away": "Chelsea", "league": "Test", "time": "20:00"}]
