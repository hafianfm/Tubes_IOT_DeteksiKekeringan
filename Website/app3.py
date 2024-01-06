import numpy as np
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from tensorflow import keras
import paho.mqtt.client as mqtt
from collections import Counter
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Load the trained model
loaded_model = keras.models.load_model("lstm_model.h5")
rounded_value_to_label = {0.0: "Kering", 1.0: "Normal", 2.0: "Basah"}

# Global variable to store predictions
predictions = []

def classify(humidity):
    prediction = loaded_model.predict(np.array([[humidity]]))
    rounded_value = round(prediction[0][0])
    if rounded_value < 0.0 :
        rounded_value = 0.0
    elif rounded_value > 2.0:
        rounded_value = 2.0
    predicted_label = rounded_value_to_label.get(rounded_value, "Unknown")
    return predicted_label

def on_connect4(client, userdata, flags, rc):
    print(f"Connected to Broker1 with result code {str(rc)}")
    client.subscribe(mqtt_topic4)

def on_connect2(client, userdata, flags, rc):
    print(f"Connected to Broker2 with result code {str(rc)}")
    client.subscribe(mqtt_topic2)

def on_connect3(client, userdata, flags, rc):
    print(f"Connected to Broker3 with result code {str(rc)}")
    client.subscribe(mqtt_topic3)

def on_message4(client, userdata, msg):
    data_raw = msg.payload.decode()
    data = float(data_raw.split("= ")[1])
    if data != "adadsa":
        humidity = float(data)  # Assuming data is a single humidity value
        result = classify(humidity)
        predictions.append(result)  # Store (sensor_id, result) tuple
        if (predictions[0] != "Unknown") and (len(predictions) == 3):
            # print(predictions) #Tampilkan jika perlu bukti
            if len(predictions) == 3:
                majority_result = check_majority()
                display_all(majority_result)
                predictions.clear()

def on_message2(client, userdata, msg):
    data_raw = msg.payload.decode()
    data = float(data_raw.split("= ")[1])
    if data != "adadsa":
        humidity = float(data)  # Assuming data is a single humidity value
        result = classify(humidity)
        predictions.append(result)  # Store (sensor_id, result) tuple
        if (predictions[0] != "Unknown") and (len(predictions) == 3):
            # print(predictions) #Tampilkan jika perlu bukti
            if len(predictions) == 3:
                majority_result = check_majority()
                display_all(majority_result)
                predictions.clear()
        # display_all()
        
    time.sleep(1)

def on_message3(client, userdata, msg):
    data = msg.payload.decode()
    if data != "adadsa":
        humidity = float(data)  # Assuming data is a single humidity value
        result = classify(humidity)
        predictions.append(result)  # Store (sensor_id, result) tuple
        if (predictions[0] != "Unknown") and (len(predictions) == 3):
            # print(predictions) #Tampilkan jika perlu bukti
            if len(predictions) == 3:
                majority_result = check_majority()
                display_all(majority_result)
                predictions.clear()
        # # else:
        # #     predictions.clear()
    time.sleep(1)

def display_all(majority_result):
    print(f"Majority Result: {majority_result}")
    socketio.emit("majority_result", {'humid': majority_result})


def SOKET(majority_result):
    socketio.emit("majority_result", {"humid": majority_result})
    print(f"Data successfully emitted: {majority_result}")


# Function to check majority prediction
def check_majority():
    kering = predictions.count("Kering")
    normal = predictions.count("Normal")
    basah = predictions.count("Basah")

    if kering > normal and kering > basah:
        return "Kering"
    elif normal > kering and normal > basah:
        return "Normal"
    elif basah > kering and basah > normal:
        return "Basah"
    else:
        return "Normal"

mqtt_broker2 = "broker.mqtt-dashboard.com"
mqtt_port2 = 1883
mqtt_topic2 = "ican"

mqtt_broker4 = "broker.mqtt-dashboard.com"
mqtt_port4 = 1883
mqtt_topic4 = "addin"

mqtt_broker3 = "broker.mqtt-dashboard.com"
mqtt_port3 = 1883
mqtt_topic3 = "pian"

client2 = mqtt.Client()
client2.on_connect = on_connect2
client2.on_message = on_message2
client2.connect(mqtt_broker2, mqtt_port2, 60)
client2.loop_start()

client4 = mqtt.Client()
client4.on_connect = on_connect4
client4.on_message = on_message4
client4.connect(mqtt_broker4, mqtt_port4, 60)
client4.loop_start()

client3 = mqtt.Client()
client3.on_connect = on_connect3
client3.on_message = on_message3
client3.connect(mqtt_broker3, mqtt_port3, 60)
client3.loop_start()


@app.route('/')
def home():
    return render_template('predict_temperature.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.json
        #make your code here

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False) # Assuming you want to run the Flask app synchronously
socketio.run(app)