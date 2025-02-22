import asyncio
import logging
import re
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message
from info import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, CHANNEL_ID, START_URL, db

# Initialize bot
app = Client("movie_scraper_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Regex patterns
HOWBLOGS_PATTERN = re.compile(r"https://howblogs\.xyz/[^\s]+")
GOFILE_PATTERN = re.compile(r"https://gofile\.io/[^\s]+")
STREAMTAPE_PATTERN = re.compile(r"https://streamtape\.to/[^\s]+")

async def scrape_movies():
    while True:
        try:
            response = requests.get(START_URL, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            latest_movies = soup.find_all("div", class_="fmvideo")

            for movie in latest_movies:
                movie_name = movie.find("a").text.strip()
                movie_link = movie.find("a")["href"]

                if db.is_movie_scraped(movie_name):
                    continue  # Skip if already scraped

                movie_page = requests.get(movie_link, timeout=10)
                howblogs_links = HOWBLOGS_PATTERN.findall(movie_page.text)

                for howblogs_link in howblogs_links:
                    howblogs_page = requests.get(howblogs_link, timeout=10)
                    gofile_links = GOFILE_PATTERN.findall(howblogs_page.text)
                    streamtape_links = STREAMTAPE_PATTERN.findall(howblogs_page.text)

                    all_links = gofile_links + streamtape_links
                    if all_links:
                        for link in all_links:
                            db.insert_movie(movie_name, link)
                            await app.send_message(CHANNEL_ID, f"🎬 **{movie_name}**\n🔗 {link}")

        except Exception as e:
            logger.error(f"Error in scraping: {e}")

        await asyncio.sleep(300)  # Wait 5 minutes before next scrape

@app.on_message(filters.command("update_domain") & filters.user(OWNER_ID))
async def update_domain(_, message: Message):
    global START_URL
    try:
        new_url = message.text.split(" ", 1)[1].strip()
        START_URL = new_url
        db.update_domain(new_url)
        await message.reply_text(f"✅ Domain updated to {new_url}")
    except IndexError:
        await message.reply_text("❌ Usage: /update_domain {new_website_url}")

@app.on_message(filters.command("recent") & filters.private)
async def recent_links(_, message: Message):
    recent_movies = db.get_recent_movies(10)
    if not recent_movies:
        await message.reply_text("No recent links found.")
        return

    text = "\n".join([f"{i+1}. {name} = [ {link} ]" for i, (name, link) in enumerate(recent_movies)])
    await message.reply_text(text)

if __name__ == "__main__":
    app.start()
    asyncio.run(scrape_movies())
    app.stop()
