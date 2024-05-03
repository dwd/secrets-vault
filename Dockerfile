FROM python:3-slim AS builder

RUN pip install pipenv

WORKDIR /deps
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv requirements >requirements.txt

WORKDIR /app
COPY main.py /app
COPY gh /app

RUN pip install --target=/app -r /deps/requirements.txt

# A distroless container image with Python and some basics like SSL certificates
# https://github.com/GoogleContainerTools/distroless
FROM gcr.io/distroless/python3-debian10
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]
