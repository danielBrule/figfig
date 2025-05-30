FROM python:3.11-slim


RUN apt-get update && apt-get install -y unixodbc unixodbc-dev libodbc1 odbcinst gnupg2 curl
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17



WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .  

COPY db/  ./db/
COPY db/database.py  ./db/database.py
COPY db/init_db.py  ./db/init_db.py
COPY db/models.py  ./db/models.py

COPY app/ ./app/


RUN ls -la ./db
WORKDIR /code/db/

RUN python /code/db/init_db.py > result.txt

CMD ["python", "app/main.py"]
