FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libsasl2-dev libsasl2-modules gettext && apt-get install -y vim   && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home appuser
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

# Cache dependencies
COPY pyproject.toml uv.lock* ./
RUN pip install --upgrade pip && pip install uv

WORKDIR /home/appuser
# Required in order to avoid "uv sync" creating a new venv
ENV UV_PROJECT_ENVIRONMENT=/home/appuser/.venv
RUN uv venv .venv && uv sync

# Copy application files
COPY --chown=appuser:appuser . ./limoeiro/
WORKDIR /home/appuser/limoeiro

RUN msgfmt ./app/i18n/locales/en/LC_MESSAGES/messages.po \
    -o ./app/i18n/locales/en/LC_MESSAGES/messages.mo && \
    msgfmt ./app/i18n/locales/pt/LC_MESSAGES/messages.po \
    -o ./app/i18n/locales/pt/LC_MESSAGES/messages.mo

# Create a startup script
COPY --chown=appuser:appuser start.sh /home/appuser/start.sh
RUN chmod +x /home/appuser/start.sh

CMD ["/home/appuser/start.sh"]
