FROM confluentinc/cp-kafka:latest

# Оптимизация памяти JVM
ENV KAFKA_HEAP_OPTS="-Xmx1g -Xms1g"
ENV KAFKA_JVM_PERFORMANCE_OPTS="-XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35"