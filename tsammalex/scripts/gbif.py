"""
- collect occurrence data from gbif
- match against shapes of ecoregions

http://stackoverflow.com/a/20793808


http://www.gbif.org/species/5219404


robert@astroman:~$ curl "http://api.gbif.org/v1/species/match?name=Acacia+erioloba" | jsonpp | less

{
    "canonicalName": "Acacia erioloba",
    "class": "Magnoliopsida",
    "classKey": 220,
    "confidence": 100,
    "family": "Fabaceae",
    "familyKey": 5386,
    "genus": "Acacia",
    "genusKey": 2978223,
    "kingdom": "Plantae",
    "kingdomKey": 6,
    "matchType": "EXACT",
    "order": "Fabales",
    "orderKey": 1370,
    "phylum": "Magnoliophyta",
    "phylumKey": 49,
    "rank": "SPECIES",
    "scientificName": "Acacia erioloba E.Mey.",
    "species": "Acacia erioloba",
    "speciesKey": 2980134,
    "synonym": false,
    "usageKey": 2980134
}


robert@astroman:~$ curl "http://api.gbif.org/v1/occurrence/search?taxonKey=2980134" | jsonpp | less

{
    "count": 455,
    "endOfRecords": false,
    "limit": 20,
    "offset": 0,
    "results": [
        {
            "basisOfRecord": "HUMAN_OBSERVATION",
            "catalogNumber": "1920798038",
            "class": "Magnoliopsida",
            "classKey": 220,
            "collectionCode": "naturgucker",
            "country": "Namibia",
           "countryCode": "NA",
            "datasetKey": "6ac3f774-d9fb-4796-b3e9-92bf6c81c084",
            "day": 25,
            "decimalLatitude": -20.42299,
            "decimalLongitude": 17.33196,
            "eventDate": "2012-09-24T22:00:00.000+0000",
            "extensions": {},
            "facts": [],
            "family": "Fabaceae",
            "familyKey": 5386,
            "gbifID": "920182471",
            "genericName": "Acacia",
            "genus": "Acacia",
            "genusKey": 2978223,
            "geodeticDatum": "WGS84",
            "identifiers": [],
            "institutionCode": "naturgucker",
            "issues": [
                "COORDINATE_ROUNDED",
                "GEODETIC_DATUM_ASSUMED_WGS84"
            ],
            "key": 920182471,
            "kingdom": "Plantae",
            "kingdomKey": 6,
            "lastCrawled": "2014-12-04T15:14:11.758+0000",
            "lastInterpreted": "2014-11-14T15:14:44.603+0000",
            "lastParsed": "2014-11-14T15:14:44.423+0000",
            "locality": "Waterberg",
            "month": 9,
            "order": "Fabales",
            "orderKey": 1370,
            "phylum": "Magnoliophyta",
            "phylumKey": 49,
            "protocol": "BIOCASE",
            "publishingCountry": "DE",
            "publishingOrgKey": "bb646dff-a905-4403-a49b-6d378c2cf0d9",
            "recordedBy": "881932368",
            "relations": [],
            "scientificName": "Acacia erioloba E.Mey.",
            "species": "Acacia erioloba",
            "speciesKey": 2980134,
            "specificEpithet": "erioloba",
            "taxonKey": 2980134,
            "taxonRank": "SPECIES",
            "year": 2012
        },
"""
import json

import requests
from clld.util import slug
from clld.scripts.util import parsed_args


BASE_URL = 'http://api.gbif.org/v1'


def api(path, **params):
    res = requests.get('/'.join([BASE_URL, path]), params=params).json()
    #print res
    return res


def get_ecoregions(species):
    kw = dict(
        taxonKey=api('species/match', name=species)['speciesKey'],
        basisOfRecord='HUMAN_OBSERVATION',
        hasCoordinate='true',
        limit=100)
    ocs = api('occurrence/search', **kw)['results']
    with open('%s.json' % slug(unicode(species)), 'w') as fp:
        json.dump(ocs, fp)


def main(args):
    pass


if __name__ == '__main__':
    main(parsed_args())
