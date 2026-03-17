from flask import (
    Blueprint, render_template, request
)
import eventlet
import json
import requests
import random

bp = Blueprint('upload', __name__)

@bp.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':
        file = request.files['file']
        file_contents = file.read().decode('utf-8')
        data = json.loads(file_contents)

        eventlet.spawn(process_file, data.get('features'))
        
    return render_template('upload.html')


def process_file(features):
    from .. import socketio

    batch = list()
    for idx, data in enumerate(features):
        isle_entity = create_waste_isle_entity(data)

        waste_entities = create_waste_entities(isle_entity, data['properties']['FRAKTION_TEXT'])
        batch.extend(waste_entities)
        
        if len(batch) >= 500 or idx + 1 == len(features):
            post_waste_entities(batch)
            batch = list()

            eventlet.sleep(0.1)

            msg = { 'current': idx + 1, 'total': len(features) }
            print(msg)
            socketio.emit('file_progress', msg)


def create_waste_isle_entity(data):
    id = data['properties']['SE_SDO_ROWID']
    coordinates = data['geometry']['coordinates']
    address_locality = 'Vienna'
    address_country = 'AT'
    if len(str(data['properties']['BEZIRK'])) == 1:
        postal_code = '10' + str(data['properties']['BEZIRK']) + '0'
    else:
        postal_code = '1' + str(data['properties']['BEZIRK']) + '0'
    street_address = data['properties']['STRASSE'] + ('' if data['properties']['ONR'] is None else ' ' + data['properties']['ONR'])

    return {
        "id": f"urn:ngsi-ld:WasteContainerIsle:{id}",
        "type": "WasteContainerIsle",
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": coordinates
            }
        },
        "address": {
            "type": "Property",
            "value": {
                "addressCountry": address_country,
                "addressLocality": address_locality,
                "postalCode": postal_code,
                "streetAddress": street_address
            }
        },
        "seeAlso": {
            "type": "Property",
            "value": [ "https://www.wien.gv.at/umwelt/ma48/beratung/muelltrennung/index.html" ]
        },
        "@context": [
            "https://raw.githubusercontent.com/smart-data-models/dataModel.WasteManagement/master/context.jsonld"
        ]
    }


def create_waste_entities(waste_isle, types):
    entities = list()

    containers = list()
    container_ids = list()
    for idx, type in enumerate(types.replace(' ', '').split(',')):
        if type == '':
            continue

        container = create_waste_container_entity(waste_isle, idx + 1, type)
        containers.append(container)
        container_ids.append(container['id'])

    waste_isle['refWasteContainer'] = {
        "type": "Property",
        "value": container_ids
    }

    entities.append(waste_isle)
    entities.extend(containers)

    return entities


def create_waste_container_entity(waste_isle, number, type):
    id = waste_isle['id'].replace('Isle', '') + ':' + str(number)

    if type == 'Leichtverpackungen' or type == 'Leichtverp': # mistake in city data
        kind = 'plastic'
        color = 'yellow'
        uri = 'https://www.wien.gv.at/umwelt/ma48/beratung/muelltrennung/plastikflaschen/plastikflaschen.html'
    if type == 'Altglas' or type == 'A': # mistake in city data
        kind = 'glass'
        color = 'green'
        uri = 'https://www.wien.gv.at/umwelt/ma48/beratung/muelltrennung/altglas.html'
    if type == 'Biomüll' or type == 'B': # mistake in city data
        kind = 'organic'
        color = 'brown'
        uri = 'https://www.wien.gv.at/umwelt/ma48/beratung/muelltrennung/biogener-abfall/sammlung.html'
    if type == 'Altpapier':
        kind = 'paper'
        color = 'red'
        uri = 'https://www.wien.gv.at/umwelt/ma48/beratung/muelltrennung/altpapier.html'
    
    try:
        if kind is None:
            print(type)
    except:
        print(waste_isle['id'])
        print(type)

    return {
        "id": id,
        "type": "WasteContainer",
        "location": waste_isle['location'],
        "address": waste_isle['address'],
        "storedWasteKind": {
            "type": "Property",
            "value": kind
        },
        "category": {
            "type": "Property",
            "value": "dumpster"
        },
        "binColor": {
            "type": "Property",
            "value": color
        },
        "fillingLevel": {
            "type": "Property",
            "value": random.uniform(0, 1)
        },
        "seeAlso": {
            "type": "Property",
            "value": [ uri ]
        },
        "refWasteContainerIsle": {
            "type": "Relationship",
            "object": waste_isle['id']
        },
        "@context": [
            "https://raw.githubusercontent.com/smart-data-models/dataModel.WasteManagement/master/context.jsonld"
        ]
    }


def post_waste_entities(entities):
    response = requests.post(
        'https://orion-ld-fiware-test.apps.okd.cs.technikum-wien.at/ngsi-ld/v1/entityOperations/upsert', 
        json.dumps(entities),
        headers={
            'Content-Type': 'application/ld+json'
        }
    )
