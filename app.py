from flask import Flask, request, jsonify
// import mysql.connector

app = Flask(__name__)

#MySQL CONNECTION


#Insert Data From ESP
latest_data = {
    "temperature": 0,
    "humidity": 0
}

@app.route('/data', methods=['GET'])
def receive_data():

    temp = request.args.get('temp')
    hum = request.args.get('hum')

    latest_data["temperature"] = temp
    latest_data["humidity"] = hum

    print("Received:", temp, hum)

    return "Data Saved", 200

# ---------------- API FOR DASHBOARD ----------------
@app.route('/get-data', methods=['GET'])
def get_data():

    return jsonify(latest_data)

@app.route('/')
def home():

    return "IoT Flask Server Running"

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port
    )
