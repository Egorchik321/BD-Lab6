FROM redis:alpine

# Создание конфигурационного файла
RUN mkdir -p /usr/local/etc/redis
RUN echo "maxmemory 1gb" > /usr/local/etc/redis/redis.conf \
    && echo "maxmemory-policy allkeys-lru" >> /usr/local/etc/redis/redis.conf

# Запуск Redis с конфигом
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]