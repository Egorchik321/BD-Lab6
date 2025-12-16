#!/bin/bash

echo "=== Проверка оркестрации Big Data-приложений ==="
echo "Время проверки: $(date)"
echo ""

# Функция проверки сервиса
check_service() {
    local name=$1
    local host=$2
    local port=$3
    local endpoint=$4
    
    echo -n "✓ $name: "
    if curl -s -f "http://${host}:${port}${endpoint}" > /dev/null; then
        echo "ДОСТУПЕН"
        return 0
    else
        echo "НЕДОСТУПЕН"
        return 1
    fi
}

# Проверка Spark
echo "--- Spark Cluster ---"
check_service "Spark Master UI" "localhost" "8080" ""
check_service "Spark Worker 1" "localhost" "8081" ""
check_service "Spark Worker 2" "localhost" "8082" ""
check_service "Spark History Server" "localhost" "18080" ""

# Проверка Flink
echo ""
echo "--- Flink Cluster ---"
check_service "Flink JobManager" "localhost" "8083" ""
echo -n "✓ Flink TaskManagers: "
if docker-compose -f docker-compose.full.yml ps | grep flink-taskmanager | grep Up | wc -l | grep -q "2"; then
    echo "2 ЗАПУЩЕНО"
else
    echo "НЕ ВСЕ ЗАПУЩЕНЫ"
fi

# Проверка Kafka
echo ""
echo "--- Kafka Cluster ---"
echo -n "✓ Kafka Brokers: "
kafka_count=$(docker-compose -f docker-compose.full.yml ps | grep kafka- | grep Up | wc -l)
echo "$kafka_count ЗАПУЩЕНО"

# Проверка Redis
echo ""
echo "--- Redis ---"
echo -n "✓ Redis: "
if docker-compose -f docker-compose.full.yml exec -T redis redis-cli ping | grep -q PONG; then
    echo "РАБОТАЕТ (PONG)"
else
    echo "НЕ РАБОТАЕТ"
fi

# Проверка ML Server
echo ""
echo "--- ML Model Server ---"
check_service "ML Server Health" "localhost" "5000" "/health"

# Проверка мониторинга
echo ""
echo "--- Monitoring Stack ---"
check_service "Prometheus" "localhost" "9090" "/metrics"
check_service "Grafana" "localhost" "3000" "/api/health"

# Запуск тестового Spark job
echo ""
echo "--- Запуск тестового Spark Job ---"
docker-compose -f docker-compose.full.yml exec spark-master \
    /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --deploy-mode cluster \
    --name "TestRecommendationJob" \
    --conf "spark.executor.instances=2" \
    --conf "spark.executor.memory=2g" \
    --conf "spark.driver.memory=1g" \
    /opt/spark/work-dir/test-job.py 2>&1 | tail -20

echo ""
echo "=== Проверка завершена ==="