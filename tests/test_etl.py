#!/usr/bin/env python3
import subprocess
import sys

def test_spark_connection():
    """Тест проверяет, что Spark Master доступен."""
    try:
        # Пробуем получить статус мастера через curl
        result = subprocess.run(
            ["curl", "-s", "http://spark-master:8080"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "Spark Master" in result.stdout:
            print("✅ Spark Master UI доступен.")
            return True
        else:
            print("⚠️  Spark Master не вернул ожидаемую страницу.")
            return False
    except Exception as e:
        print(f"❌ Не удалось подключиться к Spark Master: {e}")
        return False

if __name__ == "__main__":
    if test_spark_connection():
        sys.exit(0)  # Успех
    else:
        sys.exit(1)  # Провал
