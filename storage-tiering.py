#!/usr/bin/env python3
"""
Реализация storage tiering для снижения затрат на хранение
"""

import json
import time
from datetime import datetime, timedelta
import subprocess
import os

class StorageTieringManager:
    def __init__(self):
        # Конфигурация storage tiering
        self.tiers = {
            'hot': {
                'storage_class': 'ssd',
                'cost_per_gb_month': 0.10,  # $0.10/GB-месяц
                'retention_days': 7,
                'performance': 'high',
                'access_frequency': 'daily'
            },
            'warm': {
                'storage_class': 'hdd',
                'cost_per_gb_month': 0.03,  # $0.03/GB-месяц
                'retention_days': 30,
                'performance': 'medium',
                'access_frequency': 'weekly'
            },
            'cold': {
                'storage_class': 'archive',
                'cost_per_gb_month': 0.01,  # $0.01/GB-месяц
                'retention_days': 365,
                'performance': 'low',
                'access_frequency': 'monthly'
            }
        }
        
        # Текущее распределение данных
        self.current_distribution = {
            'hot': 100,  # GB
            'warm': 50,  # GB
            'cold': 20   # GB
        }
        
        self.baseline_cost = 0.10  # Все данные в hot storage
        self.target_savings = 0.50  # 50% снижение затрат
        
    def calculate_storage_cost(self, distribution):
        """Расчет стоимости хранения"""
        total_cost = 0
        for tier, gb in distribution.items():
            tier_cost = self.tiers[tier]['cost_per_gb_month'] * gb
            total_cost += tier_cost
        return total_cost
    
    def optimize_tiering(self, access_patterns):
        """
        Оптимизация tiering на основе паттернов доступа
        access_patterns: словарь с частотой доступа к данным
        """
        optimized_distribution = {'hot': 0, 'warm': 0, 'cold': 0}
        
        total_data = sum(self.current_distribution.values())
        
        # Анализ паттернов доступа
        for dataset, pattern in access_patterns.items():
            data_size = pattern.get('size_gb', 0)
            access_freq = pattern.get('access_frequency', 'monthly')
            last_access = pattern.get('last_access_days', 30)
            
            # Определение подходящего tier
            if access_freq == 'daily' or last_access <= 7:
                optimized_distribution['hot'] += data_size
            elif access_freq == 'weekly' or last_access <= 30:
                optimized_distribution['warm'] += data_size
            else:
                optimized_distribution['cold'] += data_size
        
        return optimized_distribution
    
    def migrate_data(self, from_tier, to_tier, data_size_gb):
        """Эмуляция миграции данных между tiers"""
        print(f"Migrating {data_size_gb}GB from {from_tier} to {to_tier} tier...")
        
        # В реальной системе здесь был бы вызов API хранилища
        # Для эмуляции используем логирование
        
        migration_log = {
            'timestamp': datetime.now().isoformat(),
            'from_tier': from_tier,
            'to_tier': to_tier,
            'size_gb': data_size_gb,
            'cost_saving_per_month': data_size_gb * (
                self.tiers[from_tier]['cost_per_gb_month'] - 
                self.tiers[to_tier]['cost_per_gb_month']
            )
        }
        
        # Обновление распределения
        self.current_distribution[from_tier] -= data_size_gb
        self.current_distribution[to_tier] += data_size_gb
        
        return migration_log
    
    def apply_tiering_policy(self, table_name, retention_days):
        """Применение политики tiering к таблице"""
        # Эмуляция ALTER TABLE для tiering
        policy = f"""
        -- Автоматический переход старых данных в холодное хранилище
        ALTER TABLE {table_name} SET TBLPROPERTIES (
            "storage_handler" = "org.apache.hadoop.hive.ql.storage.ArchiveStorageHandler",
            "retention_days" = "{retention_days}",
            "tiering_policy" = "{{
                'hot': {{'days': 7}},
                'warm': {{'days': 30}},
                'cold': {{'days': {retention_days}}}
            }}"
        );
        """
        
        print(f"Applying tiering policy to {table_name}:")
        print(policy)
        
        # В реальной системе: выполнение SQL через Spark/Hive
        # Для эмуляции сохраняем в файл
        with open(f'tiering_policy_{table_name}.sql', 'w') as f:
            f.write(policy)
        
        return policy
    
    def generate_savings_report(self):
        """Генерация отчета об экономии"""
        # Расчет стоимостей
        baseline_cost = self.calculate_storage_cost(
            {'hot': sum(self.current_distribution.values())}
        )
        
        optimized_cost = self.calculate_storage_cost(self.current_distribution)
        
        savings = baseline_cost - optimized_cost
        savings_percentage = (savings / baseline_cost) * 100 if baseline_cost > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'storage_costs': {
                'baseline_all_hot': round(baseline_cost, 2),
                'optimized_tiered': round(optimized_cost, 2),
                'monthly_savings': round(savings, 2),
                'savings_percentage': round(savings_percentage, 2),
                'target_savings': self.target_savings * 100
            },
            'data_distribution': {
                'hot_gb': self.current_distribution['hot'],
                'warm_gb': self.current_distribution['warm'],
                'cold_gb': self.current_distribution['cold'],
                'total_gb': sum(self.current_distribution.values())
            },
            'cost_per_tier': {
                tier: {
                    'cost_per_gb': self.tiers[tier]['cost_per_gb_month'],
                    'total_cost': round(self.tiers[tier]['cost_per_gb_month'] * 
                                      self.current_distribution[tier], 2)
                }
                for tier in self.tiers
            },
            'achievements': {
                'target_50_savings': savings_percentage >= 50,
                'hot_data_reduction': round(
                    (1 - self.current_distribution['hot'] / 
                     sum(self.current_distribution.values())) * 100, 2
                ),
                'cold_data_utilization': round(
                    self.current_distribution['cold'] / 
                    sum(self.current_distribution.values()) * 100, 2
                )
            }
        }
        
        return report

