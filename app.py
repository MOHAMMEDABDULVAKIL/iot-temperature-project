from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

#MySQL CONNECTION
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Abdul@2025",
    database="sensor_db"
)

print("Connected to MySQL")

#Insert Data From ESP
@app.route('/data', methods=['GET'])
def receive_data():

    temp = request.args.get('temp')
    hum = request.args.get('hum')

    print("Received:", temp, hum)

    if temp is not None and hum is not None:

        cursor = db.cursor()

        sql = """INSERT INTO sensor_data (temperature, humidity) 
        VALUES (%s, %s)"""

        cursor.execute(sql, (temp, hum))
        db.commit()

        cursor.close()

        print("Saved to MySQL")

        return "Data Saved", 200

    return "Invalid data", 400

# ---------------- API FOR DASHBOARD ----------------
@app.route('/get-data', methods=['GET'])
def get_data():

    cursor = db.cursor()

    cursor.execute("""
        SELECT temperature, humidity, timestamp
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    cursor.close()

    data = []

    for r in reversed(rows):
        data.append({
            "temperature": r[0],
            "humidity": r[1],
            "time": r[2].strftime("%H:%M:%S")
        })

    return jsonify(data)


# ---------------- DASHBOARD UI ----------------
@app.route('/')
def dashboard():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IoT Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>

    <body>
        <h2>🌡️ Live IoT Temperature & Humidity Dashboard</h2>

        <canvas id="chart" width="800" height="400"></canvas>

        <script>

            async function fetchData() {
                const response = await fetch('/get-data');
                return await response.json();
            }

            async function drawChart() {

                const data = await fetchData();

                const labels = data.map(d => d.time);
                const temp = data.map(d => d.temperature);
                const hum = data.map(d => d.humidity);

                new Chart(document.getElementById('chart'), {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Temperature (°C)',
                                data: temp,
                                borderColor: 'red',
                                fill: false
                            },
                            {
                                label: 'Humidity (%)',
                                data: hum,
                                borderColor: 'blue',
                                fill: false
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        animation: false
                    }
                });
            }

            drawChart();

        </script>
    </body>
    </html>
    """

#RUn Server
import os

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port
    )