import requests

URL = 'http://router.project-osrm.org'


def trip(coordinates, profile='driving'):
    if type(coordinates) is list:
        coordinates = ';'.join(coordinates)

    response = requests.request(
        method='GET',
        url=f'{URL}/trip/v1/{profile}/{coordinates}?geometries=geojson'
    )

    return response.json()
