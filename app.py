import pymysql
import pandas as pd
import folium
from sklearn.cluster import DBSCAN
import numpy as np

# Connect to MySQL Database
db = pymysql.connect(
    host="localhost",
    user="root",
    password="sakthi0012B@",  # Update with your MySQL password
    database="crime_mapping"
)
cursor = db.cursor()

# Fetch Crime Data
cursor.execute("SELECT latitude, longitude FROM crime_reports")
data = cursor.fetchall()
db.close()

# Convert to DataFrame
df = pd.DataFrame(data, columns=['latitude', 'longitude'])

# Check if data exists
if df.empty:
    print("No crime data found! Check your database.")
    exit()

# Ensure data is numeric
df = df.apply(pd.to_numeric, errors='coerce')

# Apply DBSCAN Clustering
epsilon = 0.01  # Defines neighborhood size (adjust based on data)
min_samples = 3  # Minimum points needed to form a cluster
dbscan = DBSCAN(eps=epsilon, min_samples=min_samples)
df['cluster'] = dbscan.fit_predict(df[['latitude', 'longitude']])

# Create Map
map_center = [df['latitude'].mean(), df['longitude'].mean()]
crime_map = folium.Map(location=map_center, zoom_start=12)

# Define Cluster Colors
colors = ['red', 'blue', 'green', 'purple', 'orange', 'black', 'pink']

# Convert cluster_id to an integer before using it as an index
df['cluster'] = df['cluster'].astype(int)  

# Add Crime Points to Map
for _, row in df.iterrows():
    cluster_id = int(row['cluster'])  # Ensure integer type
    color = colors[cluster_id % len(colors)] if cluster_id != -1 else "gray"  # Gray for noise
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Cluster: {cluster_id}",
        icon=folium.Icon(color=color)
    ).add_to(crime_map)

# Save Map
crime_map.save("crime_dbscan.html")
print("DBSCAN Crime Map Generated! Open 'crime_dbscan.html' in your browser.")
