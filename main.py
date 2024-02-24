import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import date, timedelta
import matplotlib.dates as mdates



# Fetch historical data for VAS
vas_data = yf.download(
    'VAS.AX', start='2003-01-01')  # Assuming VAS has data for 20 years
vas_data['Date'] = vas_data.index

print(vas_data.head())  # To verify the data

vas_data['DateNumeric'] = vas_data['Date'].apply(lambda date: date.toordinal())

# Function to prepare data and fit model
def fit_model(data, start_date):
    filtered_data = data[data['Date'] >= pd.to_datetime(start_date)]
    X = filtered_data[['DateNumeric']]
    y = filtered_data['Close']

    model = LinearRegression()
    model.fit(X, y)
    return model, filtered_data

# Get today's date
today = date.today()

def get_past_date(days_ago):
    return (today - timedelta(days=days_ago)).isoformat()

models = {
    '20Y': fit_model(vas_data, get_past_date(20 * 365)),
    '3Y': fit_model(vas_data, get_past_date(3 * 365)),
    '1Y': fit_model(vas_data, get_past_date(365)),
    '1M': fit_model(vas_data, get_past_date(30)),
}

latest_date = vas_data['DateNumeric'].iloc[-1]
latest_price = vas_data['Close'].iloc[-1]

for timespan, (model, data) in models.items():
    predicted_price = model.predict([[latest_date]])[0]
    print(
        f"{timespan} Model: Predicted Price = {predicted_price:.2f}, Actual Price = {latest_price:.2f}"
    )

plt.figure(figsize=(20, 10))  # Increase the size of the figure
fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # Create 4 subplots

fig.suptitle('VAS Price History with Linear Prediction', fontsize=20)


# Flatten the axs array
axs = axs.ravel()

# Plot each model's prediction
colors = ['red', 'blue', 'green',
          'purple']  # Define a list of colors for the lines
for i, (timespan, (model, data)) in enumerate(models.items()):
    # Predict prices across the dataset's date range for the graph
    predicted_prices = model.predict(data[['DateNumeric']])
    axs[i].plot(data['Date'],
                predicted_prices,
                label=f'{timespan} Prediction',
                color=colors[i],
                linewidth=2)
    axs[i].plot(vas_data['Date'],
                vas_data['Close'],
                label='Actual Price',
                color='black',
                linewidth=2)  # Plot actual data
    axs[i].axhline(y=latest_price, color='gray',
                   linestyle='--')  # Add horizontal line for latest price
    axs[i].set_title(timespan, fontsize=15)  # Set title to just the timespan
    axs[i].set_xlabel('Date', fontsize=8)  # Reduce font size
    axs[i].set_ylabel('Price (AUD)', fontsize=10)  # Reduce font size
    axs[i].legend(fontsize=8)  # Reduce font size
    axs[i].set_xlim([data['Date'].min(), data['Date'].max()])  # Set x-axis limits to the relevant data

    # Format x-axis
    axs[i].xaxis.set_major_locator(mdates.AutoDateLocator())
    axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d'))
    plt.setp(axs[i].xaxis.get_majorticklabels(), rotation=45)

    # Limit y-axis
    axs[i].set_ylim([data['Close'].min() * 0.9, data['Close'].max() * 1.1])

    # Determine whether to buy or sell and calculate delta
    if predicted_prices[-1] > latest_price:
        buy_sell_text = 'Buy'
        color = 'green'
    else:
        buy_sell_text = 'Sell'
        color = 'red'

    delta = predicted_prices[-1] - latest_price

    # Buy/Sell annotation
    buy_sell_annotation = axs[i].text(
        0.05,  # Adjust these values to move the text
        0.15,
        f'{buy_sell_text}',
        transform=axs[i].transAxes,
        fontsize=12,  # Increase font size
        color=color,
        verticalalignment='center',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'))

    # Delta annotation
    delta_annotation = axs[i].text(
        0.05,  # Adjust these values to move the text
        0.10,  # Adjust this value to move the text
        f'Delta: ${delta:.2f}',
        transform=axs[i].transAxes,
        fontsize=10,
        color='black',
        verticalalignment='center',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'))

plt.tight_layout()  # Adjust layout for better spacing
plt.show()
