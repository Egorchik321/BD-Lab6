import os
import json
from datetime import datetime, timedelta
import shutil

class StorageTiering:
    def __init__(self):
        self.tiers = {
            'hot': {'path': 'data/hot/', 'max_age_days': 7, 'cost_factor': 1.0},
            'warm': {'path': 'data/warm/', 'max_age_days': 30, 'cost_factor': 0.5},
            'cold': {'path': 'data/cold/', 'max_age_days': 365, 'cost_factor': 0.2}
        }
        
    def calculate_savings(self, original_cost=1000):
        total_size = 0
        tiered_cost = 0
        
        for tier_name, tier_info in self.tiers.items():
            tier_path = tier_info['path']
            if os.path.exists(tier_path):
                tier_size = sum(os.path.getsize(f) for f in os.listdir(tier_path) 
                              if os.path.isfile(os.path.join(tier_path, f)))
                total_size += tier_size
                tiered_cost += tier_size * tier_info['cost_factor']
        
        if total_size == 0:
            return 0
        
        avg_cost_per_gb = original_cost / (total_size / (1024**3))
        savings = original_cost - tiered_cost
        savings_percent = (savings / original_cost) * 100
        
        return savings_percent
    
    def apply_tiering(self, data_path='data/raw/'):
        for file in os.listdir(data_path):
            file_path = os.path.join(data_path, file)
            if os.path.isfile(file_path):
                file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_age.days <= 7:
                    dest = self.tiers['hot']['path']
                elif file_age.days <= 30:
                    dest = self.tiers['warm']['path']
                else:
                    dest = self.tiers['cold']['path']
                
                os.makedirs(dest, exist_ok=True)
                shutil.move(file_path, os.path.join(dest, file))
                print(f"Moved {file} to {dest} ({file_age.days} days old)")
        
        savings = self.calculate_savings()
        print(f"Storage tiering applied. Estimated savings: {savings:.1f}%")
        
        if savings >= 50:
            print("Target achieved: 50% cost reduction on storage")
        else:
            print(f"Target not met. Current savings: {savings:.1f}%")
        
        return savings

if __name__ == "__main__":
    tiering = StorageTiering()
    savings = tiering.apply_tiering()
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'savings_percentage': savings,
        'target_achieved': savings >= 50,
        'tier_distribution': {
            'hot_files': len(os.listdir('data/hot/')) if os.path.exists('data/hot/') else 0,
            'warm_files': len(os.listdir('data/warm/')) if os.path.exists('data/warm/') else 0,
            'cold_files': len(os.listdir('data/cold/')) if os.path.exists('data/cold/') else 0
        }
    }
    
    with open('storage_tiering_report.json', 'w') as f:
        json.dump(report, f, indent=2)