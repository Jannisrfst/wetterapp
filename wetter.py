from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread
import random
import time

class WeatherData:
    def __init__(self):
        self.humidity = random.randint(0, 100)
        self.pressure = random.randint(950, 1050)
        self.temperature = random.randint(0, 40)
        self._registered = False
        self._observers = []

    @staticmethod
    def get_instance():
        if not hasattr(WeatherData, "_instance"):
            WeatherData._instance = WeatherData()
        return WeatherData._instance

    def toJson(self):
        return {"humidity": self.humidity, "pressure": self.pressure, "temperature": self.temperature}

    def set_registered(self, registered):
        self._registered = registered

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.on_update(self)

class WeatherObserver:
    def __init__(self, socketio):
        self.socketio = socketio

    def on_update(self, weather_data):
        print("Weather update:", weather_data.toJson())
        self.socketio.emit("weather_update", weather_data.toJson())

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
weather_data = WeatherData.get_instance()

observer = WeatherObserver(socketio)
weather_data.add_observer(observer)

@app.route('/')
def index():
    return render_template('index.html')

def generate_weather_data():
    while True:
        if weather_data._registered:
            weather_data.humidity = random.randint(0, 100)
            weather_data.pressure = random.randint(950, 1050)
            weather_data.temperature = random.randint(0, 40)
            weather_data.notify_observers()
            time.sleep(5)

@socketio.on('location_data')
def handle_location_data(data):
    print('Received location data:', data)
    weather_data.set_registered(True)
    Thread(target=generate_weather_data).start()

if __name__ == '__main__':
    socketio.run(app)
