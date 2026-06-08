FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl

WORKDIR /app

COPY agents/pesquisador_agent/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY agents/pesquisador_agent ./agents/pesquisador_agent

CMD ["uvicorn", "agents.pesquisador_agent.server:app", "--host", "0.0.0.0", "--port", "8000"]

