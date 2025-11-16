#!/bin/bash

echo -e "Нагрузочное тестирование\n"

if ! curl -s http://localhost:8080/health > /dev/null; then
    echo -e "Сервис не доступен на http://localhost:8080\n"
    exit 1
fi

RESULTS_DIR="load_test_results"
mkdir -p "$RESULTS_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="$RESULTS_DIR/results_$TIMESTAMP.html"
CSV_FILE="$RESULTS_DIR/stats_$TIMESTAMP.csv"


locust -f locustfile.py \
    --host=http://localhost:8080 \
    -u 200 \
    -r 15 \
    -t 5m \
    --headless \
    --html "$RESULTS_FILE" \
    --csv "$RESULTS_DIR/stats_$TIMESTAMP" \
    --loglevel INFO

if [ $? -eq 0 ]; then
    echo -e "\nТестирование завершено\n"
    echo -e "HTML отчет: $RESULTS_FILE"
fi
