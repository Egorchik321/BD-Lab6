#!/bin/bash
# Управление ресурсами по очередям YARN

echo "=== YARN Capacity Scheduler Emulation ==="
echo "Очередь ETL: 60% ресурсов"
echo "Очередь ML: 30% ресурсов"
echo "Очередь Default: 10% ресурсов"
echo ""

# Мониторинг использования ресурсов
monitor_resources() {
    echo "Текущее использование ресурсов:"
    echo "--------------------------------"
    
    # ETL queue
    etl_cpu=$(docker stats --no-stream --format "{{.CPUPerc}}" spark-etl-master-1 2>/dev/null | sed 's/%//') || etl_cpu=0
    etl_mem=$(docker stats --no-stream --format "{{.MemUsage}}" spark-etl-master-1 2>/dev/null | cut -d'/' -f1 | sed 's/[^0-9.]//g') || etl_mem=0
    
    # ML queue
    ml_cpu=$(docker stats --no-stream --format "{{.CPUPerc}}" spark-ml-master-1 2>/dev/null | sed 's/%//') || ml_cpu=0
    ml_mem=$(docker stats --no-stream --format "{{.MemUsage}}" spark-ml-master-1 2>/dev/null | cut -d'/' -f1 | sed 's/[^0-9.]//g') || ml_mem=0
    
    # Default queue
    def_cpu=$(docker stats --no-stream --format "{{.CPUPerc}}" spark-default-master-1 2>/dev/null | sed 's/%//') || def_cpu=0
    def_mem=$(docker stats --no-stream --format "{{.MemUsage}}" spark-default-master-1 2>/dev/null | cut -d'/' -f1 | sed 's/[^0-9.]//g') || def_mem=0
    
    echo "ETL Queue: CPU=${etl_cpu}%, Memory=${etl_mem}MB"
    echo "ML Queue:  CPU=${ml_cpu}%, Memory=${ml_mem}MB"
    echo "Default:   CPU=${def_cpu}%, Memory=${def_mem}MB"
    
    # Проверка лимитов
    check_limits() {
        queue=$1
        cpu_usage=$2
        mem_usage=$3
        cpu_limit=$4
        mem_limit=$5
        
        if (( $(echo "$cpu_usage > $cpu_limit" | bc -l) )); then
            echo "⚠️  $queue: Превышение CPU лимита! ${cpu_usage}% > ${cpu_limit}%"
        fi
        
        if (( $(echo "$mem_usage > $mem_limit * 1024" | bc -l) )); then
            echo "⚠️  $queue: Превышение Memory лимита! ${mem_usage}MB > $(echo "$mem_limit * 1024" | bc)MB"
        fi
    }
    
    echo ""
    echo "Проверка лимитов:"
    check_limits "ETL" "$etl_cpu" "$etl_mem" "60" "9.6"
    check_limits "ML" "$ml_cpu" "$ml_mem" "30" "4.8"
    check_limits "Default" "$def_cpu" "$def_mem" "10" "1.6"
}

# Запуск Job с указанием очереди
submit_job() {
    queue=$1
    job_script=$2
    
    case $queue in
        "etl")
            master="spark://spark-etl-master:7077"
            echo "Отправка job в очередь ETL..."
            ;;
        "ml")
            master="spark://spark-ml-master:7078"
            echo "Отправка job в очередь ML..."
            ;;
        "default")
            master="spark://spark-default-master:7079"
            echo "Отправка job в очередь Default..."
            ;;
        *)
            echo "Неизвестная очередь: $queue"
            exit 1
            ;;
    esac
    
    docker exec spark-etl-master-1 \
        /opt/spark/bin/spark-submit \
        --master $master \
        --deploy-mode client \
        $job_script
}

# Основное меню
case $1 in
    "monitor")
        monitor_resources
        ;;
    "submit")
        submit_job $2 $3
        ;;
    *)
        echo "Использование: $0 {monitor|submit queue script.py}"
        echo "Примеры:"
        echo "  $0 monitor"
        echo "  $0 submit etl /opt/spark/work-dir/etl-job.py"
        ;;
esac