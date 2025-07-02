FROM python:3.11-slim

# Build argument for environment (dev/prod)
ARG ENV=dev
ENV APP_ENV=${ENV}

# System dependencies
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev libodbc1 odbcinst gnupg2 curl
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list -o /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /code

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy environment-specific .env
COPY docker/docker.env.${ENV} .env

# Copy source code
COPY src/ ./src/ 

# Entry point setup
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use an explicit working directory for app run
WORKDIR /code/src
ENV PYTHONPATH=/code/src
ENTRYPOINT ["/entrypoint.sh"]