import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from datetime import datetime
from pyrogram import Client, filters
from EQUROBOT import app

  
def google_dork(dork_query, num_results=10):
    query = urllib.parse.quote_plus(dork_query)
    url = f"https://www.google.com/search?q={query}&num={num_results}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title = g.find('h3').text
                description = g.find('span', class_='aCOpRe').text
                results.append({
                    'title': title,
                    'link': link,
                    'description': description
                })

        return results
    else:
        print(f"Error: Unable to fetch results. Status code: {response.status_code}")
        return None

@app.on_message(filters.command("dork") & filters.private)
def dork(client, message):
    query = message.text.split(" ", 1)
    if len(query) == 1:
        message.reply_text("🚫 𝗣𝗹𝗲𝗮𝘀𝗲 𝗽𝗿𝗼𝘃𝗶𝗱𝗲 𝗮 𝘀𝗲𝗮𝗿𝗰𝗵 𝗾𝘂𝗲𝗿𝘆.\n\n /dork <your_query>")
        return

    dork_query = query[1]
    start_time = time.time()
    results = google_dork(dork_query)
    end_time = time.time()

    if results:
        results_text = "\n".join([f"{idx + 1}. [{res['title']}]({res['link']})" for idx, res in enumerate(results)])
        time_taken = end_time - start_time
        caption = (f"┏━━━━━━━⍟\n"
                   f"┃ 𝗗𝗼𝗿𝗸𝗲𝗱 URLs 𝗵𝗲𝗿𝗲 ✅\n"
                   f"┗━━━━━━━━━━━━━━⊛\n"
                   f"⊙ 𝗧𝗶𝗺𝗲 𝗧𝗮𝗸𝗲𝗻 : {time_taken:.2f} seconds\n"
                   f"⊙ 𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗲𝗱 𝗯𝘆 : {message.from_user.first_name}\n\n"
                   f"{results_text}")
        message.reply_text(caption, disable_web_page_preview=True)
    else:
        message.reply_text("No results found.")
