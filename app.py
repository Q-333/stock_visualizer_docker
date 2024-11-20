
import csv
from flask import Flask, render_template, request
import requests
import pygal
from datetime import datetime

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

api_key = 'L3N6WZF86JZURK2W' 

# read csv file
def load_symbols():
    symbols = []
    csv_file = "stocks.csv"
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                symbol = row[0]
                company = row[1]
                sector = row[2]
                symbols.append(symbol)

    except Exception as e:
        print(f"Error reading stocks.csv: {e}")
    return symbols

# route for the stock visualizer page
@app.route('/', methods=('GET', 'POST'))
def stock_visualizer():
    #load the csv file
    symbols = load_symbols()

    if request.method == 'POST':
        symbol = request.form['symbol']
        chart_type = int(request.form['chart_type'])
        time_series = request.form['time_series']
        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
        end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d")

        # request parameters for API
        params = {
            'function': time_series,
            'symbol': symbol,
            'apikey': api_key,
            'outputsize': 'full'
        }
        url = 'https://www.alphavantage.co/query'
        response = requests.get(url, params=params)
        data = response.json()

        # call filter data function and create chart function
        filtered_data = filter_data_by_date(data, start_date, end_date)
        chart_svg = create_chart(filtered_data, chart_type, symbol)

        # Return chart
        return render_template('stock_visualizer.html', chart_svg=chart_svg, symbols=symbols)
    
    return render_template('stock_visualizer.html', chart_svg=None, symbols=symbols)

# filter data by the date
def filter_data_by_date(data, start_date, end_date):
    time_series_data = next((data[key] for key in data.keys() if 'Time Series' in key), None)
    if time_series_data is None:
        return {}

    filtered_data = {
        date_str: daily_data
        for date_str, daily_data in time_series_data.items()
        if start_date <= datetime.strptime(date_str, "%Y-%m-%d") <= end_date
    }
    return filtered_data

#render svg chart in a web usable format
def create_chart(data, chart_type, symbol):
    dates = sorted(data.keys())
    open_prices = [float(data[date]['1. open']) for date in dates]
    high_prices = [float(data[date]['2. high']) for date in dates]
    low_prices = [float(data[date]['3. low']) for date in dates]
    close_prices = [float(data[date]['4. close']) for date in dates]

    chart = pygal.Bar(title=f'{symbol} Stock Prices', x_label_rotation=20) if chart_type == 1 else pygal.Line(title=f'{symbol} Stock Prices', x_label_rotation=20)
    chart.x_labels = dates
    chart.add('Open', open_prices)
    chart.add('High', high_prices)
    chart.add('Low', low_prices)
    chart.add('Close', close_prices)
    return chart.render_data_uri()

#run app after flask run has been called
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)