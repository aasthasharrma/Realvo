import requests
import re
import csv

ticker = 'SPG'
url = f'https://www.macrotrends.net/assets/php/market_cap.php?t={ticker}'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
}

data = requests.get(url, headers=headers).text

match = re.search(r"var chartData = (\[.*?\]);", data)

if match:
    chart_data_str = match.group(1)
    chart_data = eval(chart_data_str)
    csv_file = f"{ticker}_market_cap.csv"
    csv_columns = chart_data[0].keys()

    try:
        with open(csv_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in chart_data:
                writer.writerow(data)
        print(f"Data successfully written to {csv_file}")
    except IOError:
        print("I/O error")
else:
    print("Chart data not found.")