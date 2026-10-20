#!/usr/bin/env bash
# Build phase: NO database access — Render internal DB hostname is not
# reachable during builds. All DB operations run at start time via render.yaml.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input