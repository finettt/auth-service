#!/bin/sh
uvicorn gateway:gateway --host 0.0.0.0 --port 443 --ssl-certfile .ssl/cert.pem --ssl-keyfile .ssl/key.pem --workers 4
