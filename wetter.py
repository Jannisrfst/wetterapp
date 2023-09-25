from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# weather-Klasse, die die weatherdaten speichert und Observers führt
class Weather:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Weather, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.observers = []
        self.temperature = 0
        self.humidity = 0
        self.pressure = 0

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def set_weatherdata(self, temperature, humidity, pressure):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.notify_observers()

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

# Observerklasse, die die weatherdaten speichert und an die Clients sendet
class weatherObserver(threading.Thread):
    def __init__(self, weather_data):
        super(weatherObserver, self).__init__()
        self.weather_data = weather_data

    def run(self):
        while True:
            self.update(self.weather_data)
            time.sleep(60)

    def update(self, weather_data):
        self.temperature = weather_data.temperature
        self.humidity = weather_data.humidity
        self.pressure = weather_data.pressure

        # Die Wetterdaten an die Clients senden
        emit('weather_update', {'temperature': self.temperature, 'humidity': self.humidity, 'pressure': self.pressure})

weatherS = Weather()

@app.route('/')
def index():  
    print("Print")
    return render_template('index.html')

@socketio.on('register')
def register(data):
    observer1 = weatherObserver(weatherS)
    latitude = data.get('lat')
    longitude = data.get('long')

    weatherS.add_observer(observer1)
    observer1.start()

    emit('registration_successful', {'message': 'success!'})


if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000)
