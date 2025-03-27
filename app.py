import pymysql
import pandas as pd
import folium
from sklearn.cluster import KMeans

# Connect to MySQL Database
db = pymysql.connect(
    host="localhost",
    user="root",
    password="sakthi0012B@",  # Change to your MySQL password
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

# Apply K-Means Clustering
optimal_clusters = 3  # Change based on the Elbow method
kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
df['cluster'] = kmeans.fit_predict(df[['latitude', 'longitude']])

# Create Map
map_center = [df['latitude'].mean(), df['longitude'].mean()]
crime_map = folium.Map(location=map_center, zoom_start=12)

# Define Cluster Colors
colors = ['red', 'blue', 'green', 'purple', 'orange']

# Add Crime Points to Map
for _, row in df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Cluster: {int(row['cluster'])}",  # Ensure integer value
        icon=folium.Icon(color=colors[int(row['cluster'])])  # FIX applied here
    ).add_to(crime_map)

# Save Map
crime_map.save("crime_hotspots.html")
print("Crime hotspot map updated! Open 'crime_hotspots.html' in your browser.")
