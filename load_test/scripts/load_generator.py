#!/usr/bin/env python3
"""
Генератор нагрузки для рекомендательной системы e-commerce
Генерирует реалистичные события пользователей: просмотры, добавления в корзину, покупки
"""
import json
import random
import time
import sys
from datetime import datetime
from kafka import KafkaProducer
import logging

class EcommerceLoadGenerator:
    def __init__(self, bootstrap_servers='localhost:9092', topic='ecommerce_events'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
        self.topic = topic
        self.event_types = ['view', 'add_to_cart', 'purchase']
        self.products = [f'product_{i:04d}' for i in range(1, 501)]  # 500 продуктов
        self.categories = ['electronics', 'clothing', 'books', 'home', 'sports']
        
        # Паттерны пользователей: 80% обычных, 15% активных, 5% новых
        self.user_profiles = {
            'regular': {'min_sessions': 3, 'max_sessions': 10, 'purchase_prob': 0.3},
            'active': {'min_sessions': 10, 'max_sessions': 30, 'purchase_prob': 0.6},
            'new': {'min_sessions': 1, 'max_sessions': 3, 'purchase_prob': 0.1}
        }
    
    def generate_user_session(self, user_id, profile='regular'):
        """Генерация сессии пользователя"""
        profile_config = self.user_profiles[profile]
        num_events = random.randint(
            profile_config['min_sessions'], 
            profile_config['max_sessions']
        )
        
        session_events = []
        session_start = datetime.now()
        
        for i in range(num_events):
            # Определяем тип события
            if i == num_events - 1 and random.random() < profile_config['purchase_prob']:
                event_type = 'purchase'
            elif i > 0 and random.random() < 0.3:
                event_type = 'add_to_cart'
            else:
                event_type = 'view'
            
            # Генерируем событие
            event = {
                'event_id': f'evt_{int(time.time()*1000)}_{user_id}_{i}',
                'user_id': f'user_{user_id:06d}',
                'session_id': f'sess_{int(session_start.timestamp())}_{user_id}',
                'event_type': event_type,
                'product_id': random.choice(self.products),
                'category': random.choice(self.categories),
                'price': round(random.uniform(10, 1000), 2) if event_type == 'purchase' else None,
                'timestamp': datetime.now().isoformat(),
                'user_profile': profile,
                'page_load_time': random.uniform(0.5, 2.5),
                'geo_location': random.choice(['US', 'EU', 'ASIA', 'RU']),
                'device': random.choice(['mobile', 'desktop', 'tablet'])
            }
            
            session_events.append(event)
            time.sleep(random.uniform(0.1, 0.5))  # Реалистичные паузы между действиями
        
        return session_events
    
    def generate_load(self, target_rps=100, duration_seconds=60):
        """Генерация нагрузки с заданным RPS"""
        print(f" Запуск генератора нагрузки: {target_rps} RPS, {duration_seconds} сек")
        print(f"Топик Kafka: {self.topic}")
        print("=" * 50)
        
        start_time = time.time()
        total_events = 0
        user_counter = 1
        
        try:
            while time.time() - start_time < duration_seconds:
                batch_start = time.time()
                batch_events = 0
                
                # Определяем профиль пользователя
                rand = random.random()
                if rand < 0.8:
                    profile = 'regular'
                elif rand < 0.95:
                    profile = 'active'
                else:
                    profile = 'new'
                
                # Генерируем сессию
                session = self.generate_user_session(user_counter, profile)
                
                # Отправляем события в Kafka
                for event in session:
                    self.producer.send(self.topic, event)
                    batch_events += 1
                    total_events += 1
                
                user_counter += 1
                
                # Контроль скорости
                batch_time = time.time() - batch_start
                expected_time = batch_events / target_rps
                
                if batch_time < expected_time:
                    time.sleep(expected_time - batch_time)
                
                # Промежуточная статистика
                if total_events % 100 == 0:
                    elapsed = time.time() - start_time
                    current_rps = total_events / elapsed if elapsed > 0 else 0
                    print(f"📊 Событий: {total_events}, Текущий RPS: {current_rps:.1f}, Пользователей: {user_counter}")
            
            # Финальная статистика
            elapsed = time.time() - start_time
            actual_rps = total_events / elapsed
            
            print("\n" + "=" * 50)
            print("Генерация нагрузки завершена")
            print(f" Итоговая статистика:")
            print(f"   Всего событий: {total_events}")
            print(f"   Всего пользователей: {user_counter}")
            print(f"   Целевой RPS: {target_rps}")
            print(f"   Фактический RPS: {actual_rps:.1f}")
            print(f"   Общее время: {elapsed:.1f} сек")
            print(f"   Топик Kafka: {self.topic}")
            
            return {
                'total_events': total_events,
                'total_users': user_counter,
                'target_rps': target_rps,
                'actual_rps': actual_rps,
                'duration': elapsed
            }
            
        except Exception as e:
            print(f"Ошибка при генерации нагрузки: {e}")
            raise
        finally:
            self.producer.flush()
            self.producer.close()

def main():
    """Основная функция с аргументами командной строки"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Генератор нагрузки для e-commerce')
    parser.add_argument('--rps', type=int, default=100, help='Целевой RPS (событий в секунду)')
    parser.add_argument('--duration', type=int, default=60, help='Длительность теста в секундах')
    parser.add_argument('--topic', type=str, default='ecommerce_events', help='Топик Kafka')
    parser.add_argument('--bootstrap', type=str, default='localhost:9092', help='Bootstrap servers Kafka')
    
    args = parser.parse_args()
    
    # Создаем генератор
    generator = EcommerceLoadGenerator(
        bootstrap_servers=args.bootstrap,
        topic=args.topic
    )
    
    # Запускаем генерацию
    results = generator.generate_load(
        target_rps=args.rps,
        duration_seconds=args.duration
    )
    
    # Сохраняем результаты
    import json
    with open('load_test/results/generation_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Отчет сохранен в load_test/results/generation_report.json")

if __name__ == "__main__":
    main()