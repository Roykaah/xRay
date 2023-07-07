import numpy as np
import psutil
import time
import pandas as pd
import cv2
import json 
import csv
#read a json file
def read_json(filename):
    with open(filename, 'r') as f:
        datastore = json.load(f)
    return datastore

#read all json keys and values
def read_json_keys(filename):
    with open(filename, 'r') as f:
        datastore = json.load(f)
        json_object = json.loads(datastore)
        for key, value in json_object.items():
            print(key, ":", value)

#read_json_keys('relatorios_finais/Bruna1688233874.9492667.json')
#str to json
#json_object = json.loads(json_string)

#see 

process = psutil.Process()
cpu_before = process.cpu_percent()
memory_before = process.memory_info().rss
print(process.memory_info())
memory_after = process.memory_info().rss # AGORA
memory_consumed = abs(memory_after - memory_before)
print(f"Consumo de memória: {memory_consumed/1024/1024:.2f} MB")

cpu_after = process.cpu_percent()
cpu_consumed = cpu_after - cpu_before
print(f"Uso da CPU: {cpu_consumed/10:.2f}%")