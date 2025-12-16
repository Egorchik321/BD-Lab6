#!/bin/bash
# Запуск Spark job с dynamic allocation

JOB_SCRIPT=$1
MASTER=${2:-"spark://spark-master:7077"}

echo "=== Запуск Spark Job с Dynamic Allocation ==="
echo "Job: $JOB_SCRIPT"
echo "Master: $MASTER"
echo ""

# Загрузка конфигурации
CONFIG_FILE="spark-dynamic.conf"
if [ -f "$CONFIG_FILE" ]; then
    CONFIG_OPTIONS=""
    while IFS='=' read -r key value; do
        # Пропускаем комментарии и пустые строки
        [[ $key =~ ^#.* ]] && continue
        [[ -z $key ]] && continue
        CONFIG_OPTIONS="$CONFIG_OPTIONS --conf $key=$value"
    done < "$CONFIG_FILE"
    echo "Загружена конфигурация из $CONFIG_FILE"
fi

# Команда запуска
docker exec lab-6-test-spark-master-1 \
    /opt/spark/bin/spark-submit \
    --master $MASTER \
    --deploy-mode cluster \
    --name "DynamicAllocationJob_$(date +%Y%m%d_%H%M%S)" \
    $CONFIG_OPTIONS \
    --conf "spark.driver.memory=1g" \
    --conf "spark.executor.memory=2g" \
    --conf "spark.executor.cores=1" \
    --class "org.apache.spark.examples.SparkPi" \
    /opt/spark/examples/jars/spark-examples_2.12-3.5.0.jar 1000

# Мониторинг масштабирования
echo ""
echo "=== Мониторинг Dynamic Allocation ==="
echo "Ожидание 10 секунд для масштабирования..."
sleep 10

# Проверка количества executors
echo "Текущее состояние кластера:"
docker exec lab-6-test-spark-master-1 \
    curl -s http://localhost:8080 | grep -A5 "Alive Workers"