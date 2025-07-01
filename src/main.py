import os
import subprocess

SCRAPER = os.getenv("SCRAPER")

if SCRAPER == "scraper_dailyurl":
    subprocess.run(["python", "src/scrapers/scrap_1_get_daily_urls.py"])
elif SCRAPER == "scraper_articles_primary_info":
    subprocess.run(["python", "src/scrapers/scrap_2_get_articles_primary_info.py"])
elif SCRAPER == "scraper_articles_secondary_info":
    subprocess.run(["python", "src/scrapers/scrap_3_get_articles_secondary_info.py"])
elif SCRAPER == "scraper_comments":
    subprocess.run(["python", "src/scrapers/scrap_4_get_comments.py"])
else:
    raise ValueError(f"Unknown SCRAPER type: {SCRAPER}")
