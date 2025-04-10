FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libsasl2-dev libsasl2-modules gettext && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Cache dependencies
COPY pyproject.toml uv.lock* ./
RUN pip install --upgrade pip && pip install uv && uv venv && uv sync

# Create a non-root user
RUN useradd --create-home appuser
USER appuser

# Set the working directory
WORKDIR /home/appuser

# Copy application files
COPY --chown=appuser:appuser . .

RUN msgfmt ./app/i18n/locales/en/LC_MESSAGES/messages.po \
    -o ./app/i18n/locales/en/LC_MESSAGES/messages.mo && \
    msgfmt ./app/i18n/locales/pt/LC_MESSAGES/messages.po \
    -o ./app/i18n/locales/pt/LC_MESSAGES/messages.mo

CMD [".venv/bin/alembic", "upgrade", "head"] && \
    [".venv/bin/uvicorn", "app.main:app", "--port", "8080", "--host", "0.0.0.0"]
