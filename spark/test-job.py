from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg
import time

def main():
    # Создание Spark сессии
    spark = SparkSession.builder \
        .appName("ECommerceRecommendations") \
        .config("spark.sql.shuffle.partitions", "10") \
        .config("spark.dynamicAllocation.enabled", "true") \
        .config("spark.dynamicAllocation.minExecutors", "1") \
        .config("spark.dynamicAllocation.maxExecutors", "4") \
        .getOrCreate()
    
    # Логирование начала работы
    print(f"=== Starting Spark Job at {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Spark Version: {spark.version}")
    print(f"Master URL: {spark.sparkContext.master}")
    
    try:
        # Тестовые данные для рекомендательной системы
        data = [
            (1, "user_001", "product_A", 5.0, "view"),
            (2, "user_001", "product_B", 4.5, "purchase"),
            (3, "user_002", "product_A", 3.0, "view"),
            (4, "user_002", "product_C", 5.0, "purchase"),
            (5, "user_003", "product_B", 2.5, "view"),
            (6, "user_003", "product_D", 4.0, "cart"),
            (7, "user_004", "product_A", 4.5, "purchase"),
            (8, "user_004", "product_E", 3.5, "view"),
            (9, "user_005", "product_C", 5.0, "purchase"),
            (10, "user_005", "product_F", 4.0, "view")
        ]
        
        columns = ["id", "user_id", "product_id", "rating", "event_type"]
        
        # Создание DataFrame
        df = spark.createDataFrame(data, columns)
        
        print("\n=== Data Sample ===")
        df.show(5)
        
        print("\n=== DataFrame Schema ===")
        df.printSchema()
        
        # Аналитика пользователей
        print("\n=== User Analytics ===")
        user_stats = df.groupBy("user_id") \
            .agg(
                count("*").alias("total_events"),
                count(col("event_type") == "purchase").alias("purchases"),
                avg("rating").alias("avg_rating")
            ) \
            .orderBy("user_id")
        
        user_stats.show()
        
        # Аналитика продуктов
        print("\n=== Product Analytics ===")
        product_stats = df.groupBy("product_id") \
            .agg(
                count("*").alias("total_views"),
                count(col("event_type") == "purchase").alias("total_purchases"),
                avg("rating").alias("avg_rating")
            ) \
            .orderBy(col("total_purchases").desc())
        
        product_stats.show()
        
        # Рекомендации: топ продуктов по рейтингу
        print("\n=== Top Recommended Products ===")
        top_products = df.filter(col("rating") >= 4.0) \
            .groupBy("product_id") \
            .agg(
                count("*").alias("high_rating_count"),
                avg("rating").alias("avg_high_rating")
            ) \
            .orderBy(col("avg_high_rating").desc(), col("high_rating_count").desc()) \
            .limit(5)
        
        top_products.show()
        
        # Сохранение результатов в Redis-совместимый формат
        print("\n=== Saving Recommendations ===")
        recommendations = top_products.collect()
        
        # Здесь можно добавить логику сохранения в Redis
        # Для демонстрации просто выводим
        for row in recommendations:
            print(f"Product {row['product_id']}: {row['avg_high_rating']:.2f} avg rating")
        
        # Метрики выполнения
        print("\n=== Job Metrics ===")
        print(f"Total records processed: {df.count()}")
        print(f"Number of users: {df.select('user_id').distinct().count()}")
        print(f"Number of products: {df.select('product_id').distinct().count()}")
        
        # Проверка соединения с Kafka
        print("\n=== Testing Kafka Connectivity ===")
        try:
            # Простая проверка через socket
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('kafka-1', 9092))
            if result == 0:
                print("✓ Kafka broker 1 is reachable")
            else:
                print("✗ Cannot reach Kafka broker 1")
            sock.close()
        except Exception as e:
            print(f"Kafka connectivity test failed: {e}")
        
    except Exception as e:
        print(f"\n!!! Error during job execution: {e}")
        raise
    finally:
        # Всегда останавливаем Spark сессию
        print(f"\n=== Stopping Spark Session at {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        spark.stop()
        print("Spark session stopped successfully")

if __name__ == "__main__":
    main()