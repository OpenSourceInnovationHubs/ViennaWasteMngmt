from flask import (
    Blueprint, render_template, request
)
import eventlet
import json
import requests

from ..service.orion_ld import (
    entities, delete, count
)

bp = Blueprint('admin', __name__)

@bp.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        action = request.form['action']

        if action == 'delete-all':
            eventlet.spawn(delete_all)


    return render_template('admin.html')


def delete_all():
    from .. import socketio

    total_count = count('WasteContainerIsle') + count('WasteContainer')

    deleted = 0
    while deleted < total_count:
        isle_entities = entities('WasteContainerIsle')
        delete_entities(isle_entities)

        container_entities = entities('WasteContainer')
        delete_entities(container_entities)

        deleted += len(isle_entities)
        deleted += len(container_entities)

        eventlet.sleep(0.1)

        msg = { 'current': deleted, 'total': total_count }
        print(msg)
        socketio.emit('admin_progress', msg)
    

def delete_entities(entities):
    ids = list()

    for entity in entities:
        ids.append(entity['id'])
    
    delete(ids)
