FROM python:3.11-slim


RUN apt-get update && apt-get install -y unixodbc unixodbc-dev libodbc1 odbcinst gnupg2 curl
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17



WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .  

COPY src/  ./src/

COPY src/db             ./src/db
COPY src/db/models.py   ./db/models.py
COPY src/db/database.py ./db/database.py

COPY src/scrapers  ./src/scrapers
COPY src/scrapers/scrap_1_get_daily_urls.py               ./src/scrapers/scrap_1_get_daily_urls.py
COPY src/scrapers/scrap_2_get_articles_primary_info.py    ./src/scrapers/scrap_2_get_articles_primary_info.py
COPY src/scrapers/scrap_3_get_articles_secondary_info.py  ./src/scrapers/scrap_3_get_articles_secondary_info.py
COPY src/scrapers/scrap_4_get_comments.py                 ./src/scrapers/scrap_4_get_comments.py


COPY src/utils               ./src/utils
COPY src/utils/helpers.py    ./src/utils/helpers.py
COPY src/utils/log.py        ./src/utils/log.py
COPY src/utils/constants.py  ./src/utils/constants.py

COPY src/init_db.py  ./src/init_db.py




WORKDIR /code/src

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# RUN python init_db.py > result.txt
# CMD ["python", "app/main.py"]
