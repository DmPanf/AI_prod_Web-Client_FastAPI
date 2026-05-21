#!/bin/bash
pip install -qr requirements.txt
pip list
nohup uvicorn app:app --host 0.0.0.0 --port 8001 --reload &
