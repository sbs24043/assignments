FROM --platform=linux/arm64/v8 flwr/clientapp:1.17.0

WORKDIR /app
COPY pyproject.toml .
RUN sed -i 's/.*flwr\[simulation\].*//' pyproject.toml \
    && python -m pip install -U --no-cache-dir .

ENTRYPOINT ["flwr-clientapp"]