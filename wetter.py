
import random
import time
import json
from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
from threading import Thread


# Singleton Pattern
class WeatherData:
    def __init__(self):
        self.humidity = random.randint(0, 100)
        self.pressure = random.randint(950, 1050)
        self.temperature = random.randint(0, 40)

        self._observers = []

    @staticmethod
    def get_instance():
        if not hasattr(WeatherData, "_instance"):
            WeatherData._instance = WeatherData()
        return WeatherData._instance

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        try:
            self._observers.remove(observer)
        except:
            pass

    def notify_observers(self):
        for observer in self._observers:
            observer.on_update(self)
    
    def toJson(self):
        return {"humidity": self.humidity, "pressure": self.pressure, "temperature": self.temperature}

# Observer Pattern
class WeatherObserver:
    def __init__(self, socketio):
        self.socketio = socketio

    def on_update(self, weather_data):
        print("Weather update:", weather_data.toJson())
        self.socketio.emit("weather_update", weather_data.toJson())

# Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app)

# Weather Data
weather_data = WeatherData.get_instance()

# Observer
observer = WeatherObserver(socketio)
weather_data.add_observer(observer)

# WebSocket
@socketio.on("connect")
def connect():
    print("Client connected")
    socketio.emit("weather_connected", {"message": "Connected to weather station"})

@socketio.on("disconnect")
def disconnect():
    socketio.emit("weather_disconnected", {"message": "Disconnected from weather station"})

# Generate Weather Data
def generate_weather_data():
    while True:
        weather_data.humidity = random.randint(0, 100)
        weather_data.pressure = random.randint(950, 1050)
        weather_data.temperature = random.randint(0, 40)

        # Send weather data to observers
        weather_data.notify_observers()

        # Sleep for 1 second
        time.sleep(1)

# Start generating weather data
t = Thread(target=generate_weather_data)
t.daemon = True
t.start()



# Render Website
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)
