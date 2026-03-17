from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    from .views import (
        home, upload, admin, route
    )
    app.register_blueprint(home.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(route.bp)

    from .api import (
        waste, trip
    )
    app.register_blueprint(waste.bp)
    app.register_blueprint(trip.bp)

    socketio.init_app(app)

    return app
