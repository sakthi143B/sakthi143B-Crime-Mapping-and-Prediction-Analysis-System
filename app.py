import pymysql
import pandas as pd
import folium
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# MySQL Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "sakthi0012B@",
    "database": "crime_mapping"
}

# Connect to MySQL
conn = pymysql.connect(**db_config)

# Fetch data for Apriori analysis
query = """
SELECT id, crime_type, report_time, location, latitude, longitude
FROM crime_reports
WHERE id IS NOT NULL;
"""

df = pd.read_sql(query, conn)
conn.close()

# Ensure there are offenders in the dataset
if df.empty:
    raise ValueError("❌ No data found! Please check the database.")

# ------------------- STEP 1: Identify Repeat Offenders -------------------

# Count crimes per offender
repeat_offenders = df['id'].value_counts().reset_index()
repeat_offenders.columns = ['id', 'crime_count']
repeat_offenders = repeat_offenders[repeat_offenders['crime_count'] > 1]

print("\n🔍 **Repeat Offenders:**")
print(repeat_offenders)

# ------------------- STEP 2: Apply Apriori Algorithm -------------------

# Prepare data for Apriori (list of crimes per offender)
offender_crime_data = df.groupby('id')['crime_type'].apply(list).reset_index()

# Convert into transaction format
transactions = offender_crime_data['crime_type'].tolist()

# Debug: Check if transactions exist
if not transactions:
    raise ValueError("❌ No crime transactions found for Apriori analysis.")

te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df_apriori = pd.DataFrame(te_ary, columns=te.columns_)

# Apply Apriori Algorithm (Reduced min_support)
frequent_itemsets = apriori(df_apriori, min_support=0.05, use_colnames=True)

# Debug: Check if frequent itemsets exist
if frequent_itemsets.empty:
    raise ValueError("❌ No frequent itemsets found! Try reducing min_support further.")

rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)

# Display frequent crime associations
print("\n📊 **Crime Association Rules:**")
print(rules[['antecedents', 'consequents', 'support', 'confidence']])

# ------------------- STEP 3: Plot Crime Locations on Map -------------------

map_center = [df['latitude'].mean(), df['longitude'].mean()]
crime_map = folium.Map(location=map_center, zoom_start=12)

for _, row in df.iterrows():
    # Choose icon properties based on crime type
    if row['crime_type'] == 'Theft':
        # Blue marker with a dollar sign icon
        icon = folium.Icon(color="blue", icon="glyphicon glyphicon-usd")
    elif row['crime_type'] == 'Burglary':
        # Green marker with a home icon
        icon = folium.Icon(color="green", icon="glyphicon glyphicon-home")
    elif row['crime_type'] == 'Assault':
        # Orange marker with an exclamation sign
        icon = folium.Icon(color="orange", icon="exclamation-sign")
    else:
        # Default purple marker with the info-sign icon
        icon = folium.Icon(color="purple", icon="info-sign")
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['crime_type']} at {row['location']}",
        icon=icon,
    ).add_to(crime_map)


crime_map.save("crime_map.html")
print("\n🗺️ **Crime Map saved as 'crime_map.html'** (Open in a browser)")
