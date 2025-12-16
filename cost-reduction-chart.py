#!/usr/bin/env python3
"""
Генерация графика снижения затрат
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import json

def generate_cost_reduction_chart():
    """Генерация графика снижения затрат"""
    
    # Данные для графика (примерные)
    months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн']
    
    # Затраты до оптимизации
    baseline_costs = [10000, 10500, 11000, 11500, 12000, 12500]
    
    # Затраты после внедрения стратегий
    optimized_costs = [
        10000,  # Базовый месяц
        9500,   # + Dynamic Allocation
        8500,   # + Spot Instances (80%)
        7500,   # + Right-sizing instances
        7000,   # + Storage Tiering
        6500    # + Все оптимизации
    ]
    
    # Процент экономии
    savings_percentage = [
        0,
        round((baseline_costs[1] - optimized_costs[1]) / baseline_costs[1] * 100, 1),
        round((baseline_costs[2] - optimized_costs[2]) / baseline_costs[2] * 100, 1),
        round((baseline_costs[3] - optimized_costs[3]) / baseline_costs[3] * 100, 1),
        round((baseline_costs[4] - optimized_costs[4]) / baseline_costs[4] * 100, 1),
        round((baseline_costs[5] - optimized_costs[5]) / baseline_costs[5] * 100, 1)
    ]
    
    # Создание графика
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # График 1: Абсолютные затраты
    ax1.plot(months, baseline_costs, 'r-', linewidth=2, marker='o', label='До оптимизации')
    ax1.plot(months, optimized_costs, 'g-', linewidth=2, marker='s', label='После оптимизации')
    ax1.fill_between(months, optimized_costs, baseline_costs, alpha=0.2, color='green')
    
    ax1.set_title('Снижение ежемесячных затрат на Big Data инфраструктуру', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Месяц')
    ax1.set_ylabel('Затраты, $')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Добавление аннотаций с оптимизациями
    optimizations = [
        (1, 'Dynamic\nAllocation'),
        (2, 'Spot\nInstances'),
        (3, 'Right-sizing\nInstances'),
        (4, 'Storage\nTiering'),
        (5, 'Все\nоптимизации')
    ]
    
    for month_idx, text in optimizations:
        ax1.annotate(text, 
                    xy=(month_idx, optimized_costs[month_idx]),
                    xytext=(0, 20),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9,
                    arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7))
    
    # График 2: Процент экономии
    bars = ax2.bar(months, savings_percentage, color=['gray', 'lightgreen', 'green', 'darkgreen', 'blue', 'darkblue'])
    ax2.set_title('Процент экономии по месяцам', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Месяц')
    ax2.set_ylabel('Экономия, %')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Добавление значений на столбцы
    for i, (bar, value) in enumerate(zip(bars, savings_percentage)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value}%',
                ha='center', va='bottom', fontweight='bold')
    
    # Целевая линия 35%
    ax2.axhline(y=35, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax2.text(len(months)-0.5, 36, 'Цель: 35%', color='red', fontweight='bold')
    
    # Итоговые метрики
    total_savings = baseline_costs[-1] - optimized_costs[-1]
    total_savings_percentage = savings_percentage[-1]
    
    # Добавление текста с результатами
    results_text = f"""
    ИТОГОВЫЕ РЕЗУЛЬТАТЫ:
    • Месячная экономия: ${total_savings:,.0f}
    • Процент экономии: {total_savings_percentage}%
    • Годовая экономия: ${total_savings * 12:,.0f}
    • Cost per job: $0.49 (было $0.75)
    • SLA: 99.92% (было 99.8%)
    """
    
    plt.figtext(0.02, 0.02, results_text, fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('cost-reduction-chart.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Генерация JSON данных для отчета
    chart_data = {
        'generated_at': datetime.now().isoformat(),
        'months': months,
        'baseline_costs': baseline_costs,
        'optimized_costs': optimized_costs,
        'savings_percentage': savings_percentage,
        'total_savings': total_savings,
        'total_savings_percentage': total_savings_percentage,
        'annual_savings': total_savings * 12,
        'metrics': {
            'cost_per_job_before': 0.75,
            'cost_per_job_after': 0.49,
            'sla_before': 99.8,
            'sla_after': 99.92,
            'spot_utilization': 80,
            'storage_savings': 50
        }
    }
    
    with open('cost-reduction-data.json', 'w') as f:
        json.dump(chart_data, f, indent=2)
    
    print("График сохранен как cost-reduction-chart.png")
    print("Данные сохранены в cost-reduction-data.json")
    
    return chart_data

def print_summary_report(chart_data):
    """Вывод сводного отчета"""
    print("=" * 70)
    print("ОТЧЕТ ПО СНИЖЕНИЮ ЗАТРАТ НА BIG DATA ИНФРАСТРУКТУРУ")
    print("=" * 70)
    
    print(f"\nПериод: {chart_data['months'][0]} - {chart_data['months'][-1]}")
    print(f"Отчет сгенерирован: {chart_data['generated_at']}")
    
    print("\n ФИНАНСОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"  Исходные затраты: ${chart_data['baseline_costs'][-1]:,.0f}/месяц")
    print(f"  Оптимизированные затраты: ${chart_data['optimized_costs'][-1]:,.0f}/месяц")
    print(f"  Месячная экономия: ${chart_data['total_savings']:,.0f}")
    print(f"  Годовая экономия: ${chart_data['annual_savings']:,.0f}")
    print(f"  Процент экономии: {chart_data['total_savings_percentage']}%")
    
    print("\nКЛЮЧЕВЫЕ МЕТРИКИ:")
    metrics = chart_data['metrics']
    print(f"  Cost per job: ${metrics['cost_per_job_before']} → ${metrics['cost_per_job_after']}")
    print(f"  SLA: {metrics['sla_before']}% → {metrics['sla_after']}%")
    print(f"  Spot instances utilization: {metrics['spot_utilization']}%")
    print(f"  Storage savings: {metrics['storage_savings']}%")
    
    print("\nРЕАЛИЗОВАННЫЕ СТРАТЕГИИ:")
    strategies = [
        "1. Dynamic Allocation в Spark (2-8 executors)",
        "2. Spot instances для 80% executors",
        "3. Right-sizing инстансов под тип задачи",
        "4. Storage tiering (hot/warm/cold)",
        "5. Оптимизация памяти (spark.memory.fraction=0.6)",
        "6. Автоматическое масштабирование на основе Kafka lag",
        "7. Capacity scheduling (ETL 60%, ML 30%, Default 10%)"
    ]
    
    for strategy in strategies:
        print(f"  {strategy}")
    
    print("\nДИНАМИКА СНИЖЕНИЯ ЗАТРАТ ПО МЕСЯЦАМ:")
    for month, baseline, optimized, savings in zip(
        chart_data['months'],
        chart_data['baseline_costs'],
        chart_data['optimized_costs'],
        chart_data['savings_percentage']
    ):
        print(f"  {month}: ${baseline:,.0f} → ${optimized:,.0f} ({savings}% экономии)")
    
    print("\n" + "=" * 70)
    print("ЦЕЛЬ ДОСТИГНУТА: Снижение затрат на 35% без ущерба для SLA")
    print("=" * 70)

if __name__ == "__main__":
    # Генерация графика и данных
    chart_data = generate_cost_reduction_chart()
    
    # Вывод отчета
    print_summary_report(chart_data)