FROM python:3.13-slim

RUN apt-get update && apt-get install -y\
    build-essential \
    curl

WORKDIR /app

COPY agents/redator_agent/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY agents/redator_agent ./agents/redator_agent 

CMD ["uvicorn", "agents.redator_agent.server:app", "--host", "0.0.0.0", "--port", "8000"]