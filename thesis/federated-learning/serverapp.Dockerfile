FROM flwr/serverapp:1.16.0.dev20250305

WORKDIR /app

COPY pyproject.toml .
RUN sed -i 's/.*flwr\[simulation\].*//' pyproject.toml \
   && python -m pip install -U --no-cache-dir .

RUN 
ENTRYPOINT ["flwr-serverapp"]