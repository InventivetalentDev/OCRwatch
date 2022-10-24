import csv
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


def append_to_csv(result):
    fields = [result['time'], result['match']['mode'], result['match']['map'], result['match']['time'], result['self']['hero']]

    for i in range(0, 5):
        fields.append(result['players']['allies'][i]['name'])
        fields.append(result['players']['allies'][i]['elims'])
        fields.append(result['players']['allies'][i]['assists'])
        fields.append(result['players']['allies'][i]['deaths'])
        fields.append(result['players']['allies'][i]['dmg'])
        fields.append(result['players']['allies'][i]['heal'])
        fields.append(result['players']['allies'][i]['mit'])

    for i in range(0, 5):
        fields.append(result['players']['enemies'][i]['name'])
        fields.append(result['players']['enemies'][i]['elims'])
        fields.append(result['players']['enemies'][i]['assists'])
        fields.append(result['players']['enemies'][i]['deaths'])
        fields.append(result['players']['enemies'][i]['dmg'])
        fields.append(result['players']['enemies'][i]['heal'])
        fields.append(result['players']['enemies'][i]['mit'])

    with open(r'log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)


influx_client = InfluxDBClient.from_config_file("config.ini")
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)


def write_to_influx(result):
    parsed_time = datetime.strptime(result['match']['time'], "%M:%S")
    duration = timedelta(minutes=parsed_time.minute, seconds=parsed_time.second)

    ally_total_elims = 0
    ally_total_assists = 0
    ally_total_deaths = 0
    ally_total_dmg = 0
    ally_total_heal = 0
    ally_total_mit = 0

    for i in range(0, 5):
        ally_total_elims += result['players']['allies'][i]['elims']
        ally_total_assists += result['players']['allies'][i]['assists']
        ally_total_deaths += result['players']['allies'][i]['deaths']
        ally_total_dmg += result['players']['allies'][i]['dmg']
        ally_total_heal += result['players']['allies'][i]['heal']
        ally_total_mit += result['players']['allies'][i]['mit']

    enemy_total_elims = 0
    enemy_total_assists = 0
    enemy_total_deaths = 0
    enemy_total_dmg = 0
    enemy_total_heal = 0
    enemy_total_mit = 0

    for i in range(0, 5):
        enemy_total_elims += result['players']['enemies'][i]['elims']
        enemy_total_assists += result['players']['enemies'][i]['assists']
        enemy_total_deaths += result['players']['enemies'][i]['deaths']
        enemy_total_dmg += result['players']['enemies'][i]['dmg']
        enemy_total_heal += result['players']['enemies'][i]['heal']
        enemy_total_mit += result['players']['enemies'][i]['mit']

    p = Point("match_stats") \
        .tag("mode", result['match']['mode']) \
        .tag("map", result['match']['map']) \
        .tag("hero", result['self']['hero']) \
        .tag("competitive", 'true' if result['match']['competitive'] else 'false')\
        .tag("state", result['state'])\
        .field("duration", duration.total_seconds())\
        .field("total_ally_elims", ally_total_elims)\
        .field("total_ememy_elims", enemy_total_elims)\
        .field("total_ally_deaths", ally_total_deaths)\
        .field("total_enemy_deaths", enemy_total_deaths)
    influx_write_api.write(bucket="overwatch", record=p)
