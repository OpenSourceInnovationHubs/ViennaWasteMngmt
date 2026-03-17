import requests
import json

URL = 'https://orion-ld-fiware-test.apps.okd.cs.technikum-wien.at/ngsi-ld/v1'
CTX = 'https://raw.githubusercontent.com/smart-data-models/dataModel.WasteManagement/master/context.jsonld'


def entities(type, limit=250, offset=0, q=None):
    return query(
        method='GET',
        endpoint='/entities',
        type=type,
        limit=limit,
        offset=offset,
        q=q
    ).json()


def upsert(entities):
    '''Resource: entityOperations/upsert

    https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.08.01_60/gs_cim009v010801p.pdf
    Page: 274
    '''
    query(
        method='POST',
        endpoint='/entityOperations/upsert',
        data=json.dumps(entities)
    )


def delete(ids):
    '''Resource: entityOperations/delete

    https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.08.01_60/gs_cim009v010801p.pdf
    Page: 278
    '''
    query(
        method='POST',
        endpoint='/entityOperations/delete',
        content_type='application/json',
        data=json.dumps(ids)
    )


def count(type, q=None):
    '''Counting number of results 

    https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.08.01_60/gs_cim009v010801p.pdf
    Page: 235
    '''
    params = {
        'options': 'count'
    }

    res = query(
        method='GET',
        endpoint='/entities',
        type=type,
        params=params,
        limit=0,
        q=q
    )

    return int(res.headers.get('Ngsild-Results-Count'))


def geo_near(type, lat, lng, dist=200, limit=1000, offset=0, q=None):
    '''NGSI-LD Geoquery Language

    https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.08.01_60/gs_cim009v010801p.pdf
    Page: 83
    '''
    params = {
        'georel': f'near;maxDistance=={dist}',
        'geometry': 'Point',
        'coordinates': f'[{lng}, {lat}]',
    }
    
    return query(
        method='GET',
        endpoint='/entities',
        type=type,
        params=params,
        limit=limit,
        offset=offset,
        q=q
    ).json()


def geo_within(type, coordinates, limit=1000, offset=0, q=None):
    '''NGSI-LD Geoquery Language

    https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.08.01_60/gs_cim009v010801p.pdf
    Page: 83
    '''
    params = {
        'georel': 'within',
        'geometry': 'Polygon',
        'coordinates': f'[{coordinates}]',
    }

    return query(
        method='GET',
        endpoint='/entities',
        type=type,
        params=params,
        limit=limit,
        offset=offset,
        q=q
    ).json()


def query(method, endpoint, type=None, params={}, limit=None, offset=None, q=None, content_type=None, data=None, server=URL):
    if type is not 0:
        params['type'] = type

    if limit is not 0:
        params['limit'] = limit

    if offset is not 0:
        params['offset'] = offset
    
    if q is not None:
        params['q'] = q
    
    headers = {
        'Link': f'<{CTX}>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
    }

    if content_type is not None:
        headers['Content-Type'] = content_type

    response = requests.request(
        method=method,
        url=f'{server}{endpoint}',
        params=params,
        headers=headers,
        data=data
    )

    return response
