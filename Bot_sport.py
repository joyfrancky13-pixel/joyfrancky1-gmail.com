import telebot
import requests

# 🔑 Vos clés d'accès réelles
TOKEN_TELEGRAM = "8941502684:AAGGo0w1njEw0VDEgtKiBWBIDTnHRKTiiqM"
RAPIDAPI_KEY = "2be02ee8f8mshcd607db0595c057p1e06e5jsnd65eb69b4d0a"

bot = telebot.TeleBot(TOKEN_TELEGRAM)

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "sportapi7.p.rapidapi.com"
}

def chercher_equipe_football(nom_equipe):
    """
    Recherche une équipe sur SportAPI7 et retourne son ID unique et son vrai nom.
    """
    url = "https://sportapi7.p.rapidapi.com/api/v1/search/teams"
    querystring = {"q": nom_equipe}
    
    try:
        response = requests.get(url, headers=HEADERS, params=querystring)
        data = response.json()
        
        # Filtrer pour s'assurer qu'on prend une équipe de football (sport id 1 généralement)
        if data.get('teams'):
            for team in data['teams']:
                if team.get('sport', {}).get('id') == 1: # 1 = Football
                    return team['id'], team['name']
            # Si pas de filtre sport, on prend le premier résultat
            return data['teams'][0]['id'], data['teams'][0]['name']
        return None, None
    except Exception as e:
        print(f"Erreur recherche équipe : {e}")
        return None, None

def recuperer_derniers_resultats(team_id):
    """
    Récupère les derniers matchs joués par l'équipe pour analyser sa forme.
    """
    url = f"https://sportapi7.p.rapidapi.com/api/v1/team/{team_id}/events/last/5"
    
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        
        historique = []
        for event in data.get('events', []):
            # On vérifie que le match est bien terminé
            if event.get('status', {}).get('type') == 'finished':
                score_home = event['homeScore'].get('current', 0)
                score_away = event['awayScore'].get('current', 0)
                
                if event['homeTeam']['id'] == team_id:
                    if score_home > score_away: historique.append('V')
                    elif score_home < score_away: historique.append('D')
                    else: historique.append('N')
                else:
                    if score_away > score_home: historique.append('V')
                    elif score_away < score_home: historique.append('D')
                    else: historique.append('N')
        return historique
    except Exception as e:
        print(f"Erreur historique : {e}")
        return []

def calculer_forme(historique):
    points = 0
    for res in historique:
        if res == 'V': points += 3
        elif res == 'N': points += 1
    max_points = len(historique) * 3
    if max_points == 0: return 0
    return round((points / max_points) * 100, 2)

# --- GESTION DES COMMANDES TELEGRAM ---

@bot.message_handler(commands=['start'])
def bienvenue(message):
    msg = (
        "🤖 *Votre Bot SportAPI7 est en ligne !*\n\n"
        "Envoyez le nom de deux équipes séparées par 'vs' pour obtenir le pronostic.\n"
        "👉 *Exemple :* `Arsenal vs Chelsea` ou `Real Madrid vs Barcelona`"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def analyser_match(message):
    texte = message.text
    if " vs " not in texte.lower():
        bot.reply_to(message, "⚠️ Format requis : `Équipe A vs Équipe B`")
        return
        
    parties = texte.split(" vs " if " vs " in texte else " VS ")
    eq_dom, eq_ext = parties[0].strip(), parties[1].strip()
    
    bot.send_message(message.chat.id, f"🔍 Analyse de *{eq_dom} vs {eq_ext}* en cours...", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'typing')
    
    id_dom, nom_dom = chercher_equipe_football(eq_dom)
    id_ext, nom_ext = chercher_equipe_football(eq_ext)
    
    if not id_dom or not id_ext:
        bot.send_message(message.chat.id, "❌ Une des deux équipes n'a pas été trouvée. Essayez d'écrire son nom complet en anglais.")
        return
        
    hist_dom = recuperer_derniers_resultats(id_dom)
    hist_ext = recuperer_derniers_resultats(id_ext)
    
    forme_dom = calculer_forme(hist_dom)
    forme_ext = calculer_forme(hist_ext)
    diff = forme_dom - forme_ext
    
    reponse = f"🏟️ *{nom_dom} vs {nom_ext}*\n\n"
    reponse += f"🏠 *{nom_dom}* (Forme : {', '.join(hist_dom)}) ➡️ *{forme_dom}%*\n"
    reponse += f"🚀 *{nom_ext}* (Forme : {', '.join(hist_ext)}) ➡️ *{forme_ext}%*\n\n"
    
    if abs(diff) < 15:
        reponse += "🔮 *Pronostic* : Match très serré. Option double chance recommandée."
    elif diff >= 15:
        reponse += f"🔮 *Pronostic* : Avantage statistique pour *{nom_dom}*."
    else:
        reponse += f"🔮 *Pronostic* : Avantage statistique pour *{nom_ext}*."
        
    bot.send_message(message.chat.id, reponse, parse_mode="Markdown")

print("🚀 Bot en cours d'exécution sur votre jeton Telegram...")
bot.infinity_polling()
