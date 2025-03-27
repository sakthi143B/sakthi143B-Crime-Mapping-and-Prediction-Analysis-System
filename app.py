import datetime
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector  
import folium
app = Flask(__name__)
app.secret_key = "your_secret_key"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="sakthi0012B@",
    database="crime_mapping"
)
cursor = db.cursor()

# Login Route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Credentials. Try Again."
    
    return render_template("login.html")

# Dashboard (Crime Map)
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    # Fetch unique crime types for filter dropdown
    cursor.execute("SELECT DISTINCT crime_type FROM crime_reports")
    crime_types = [row[0] for row in cursor.fetchall()]

    # Fetch all crime data
    cursor.execute("SELECT crime_type, location, latitude, longitude FROM crime_reports")
    crimes = cursor.fetchall()

    # Initialize Folium Map
    crime_map = folium.Map(location=[10.0, 78.0], zoom_start=6)

    # Marker Mapping: Assign crime type to CSS class
    marker_html = ""  
    for crime in crimes:
        crime_type, location, lat, lon = crime
        icon_color = "red" if crime_type == "Theft" else "blue"

        # Folium Marker with Custom ID
        marker = folium.Marker(
            location=[lat, lon],
            popup=f"{crime_type} at {location}",
            icon=folium.Icon(color=icon_color, icon="info-sign"),
        )

        # Add Custom ID to the Marker
        marker.add_to(crime_map)
        marker_html += f'var marker_{lat}_{lon} = L.marker([{lat}, {lon}]).bindPopup("{crime_type} at {location}").addTo(map); marker_{lat}_{lon}.crimeType = "{crime_type}";\n'

    # 🌟 Custom HTML Template with JavaScript Filter Logic
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crime Hotspot Map</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            body {{ background-color: #eef1f5; }}
            .nav-bar {{
                background-color: #343a40;
                color: white;
                padding: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .map-container {{ width: 100%; height: 600px; margin-top: 20px; }}
        </style>
    </head>
    <body>

    <div class="nav-bar">
        <h3>Crime Mapping Dashboard</h3>
        <a href="/logout" class="btn btn-danger">Logout</a>
    </div>

    <div class="container">
        <h4 class="mt-3">Crime Hotspots Map</h4>

        <!-- Filter Dropdown -->
        <div class="mb-3">
            <label for="crimeFilter" class="form-label">Filter by Crime Type:</label>
            <select id="crimeFilter" class="form-select">
                <option value="all">All</option>
                {"".join(f'<option value="{crime}">{crime}</option>' for crime in crime_types)}
            </select>
        </div>

        <div class="map-container">
            {crime_map._repr_html_()}  <!-- Embed Folium Map -->
        </div>
    </div>

    <script>
        var map = L.map(document.getElementsByClassName('map-container')[0].getElementsByTagName('div')[0]);
        
        // JavaScript to Store Crime Markers
        {marker_html}

        // Filter Function
        document.getElementById("crimeFilter").addEventListener("change", function() {{
            var selectedCrime = this.value;

            // Show/Hide Markers Based on Selected Crime
            for (var key in map._layers) {{
                if (map._layers[key].crimeType !== undefined) {{
                    if (selectedCrime === "all" || map._layers[key].crimeType === selectedCrime) {{
                        map._layers[key].addTo(map);
                    }} else {{
                        map.removeLayer(map._layers[key]);
                    }}
                }}
            }}
        }});
    </script>

    </body>
    </html>
    """

    # Save HTML
    with open("templates/map.html", "w", encoding="utf-8") as file:
        file.write(html_template)

    return render_template("map.html")
#crime data page 
@app.route("/crime-data-page")
def crime_data_page():
    cursor.execute("SELECT id, crime_type, location, latitude, longitude, report_time FROM crime_reports")
    crimes = cursor.fetchall()
    return render_template("crime_data.html", crimes=crimes)
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sakthi0012B@",  # Your MySQL password
        database="crime_mapping"
    )

# Add New Crime Data
@app.route('/crime-data', methods=['GET', 'POST'])
def crime_data():
    if request.method == 'POST':
        location = request.form['location']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        crime_type = request.form['crime_type']
        description = request.form['description']
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """INSERT INTO crime_reports (location, latitude, longitude, crime_type, description, report_time)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            values = (location, latitude, longitude, crime_type, description, report_time)
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/crime-data')
        except mysql.connector.Error as e:
            return f"Error: {e}"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM crime_reports")
    crimes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('crime_data.html', crimes=crimes)

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))   

if __name__ == "__main__":
    app.run(debug=True)
