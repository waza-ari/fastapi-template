#! /usr/bin/env bash

# Create files directory if it doesn't exist
mkdir -p /app/files
mkdir -p /app/files/corona_tests
mkdir -p /app/files/documents
mkdir -p /app/files/invoices

# Run migrations
alembic upgrade head
