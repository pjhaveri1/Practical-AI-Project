FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    postgresql-server-dev-all \
    && rm -rf /var/lib/apt/lists/*

# Create data directory for mounting volume
RUN mkdir -p /app/data

# Download the recipes.parquet file
RUN curl -o /app/data/recipes.parquet https://elasticbeanstalk-ap-southeast-1-535139857701.s3.ap-southeast-1.amazonaws.com/recipes.parquet

# Copy the current application files
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]