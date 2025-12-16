# Используем официальный образ Apache Spark с Python
FROM apache/spark:3.5.0-python3

# Оптимизация для контейнеров (оставляем вашу настройку)
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"

# Установка Python зависимостей с правами root, затем возврат к пользователю spark
USER root
RUN pip install pandas numpy scikit-learn
USER 185

# Создание рабочей директории
WORKDIR /opt/spark/work-dir