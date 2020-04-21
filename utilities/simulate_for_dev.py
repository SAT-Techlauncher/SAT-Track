from config import conf
import json

with open(conf.RIPE_DIR_ + 'satellites.json', 'r') as f:
    satellites = json.loads(f.read())


for satellite in satellites:
    print(satellite['name'])
