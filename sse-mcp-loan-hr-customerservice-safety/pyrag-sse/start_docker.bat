@echo off
REM Docker build and run script for Windows CMD

echo Building and starting MSSQL MCP SSE Server with Docker...

REM Check if .env file exists
IF NOT EXIST ".env" (
    echo Creating .env file...
    copy .env.example .env
)

REM Build and start containers
docker compose build --no-cache
docker compose up