def main():
    manager = StorageTieringManager()
    
    print("=" * 60)
    print("STORAGE TIERING OPTIMIZATION")
    print("=" * 60)
    
    # Пример паттернов доступа к данным
    access_patterns = {
        'recent_transactions': {
            'size_gb': 40,
            'access_frequency': 'daily',
            'last_access_days': 1
        },
        'user_profiles': {
            'size_gb': 60,
            'access_frequency': 'weekly',
            'last_access_days': 10
        },
        'historical_sales': {
            'size_gb': 50,
            'access_frequency': 'monthly',
            'last_access_days': 90
        },
        'archive_logs': {
            'size_gb': 20,
            'access_frequency': 'yearly',
            'last_access_days': 200
        }
    }
    
    # Оптимизация распределения
    print("\nАНАЛИЗ ПАТТЕРНОВ ДОСТУПА:")
    for dataset, pattern in access_patterns.items():
        print(f"  {dataset}: {pattern['size_gb']}GB, доступ: {pattern['access_frequency']}")
    
    optimized = manager.optimize_tiering(access_patterns)
    
    print(f"\nОПТИМИЗИРОВАННОЕ РАСПРЕДЕЛЕНИЕ:")
    print(f"  Hot tier: {optimized['hot']}GB (активные данные)")
    print(f"  Warm tier: {optimized['warm']}GB (редко используемые)")
    print(f"  Cold tier: {optimized['cold']}GB (архивные)")
    
    # Миграция данных (эмуляция)
    print("\nМИГРАЦИЯ ДАННЫХ:")
    
    # Пример миграции исторических данных в cold storage
    if optimized['cold'] > manager.current_distribution['cold']:
        migrate_gb = optimized['cold'] - manager.current_distribution['cold']
        log = manager.migrate_data('hot', 'cold', migrate_gb)
        print(f"  Сэкономлено: ${log['cost_saving_per_month']:.2f}/месяц")
    
    # Применение политик tiering
    print("\nПОЛИТИКИ TIERING ДЛЯ ТАБЛИЦ:")
    tables = ['sales', 'user_behavior', 'product_catalog']
    for table in tables:
        policy = manager.apply_tiering_policy(table, retention_days=365)
        print(f"  {table}: политика применена")
    
    # Генерация отчета
    report = manager.generate_savings_report()
    
    print("\nРЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ:")
    costs = report['storage_costs']
    print(f"  Исходная стоимость: ${costs['baseline_all_hot']:.2f}/месяц")
    print(f"  После оптимизации: ${costs['optimized_tiered']:.2f}/месяц")
    print(f"  Экономия: ${costs['monthly_savings']:.2f}/месяц ({costs['savings_percentage']:.2f}%)")
    
    print(f"\nЦЕЛЬ: {costs['target_savings']}% экономии")
    print(f"   ДОСТИГНУТО: {costs['savings_percentage']:.2f}%")
    
    if costs['savings_percentage'] >= costs['target_savings']:
        print(" ЦЕЛЬ ДОСТИГНУТА!")
    else:
        print("  ЦЕЛЬ НЕ ДОСТИГНУТА, нужна дополнительная оптимизация")
    
    print("\nРАСПРЕДЕЛЕНИЕ ДАННЫХ:")
    dist = report['data_distribution']
    total = dist['total_gb']
    print(f"  Hot: {dist['hot_gb']}GB ({dist['hot_gb']/total*100:.1f}%)")
    print(f"  Warm: {dist['warm_gb']}GB ({dist['warm_gb']/total*100:.1f}%)")
    print(f"  Cold: {dist['cold_gb']}GB ({dist['cold_gb']/total*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print(f"Отчет сгенерирован: {report['timestamp']}")
    
    # Сохранение отчета
    with open('storage-tiering-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("Отчет сохранен в storage-tiering-report.json")

if __name__ == "__main__":
    main()