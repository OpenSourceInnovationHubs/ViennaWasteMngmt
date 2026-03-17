from flask import (
    Blueprint, request
)

from ..service.orion_ld import entities
from ..service.osrm import trip

bp = Blueprint('trip', __name__, url_prefix='/api')

@bp.route('/district')
def district():
    postalCode = request.args.get('postalcode')
    fillingLevel= request.args.get('fillinglevel')
    storedWasteKind= request.args.get('storedWasteKind')

    wasteContainers = entities(
        type='WasteContainer',
        q=f'(address[postalCode]=="{postalCode}";fillingLevel<={fillingLevel};storedWasteKind=="{storedWasteKind}")'
    )

    coordinates = []
    for container in wasteContainers:
        coordinates.append(','.join(str(x) for x in container['location']['value']['coordinates']))

    return trip(coordinates=coordinates)
