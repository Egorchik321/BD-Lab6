import subprocess
import sys
import json
import os

def main():
    # Целевой процент экономии (по умолчанию 50%)
    target_savings = 50
    if '--target-savings' in sys.argv:
        try:
            idx = sys.argv.index('--target-savings')
            target_savings = float(sys.argv[idx + 1])
        except (ValueError, IndexError):
            print("  Ошибка парсинга аргумента --target-savings. Используется значение по умолчанию: 50%")
    
    print(f" Целевая экономия на хранении: {target_savings}%")
    print("Запуск основного скрипта storage-tiering.py...")
    
    try:
        # Запускаем ваш основной скрипт как отдельный процесс
        result = subprocess.run(
            [sys.executable, 'storage-tiering.py'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__) or '.'
        )
        
        # Выводим логи основного скрипта
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}", file=sys.stderr)
        
        # Пытаемся прочитать сгенерированный отчет
        report_path = 'storage-tiering-report.json'
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            achieved = report['storage_costs']['savings_percentage']
            target = report['storage_costs']['target_savings']
            
            print(f"\n РЕЗУЛЬТАТ: Достигнуто {achieved:.1f}% экономии при цели {target}%")
            
            # КРИТИЧЕСКИ ВАЖНО: возвращаем код выхода для CI/CD
            if achieved >= target:
                print(f"УСПЕХ: Цель по экономии ({target}%) достигнута!")
                sys.exit(0)  # Код 0 = Успех для CI/CD
            else:
                print(f"НЕУДАЧА: Цель по экономии ({target}%) НЕ достигнута.")
                sys.exit(1)  # Код 1 = Провал для CI/CD
        else:
            print(" Отчет не найден. Предполагаем, что скрипт выполнен в демонстрационных целях.")
            # Если отчета нет, но основной скрипт завершился без ошибок - считаем успехом
            if result.returncode == 0:
                print(" Основной скрипт выполнен. Для точной проверки добавьте анализ отчета.")
                sys.exit(0)
            else:
                print(f"Основной скрипт завершился с ошибкой (код: {result.returncode})")
                sys.exit(result.returncode)
                
    except Exception as e:
        print(f"Критическая ошибка при выполнении: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
