from flask import Flask, render_template, request
from datetime import datetime
from collections import defaultdict
import csv

app = Flask(__name__)

csv_file_path = "jeju_weather.csv"

def get_region_list():
    regions = set()
    with open(csv_file_path, 'r', encoding='UTF8') as file:
        reader = csv.reader(file)
        next(reader)  
        for row in reader:
            if row[0]:  
                regions.add(row[0])
    return sorted(regions)  

def calculate_monthly_avg():
    region_monthly_data = defaultdict(lambda: defaultdict(list))
    with open(csv_file_path, 'r', encoding='UTF8') as file:
        reader = csv.reader(file)
        next(reader)  
        for row in reader:
            baseDate_str = row[1]
            observatoryName = row[0]
            if row[2] != '':
                averageTemperature = float(row[2])
                baseDate = datetime.strptime(baseDate_str, "%Y%m%d")
                month_key = baseDate.strftime("%m")  
                region_monthly_data[observatoryName][month_key].append(averageTemperature)
    
    region_monthly_avg = {
        observatoryName: {
            month: sum(temps) / len(temps)
            for month, temps in months.items()
        }
        for observatoryName, months in region_monthly_data.items()
    }
    return region_monthly_avg

@app.route('/', methods=['GET', 'POST'])
def index():
    regions = get_region_list()  
    region_monthly_avg = calculate_monthly_avg()  
    matched_months = []
    selected_region = None
    target_temperature = None

    if request.method == 'POST':
        target_temperature = float(request.form['target_temperature'])
        tolerance = 2.0

        use_specific_region = request.form.get('use_specific_region')
        if use_specific_region == 'yes':
            selected_region = request.form.get('selected_region')

        if selected_region:
            for month, avg_temp in region_monthly_avg[selected_region].items():
                if abs(avg_temp - target_temperature) <= tolerance:
                    matched_months.append((month, avg_temp))
        else:
            for observatoryName, months in region_monthly_avg.items():
                for month, avg_temp in months.items():
                    if abs(avg_temp - target_temperature) <= tolerance:
                        matched_months.append((observatoryName, month, avg_temp))

    return render_template(
        'index.html',
        regions=regions,
        matched_months=matched_months,
        selected_region=selected_region,
        target_temperature=target_temperature
    )

if __name__ == '__main__':
    app.run(debug=True)
