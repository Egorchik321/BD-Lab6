#!/usr/bin/env python3
"""
Эмулятор KEDA для autoscaling на основе метрик
"""

import time
import json
import subprocess
import requests
from datetime import datetime

class KEDAEmulator:
    def __init__(self):
        self.metrics = {
            'kafka_lag': 0,
            'cpu_usage': 0,
            'memory_usage': 0,
            'active_apps': 0
        }
        
        # Конфигурация триггеров
        self.triggers = {
            'kafka': {
                'enabled': True,
                'lag_threshold': 1000,
                'activation_threshold': 100,
                'bootstrap_servers': 'kafka-1:9092',
                'consumer_group': 'spark-group',
                'topic': 'transactions'
            },
            'cpu': {
                'enabled': True,
                'threshold': 70,  # %
                'scale_up_margin': 20,
                'scale_down_margin': 30
            },
            'schedule': {
                'enabled': True,
                'peak_hours': ['09:00-18:00'],
                'min_workers_peak': 3,
                'min_workers_off_peak': 1
            }
        }
        
        self.current_workers = 2
        self.max_workers = 8
        self.min_workers = 1
        
    def get_kafka_lag(self):
        """Получение Kafka lag"""
        try:
            cmd = [
                'docker', 'exec', 'lab-6-test-kafka-1-1',
                'kafka-consumer-groups',
                '--bootstrap-server', 'localhost:9092',
                '--group', self.triggers['kafka']['consumer_group'],
                '--describe'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Парсинг вывода для получения lag
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        lag = int(parts[6])
                        return lag
        except Exception as e:
            print(f"Error getting Kafka lag: {e}")
        
        return 0
    
    def get_spark_metrics(self):
        """Получение метрик Spark"""
        try:
            # Получение CPU и памяти из Docker stats
            cmd = ['docker', 'stats', '--no-stream', '--format', '{{.CPUPerc}}\t{{.MemUsage}}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'lab-6-test-spark' in line:
                        cpu, mem = line.split('\t')
                        cpu_pct = float(cpu.replace('%', ''))
                        mem_usage = mem.split('/')[0].strip()
                        return cpu_pct, mem_usage
        except Exception as e:
            print(f"Error getting Spark metrics: {e}")
        
        return 0, '0B'
    
    def scale_workers(self, desired_count):
        """Масштабирование количества workers"""
        if desired_count < self.min_workers:
            desired_count = self.min_workers
        if desired_count > self.max_workers:
            desired_count = self.max_workers
            
        if desired_count != self.current_workers:
            print(f"Scaling from {self.current_workers} to {desired_count} workers")
            
            try:
                # Используем docker-compose для масштабирования
                cmd = [
                    'docker-compose', '-f', 'docker-compose.full.yml',
                    'up', '-d', '--scale', f'spark-worker={desired_count}'
                ]
                subprocess.run(cmd, check=True)
                self.current_workers = desired_count
                print(f"Successfully scaled to {desired_count} workers")
            except Exception as e:
                print(f"Error scaling workers: {e}")
    
    def evaluate_triggers(self):
        """Оценка всех триггеров для autoscaling"""
        print(f"\n=== Autoscaling Evaluation at {datetime.now().strftime('%H:%M:%S')} ===")
        
        # 1. Kafka trigger
        if self.triggers['kafka']['enabled']:
            lag = self.get_kafka_lag()
            self.metrics['kafka_lag'] = lag
            print(f"Kafka Lag: {lag}")
            
            if lag > self.triggers['kafka']['lag_threshold']:
                print(f" High Kafka lag ({lag} > {self.triggers['kafka']['lag_threshold']})")
                # Увеличиваем на 1 worker за каждые 1000 сообщений lag
                additional_workers = min(lag // 1000, 3)
                desired = min(self.current_workers + additional_workers, self.max_workers)
                self.scale_workers(desired)
                return
        
        # 2. CPU trigger
        if self.triggers['cpu']['enabled']:
            cpu_usage, mem_usage = self.get_spark_metrics()
            self.metrics['cpu_usage'] = cpu_usage
            self.metrics['memory_usage'] = mem_usage
            print(f"CPU Usage: {cpu_usage}%")
            
            if cpu_usage > self.triggers['cpu']['threshold']:
                scale_up_by = int((cpu_usage - self.triggers['cpu']['threshold']) / 
                                 self.triggers['cpu']['scale_up_margin']) + 1
                desired = min(self.current_workers + scale_up_by, self.max_workers)
                print(f" High CPU usage, scaling up to {desired} workers")
                self.scale_workers(desired)
            elif cpu_usage < (self.triggers['cpu']['threshold'] - self.triggers['cpu']['scale_down_margin']):
                if self.current_workers > self.min_workers:
                    print(f" Low CPU usage, scaling down to {self.current_workers - 1} workers")
                    self.scale_workers(self.current_workers - 1)
        
        # 3. Schedule trigger
        if self.triggers['schedule']['enabled']:
            current_hour = datetime.now().hour
            is_peak = 9 <= current_hour < 18  # 9:00-18:00
            
            if is_peak and self.current_workers < self.triggers['schedule']['min_workers_peak']:
                print(f"Peak hours, scaling to {self.triggers['schedule']['min_workers_peak']} workers")
                self.scale_workers(self.triggers['schedule']['min_workers_peak'])
            elif not is_peak and self.current_workers > self.triggers['schedule']['min_workers_off_peak']:
                print(f" Off-peak hours, scaling to {self.triggers['schedule']['min_workers_off_peak']} workers")
                self.scale_workers(self.triggers['schedule']['min_workers_off_peak'])
    
    def run(self):
        """Основной цикл работы эмулятора"""
        print("Starting KEDA Emulator for Spark Autoscaling")
        print(f"Configuration: Min={self.min_workers}, Max={self.max_workers}")
        print("=" * 50)
        
        try:
            while True:
                self.evaluate_triggers()
                time.sleep(30)  # Проверка каждые 30 секунд
        except KeyboardInterrupt:
            print("\nKEDA Emulator stopped")

if __name__ == "__main__":
    emulator = KEDAEmulator()
    emulator.run()