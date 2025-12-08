from datetime import datetime

class ReportGenerator:

    def generate_report(self, stats: dict):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        report = f"""
Energy Consumption Report – {ts}
------------------------------------
Mean consumption: {stats['mean']:.2f} kWh
Max consumption : {stats['max']:.2f} kWh
Min consumption : {stats['min']:.2f} kWh
Std deviation   : {stats['std_dev']:.2f} kWh
"""
        return report
