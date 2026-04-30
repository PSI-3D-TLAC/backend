# Server

Simple Flask server. All endpoints are stubs; they will later delegate to
`src/core` once the core API is available.

## Install

```
pip install flask
```

## Run

From the project root:

```
python -m src.server.run
```

The server listens on `http://127.0.0.1:5000`.

## Endpoints

- `GET  /health`

