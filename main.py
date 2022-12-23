# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import pandas as pd
import os
import datetime
import logging
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import time
from tqdm import tqdm

arcgis_user = os.environ.get('ArcGIS_USER', '')
arcgis_pass = os.environ.get('ArcGIS_PASS', '')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(filename='errors.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)
    start_time = time.time()

    gis = GIS(username=arcgis_user, password=arcgis_pass)
    print("---ARCGIS ONLINE CONECTED IN %s seconds ---" % (time.time() - start_time))
    # find all stations
    r = requests.get('https://api.gios.gov.pl/pjp-api/rest/station/findAll')
    j = r.json()
    stacje = pd.json_normalize(j)
    stacje.to_csv('stacje.csv')
    now = datetime.datetime.now()
    #
    stanowiska = pd.json_normalize({
        'id': 806, 'stationId': 142,
        'param': {'paramName': 'tlenek węgla', 'paramFormula': 'CO', 'paramCode': 'CO', 'idParam': 8}
    })
    #
    # r = requests.get('https://api.gios.gov.pl/pjp-api/rest/data/getData/{0}'.format(92))
    # dic = r.json()
    pomiarowe_PM10 = pd.DataFrame({})
    pomiarowe_CO = pd.DataFrame({})
    for sid in tqdm(stacje['id']):
        # get Stanowiska pomiarowe
        r = requests.get('https://api.gios.gov.pl/pjp-api/rest/station/sensors/{0}'.format(sid))
        stanowiska_pomiarowe = r.json()
        for stanowisko in stanowiska_pomiarowe:
            stanowiska = pd.concat([stanowiska, pd.json_normalize(stanowisko)], ignore_index=True)

        # # get Indeks jakości powietrza
        # r = requests.get('https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/{0}'.format(id))
        # indeks_jakosci_powietrza = r.json()
        #
        # print(indeks_jakosci_powietrza)
    print("---FIRST STAGE DOWNL IN %s seconds ---" % (time.time() - start_time))
    # print(len(stanowiska['id'].unique()))
    # i = 1
    for sen_id in tqdm(stanowiska['id'].unique()):

        r = requests.get('https://api.gios.gov.pl/pjp-api/rest/data/getData/{0}'.format(sen_id))
        dane_pomiarowe = r.json()

        if dane_pomiarowe['key'] == 'PM10':
            try:
                val = pd.DataFrame.from_dict(pd.json_normalize(dane_pomiarowe['values']))
                name = stacje[stacje['id'] == stanowiska[stanowiska['id'] == sen_id].iloc[0]['stationId']] \
                    .iloc[0]['stationName']
                val['stacja'] = name
                pomiarowe_PM10 = pd.concat([pomiarowe_PM10, val], ignore_index=True)
            except Exception as e:
                logger.error(e)

        if dane_pomiarowe['key'] == 'CO':
            try:
                val = pd.DataFrame.from_dict(pd.json_normalize(dane_pomiarowe['values']))
                name = stacje[stacje['id'] == stanowiska[stanowiska['id'] == sen_id].iloc[0]['stationId']] \
                    .iloc[0]['stationName']
                val['stacja'] = name
                pomiarowe_CO = pd.concat([pomiarowe_CO, val], ignore_index=True)
            except Exception as e:
                logger.error(e)

        # print(i)
        # i += 1

    print("---LAST STAGE DOWNL IN %s seconds ---" % (time.time() - start_time))

    stanowiska.to_csv('stanowsika.csv')
    pomiarowe_PM10.to_csv('pomiarowe_PM10.csv')
    pomiarowe_CO.to_csv('pomiarowe_CO.csv')

    item_to_update = '1899af778abe4d809e870727ea602530'
    stacje_to_up = gis.content.get(item_to_update)
    stacje_to_up_flayer = FeatureLayerCollection.fromitem(stacje_to_up)
    res = stacje_to_up_flayer.manager.overwrite('stacje.csv')
    stacje_to_up.update(item_properties={
        "title": "stacje_aktualizowane", "description": "Data of update: " + str(now)})

    item_to_update2 = '0586fc9231484f35a8bd02ecdbc0260e'
    stanowiska_to_up = gis.content.get(item_to_update2)
    stanowiska_to_up_flayer = FeatureLayerCollection.fromitem(stanowiska_to_up)
    stanowiska_to_up_flayer.manager.overwrite('stanowsika.csv')
    stanowiska_to_up.update(item_properties={
        "title": "stanowiska_aktualizowane", "description": "Data of update: " + str(now)})

    item_to_update3 = 'bfa7b340680a4eefbb2b2bf0ade4e89f'
    pomiarowe_PM10_to_up = gis.content.get(item_to_update3)
    pomiarowe_PM10_to_up_flayer = FeatureLayerCollection.fromitem(pomiarowe_PM10_to_up)
    pomiarowe_PM10_to_up_flayer.manager.overwrite('pomiarowe_PM10.csv')
    pomiarowe_PM10_to_up.update(item_properties={
        "title": "pomiarowe_PM10_aktualizowane", "description": "Data of update: " + str(now)})

    item_to_update4 = '7d9c66e07263468e93ad266d931aa500'
    pomiarowe_CO_to_up = gis.content.get(item_to_update4)
    pomiarowe_CO_to_up_flayer = FeatureLayerCollection.fromitem(pomiarowe_CO_to_up)
    pomiarowe_CO_to_up_flayer.manager.overwrite('pomiarowe_CO.csv')
    pomiarowe_CO_to_up.update(item_properties={
        "title": "pomiarowe_CO_aktualizowane", "description": "Data of update: " + str(now)})
    print("---ALL LAST %s seconds ---" % (time.time() - start_time))
