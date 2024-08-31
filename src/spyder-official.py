import multiprocessing
import asyncio
from typing import Literal
import httpx
import datetime
import json
from typing import TypeAlias
import sqlite3

RAIL_CHAR:TypeAlias = Literal['K', 'T', 'Z', 'D', 'G', 'C', '', 'S', 'Y']
RAIL_CHARS = ('K', 'T', 'Z', 'D', 'G', 'C', '', 'S', 'Y')

def get_route_train_no(char: RAIL_CHAR, i: int) -> str| None:
    url = "https://search.12306.cn/search/v1/train/search?keyword="+char+str(i)+"&date="+datetime.datetime.now().strftime("%Y%m%d")
    data = httpx.get(url=url)
    if data.status_code == 200:
        # print(data.content)
        try:
            data = data.content.decode('gbk')
        except UnicodeDecodeError:
            data = data.content.decode('utf-8')
        try:
            data = json.loads(data)['data']
            # return data[0]['train_no']
            return data[0]['train_no']
        except Exception:
            pass
def get_train_info(train_no: str) -> dict| None:
    if not train_no:
        return None
    url = "https://kyfw.12306.cn/otn/queryTrainInfo/query?leftTicketDTO.train_no="+train_no+"&leftTicketDTO.train_date="+datetime.datetime.now().strftime("%Y-%m-%d")+"&rand_code="
    data = httpx.get(url=url)
    if data.status_code == 200:
        data = data.content.decode()
        data = json.loads(data)
        return data
    
def record_data(data: dict):
    print(data)
    data = data['data']['data']
    for item in data:
        arrive_day_str = item.get('arrive_day_str', '')
        station_name = item.get('station_name', '')
        train_class_name = item.get('train_class_name', '')
        is_start = item.get('is_start', '')
        service_type = item.get('service_type', '')
        end_station_name = item.get('end_station_name', '')
        arrive_time = item.get('arrive_time', '')
        start_station_name = item.get('start_station_name', '')
        station_train_code = item.get('station_train_code', '')
        arrive_day_diff = item.get('arrive_day_diff', '')
        start_time = item.get('start_time', '')
        station_no = item.get('station_no', '')

        conn = sqlite3.connect('train.db')
        conn.execute('INSERT INTO train_info VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (arrive_day_str, station_name, train_class_name, is_start, service_type, end_station_name, arrive_time, start_station_name, station_train_code, arrive_day_diff, start_time, station_no))
        conn.commit()
        conn.close()
        # f.write(json.dumps(data, ensure_ascii=False, indent=4)+",\n")

def main(char: RAIL_CHAR, i: int):
    train_no = get_route_train_no(char, i)
    if train_no:
        data = get_train_info(train_no)
        if data:
            record_data(data)
    else:
        return
if __name__ == '__main__':
    sqlite3.connect('train.db')
    conn = sqlite3.connect('train.db')
    conn.execute('CREATE TABLE IF NOT EXISTS train_info (arrive_day_str TEXT, station_name TEXT, train_class_name TEXT, is_start TEXT, service_type TEXT, end_station_name TEXT, arrive_time TEXT, start_station_name TEXT, station_train_code TEXT, arrive_day_diff TEXT, start_time TEXT, station_no TEXT)')
    conn.commit()
    conn.close()
    multiprocessing.set_start_method("spawn")
    for char in RAIL_CHARS:
        tasks = []
        for i in range(1, 10000):
            # main(char, i)
            # print(f"{char}{i}")
            tasks.append(multiprocessing.Process(target=main, args=(char, i)))
    for task in tasks:
        task.start()
    for task in tasks:
        task.join()
