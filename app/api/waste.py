from flask import (
    Blueprint, request
)

from ..service.orion_ld import geo_within, geo_near

bp = Blueprint('waste', __name__, url_prefix='/api')

@bp.route('/location')
def location():
    lat = request.args.get('lat')
    lng = request.args.get('lng')

    return geo_near(
        type='WasteContainer',
        lat=lat,
        lng=lng
    )


@bp.route('/polygon')
def polygon():
    polygon = request.args.get('polygon')
    filter = request.args.get('filter')

    total = list()
    entities = geo_within(
        type='WasteContainer', 
        coordinates=polygon,
       q=f'storedWasteKind=={filter}'
    )
    while len(entities) == 1000:
        total.extend(entities)
        entities = geo_within(
            type='WasteContainer', 
            coordinates=polygon,
            offset=1000,
            q=f'storedWasteKind=={filter}'
        )
    
    total.extend(entities)
    return total


# https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.08.01_60/gs_cim009v010801p.pdf
# Page: 83
#
#def get_container_near(lat, lng):
#    response = requests.get(
#        'https://orion-ld-fiware-test.apps.okd.cs.technikum-wien.at/ngsi-ld/v1/entities',
#        params={
#            'type': 'https://smartdatamodels.org/dataModel.WasteManagement/WasteContainer',
#            'georel': 'near;maxDistance==200',
#            'geometry': 'Point',
#            'coordinates': f'[{lng}, {lat}]',
#            'q': 'storedWasteKind=="plastic"'
#        },
#        headers={
#            'Link': '<https://raw.githubusercontent.com/smart-data-models/dataModel.WasteManagement/master/context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
#        }
#    )
#
#    return response.json()
#
#
#def get_container_polygon(polygon, filter, offset=0):
#    response = requests.get(
#        'https://orion-ld-fiware-test.apps.okd.cs.technikum-wien.at/ngsi-ld/v1/entities',
#        params={
#            'type': 'WasteContainer',
#            'limit': 1000,
#            'offset': offset,
#            'georel': 'within',
#            'geometry': 'Polygon',
#            'coordinates': f'[{polygon}]',
#            'q': f'storedWasteKind=={filter}'
#        },
#        headers={
#            'Link': '<https://raw.githubusercontent.com/smart-data-models/dataModel.WasteManagement/master/context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
#        }
#    )
#
#    return response.json()
#
