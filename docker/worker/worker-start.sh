#! /usr/bin/env sh
set -e

# Sleep 1m to allow the regular backend to perform migrations if needed
echo "Sleeping for 60 seconds to allow the regular backend to perform migrations if needed"
sleep 60

exec arq worker.main.WorkerSettings
