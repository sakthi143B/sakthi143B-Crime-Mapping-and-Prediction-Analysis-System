import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA

# MySQL Database Credentials
db_config = {
    "host": "localhost",
    "user": "root",  # Change if necessary
    "password": "sakthi0012B@",  # Ensure security in production
    "database": "crime_mapping"
}

# Connect to MySQL
conn = pymysql.connect(**db_config)

# Fetch crime trend data
query_trend = """
SELECT DATE(report_time) AS report_date, COUNT(*) AS crime_count
FROM crime_reports  -- Change to your actual table name
GROUP BY report_date
ORDER BY report_date;
"""

df_trend = pd.read_sql(query_trend, conn)

# Convert report_date to DateTime format
df_trend['report_date'] = pd.to_datetime(df_trend['report_date'])
df_trend.set_index('report_date', inplace=True)

# Train ARIMA Model (2,1,2)
model = ARIMA(df_trend, order=(2,1,2))
model_fit = model.fit()

# Forecast next 6 months
forecast_steps = 6
forecast_dates = pd.date_range(start=df_trend.index[-1], periods=forecast_steps + 1, freq='M')[1:]
forecast = model_fit.forecast(steps=forecast_steps)

# Create a DataFrame for forecasted data
forecast_df = pd.DataFrame({'Forecasted Crime Count': forecast.values}, index=forecast_dates)

# Display forecasted crime data first
print("\n🔮 **Future Crime Predictions (Next 6 Months):**")
print(forecast_df)

# Plot forecast first
plt.figure(figsize=(12, 6))
plt.plot(forecast_df, label='Forecasted Crime Data', linestyle='dashed', marker='x', color='red')
plt.xlabel('Date')
plt.ylabel('Crime Count')
plt.title('Future Crime Trend Prediction')
plt.legend()
plt.grid(True)
plt.show()

# Plot historical data next
plt.figure(figsize=(12, 6))
plt.plot(df_trend, label='Actual Crime Data', marker='o')
plt.plot(forecast_df, label='Forecasted Crime Data', linestyle='dashed', marker='x', color='red')
plt.xlabel('Date')
plt.ylabel('Crime Count')
plt.title('Crime Trends (Historical + Forecast)')
plt.legend()
plt.grid(True)
plt.show()

# ------------------------- NEW ADDITION: Crime Type by Location -------------------------

# Fetch crime type data grouped by location
query_crime_type = """
SELECT location, crime_type, COUNT(*) AS crime_count
FROM crime_reports  -- Change to your actual table name
GROUP BY location, crime_type
ORDER BY location, crime_type;
"""

df_crime_type = pd.read_sql(query_crime_type, conn)
conn.close()

# Pivot for better visualization
crime_pivot = df_crime_type.pivot(index="location", columns="crime_type", values="crime_count").fillna(0)

# Plot crime distribution per location
plt.figure(figsize=(14, 7))
crime_pivot.plot(kind='bar', stacked=True, figsize=(14, 7), colormap="tab10")
plt.xlabel('Location')
plt.ylabel('Crime Count')
plt.title('Crime Distribution by Type & Location')
plt.xticks(rotation=75)
plt.legend(title="Crime Type", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(axis="y")

# Show the graph
plt.show()
