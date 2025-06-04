FROM python:3.11-slim


RUN apt-get update && apt-get install -y unixodbc unixodbc-dev libodbc1 odbcinst gnupg2 curl
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17



WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .  

COPY code/  ./code/
COPY code/db  ./code/db
COPY code/db/database.py  ./db/database.py
COPY code/db/models.py  ./db/models.py

COPY code/scrapers ./code/scrapers
COPY code/scrapers/daily_urls.py ./code/scrapers/daily_urls.py


COPY code/utils  ./code/utils
COPY code/utils/helpers.py  ./code/utils/helpers.py
COPY code/utils/log.py  ./code/utils/log.py

COPY code/init_db.py  ./code/init_db.py




RUN ls -lahR /code
WORKDIR /code/code
RUN python init_db.py > result.txt

CMD ["python", "app/main.py"]
