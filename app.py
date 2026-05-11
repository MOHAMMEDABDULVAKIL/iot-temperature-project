from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

# ==============================
# DATABASE CONNECTION
# ==============================

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    print("✅ Connected to MySQL Database")

except mysql.connector.Error as err:
    print("❌ Database Connection Failed")
    print(err)


# ==============================
# HOME ROUTE
# ==============================

@app.route('/')
def home():
    return """
    <h2>🌡️ IoT Sensor Server Running</h2>
    <p>ESP + Flask + MySQL Server is active.</p>
    """


# ==============================
# RECEIVE SENSOR DATA FROM ESP
# ==============================

@app.route('/data', methods=['GET'])
def receive_data():

    temp = request.args.get('temp')
    hum = request.args.get('hum')

    print("📥 Received Data:")
    print("Temperature:", temp)
    print("Humidity:", hum)

    if temp is not None and hum is not None:

        try:
            cursor = db.cursor()

            sql = """
            INSERT INTO sensor_data (temperature, humidity)
            VALUES (%s, %s)
            """

            values = (temp, hum)

            cursor.execute(sql, values)

            db.commit()

            cursor.close()

            print("✅ Data Saved to MySQL")

            return jsonify({
                "status": "success",
                "message": "Data saved"
            }), 200

        except mysql.connector.Error as err:

            print("❌ MySQL Error:", err)

            return jsonify({
                "status": "error",
                "message": str(err)
            }), 500

    return jsonify({
        "status": "error",
        "message": "Invalid data"
    }), 400


# ==============================
# API FOR FLUTTER APP / DASHBOARD
# ==============================

@app.route('/get-data', methods=['GET'])
def get_data():

    try:

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

    except mysql.connector.Error as err:

        print("❌ Database Fetch Error:", err)

        return jsonify({
            "status": "error",
            "message": str(err)
        }), 500


# ==============================
# RUN FLASK SERVER
# ==============================

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port
    )
