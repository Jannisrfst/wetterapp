from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import random
import time

class WeatherData:
    def __init__(self):
        self.humidity = random.randint(0, 100)
        self.pressure = random.randint(950, 1050)
        self.temperature = random.randint(0, 40)
        self._observers = {}

    @staticmethod
    def get_instance():
        if not hasattr(WeatherData, "_instance"):
            WeatherData._instance = WeatherData()
        return WeatherData._instance

    def toJson(self):
        return {"humidity": self.humidity, "pressure": self.pressure, "temperature": self.temperature}

    def add_observer(self, observer):
        self._observers[observer.sid] = observer

    def notify_observers(self):
        for observer in self._observers.values():
            observer.on_update(self)

    def update_weather_data(self):
        while not thread_stop_event.is_set():
            for observer in self._observers.values():
                self.humidity = random.randint(0, 100)
                self.pressure = random.randint(950, 1050)
                self.temperature = random.randint(0, 40)
                observer.on_update(self)
            time.sleep(5)  # update every 5 seconds


    def get_weather_data_for_location(self, latitude, longitude):
        # Use the latitude and longitude to generate weather data.
        # This is just a simple example. In a real application, you would
        # probably want to use a more sophisticated method to generate the weather data.
        self.humidity = random.randint(0, 100)
        self.pressure = random.randint(950, 1050)
        self.temperature = random.randint(0, 40)
        return self.toJson()

class WeatherObserver:
    def __init__(self, socketio, sid):
        self.socketio = socketio
        self.sid = sid

    def on_update(self, weather_data):
        print("Weather update:", weather_data.toJson())
        self.socketio.emit("weather_update", weather_data.toJson(), room=self.sid)

def background_thread():
    weather_data.update_weather_data()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
weather_data = WeatherData.get_instance()
thread_stop_event = Event()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('location_data')
def handle_location_data(data):
    observer = WeatherObserver(socketio, request.sid)
    weather_data.add_observer(observer)
    weather_data_for_location = weather_data.get_weather_data_for_location(data['latitude'], data['longitude'])
    emit('weather_update', weather_data_for_location)

if __name__ == '__main__':
    thread = Thread(target=background_thread)
    thread.start()
    socketio.run(app)
