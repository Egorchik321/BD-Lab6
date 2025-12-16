#!/bin/bash

echo "=== Запуск оптимизаций управления ресурсами ==="
echo ""

# 1. Настройка YARN Capacity Scheduler
echo "1. Настройка YARN Capacity Scheduler..."
docker-compose -f capacity-scheduler-emulation.yml up -d
sleep 5
./queue-manager.sh monitor
echo "YARN настроен"

# 2. Настройка Dynamic Allocation
echo ""
echo "2. Настройка Dynamic Allocation в Spark..."
cp spark-dynamic.conf /tmp/
./run-spark-dynamic.sh /opt/spark/examples/jars/spark-examples_2.12-3.5.0.jar
echo "Dynamic Allocation настроен"

# 3. Запуск KEDA эмулятора
echo ""
echo "3. Запуск KEDA эмулятора для autoscaling..."
docker-compose -f keda-emulation.yml up -d &
sleep 3
echo " KEDA эмулятор запущен"

# 4. Настройка Spot стратегии
echo ""
echo "4. Настройка стратегии spot инстансов..."
docker-compose -f spot-strategy.yml up -d
sleep 5
echo "Spot стратегия применена"

# 5. Расчет экономии
echo ""
echo "5. Расчет экономии от оптимизаций..."
python3 cost-calculator.py
echo "Расчет экономии завершен"

# 6. Storage Tiering оптимизация
echo ""
echo "6. Применение storage tiering..."
python3 storage-tiering.py
echo "Storage tiering применен"

# 7. Генерация графика
echo ""
echo "7. Генерация графика снижения затрат..."
python3 cost-reduction-chart.py
echo "График сгенерирован"

echo ""
echo "=== Все оптимизации успешно применены ==="
echo "Отчеты сохранены в файлах:"
echo "  • cost-optimization-report.json"
echo "  • storage-tiering-report.json"
echo "  • cost-reduction-data.json"
echo "  • cost-reduction-chart.png"
echo ""
echo "Для мониторинга используйте:"
echo "  ./queue-manager.sh monitor"
echo "  python3 keda-emulator.py"