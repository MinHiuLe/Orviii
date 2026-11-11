# ---- build stage: install the app and its dependencies into a venv ----
FROM python:3.12-slim AS build
WORKDIR /src
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .

# ---- runtime stage: only the venv, non-root user ----
FROM python:3.12-slim
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
RUN useradd --system --uid 10001 --no-create-home app
COPY --from=build /opt/venv /opt/venv
WORKDIR /app
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
