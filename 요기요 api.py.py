import re
import time
import pickle
import argparse
import warnings
warnings.filterwarnings("ignore")

import requests
from urllib.request import urlopen, Request
from fake_useragent import UserAgent
import json

def restaurant(item,item2):
    key_list = ['id', 'name', 'review_avg','begin','end','lat','lng','min_order_amount','estimated_delivery_time',
                'adjusted_delivery_fee','phone','address','logo_url','categories']
    rest_menu = {}
    for key in key_list:
        rest_menu[key]=item[key]
    item2.insert(1,rest_menu)
    return item2
def menu(item):
    #print(json.dumps(item,indent=4, ensure_ascii=False))
    key_list = ['original_image','image','description','price','name']
    rest_menu = {}
    for key in key_list:
        try:
            rest_menu[key]=item[key]
        except:
            rest_menu[key]= "No Image"
    return rest_menu

def get_restaurant_list(lat, lng,item=70):


    result_list = [] #최종 결과 저장
    result_list.append("restaurant :")
    # 헤더 선언 및 referer, User-Agent 전송
    headers = {
        "referer": "https://www.yogiyo.co.kr/mobile/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Accept": "application/json",
        "x-apikey": "iphoneap",
        "x-apisecret": "fe5183cc3dea12bd0ce299cf110a75a2",
    }
    params = {
        "items": item,
        "lat": 37.2831587400464,
        "lng": 127.045818871424,
        "order": "rank",
        "page": 0,
        "search":"", 
    }
    host = "https://www.yogiyo.co.kr"
    path = "/api/v1/restaurants-geo/?catagory="
    url = host + path
    response = requests.get(url, headers=headers, params=params)
    i=0
    for item in response.json()["restaurants"]:
        print(i)
        i+=1
        temp_list = ["info :"]
        temp_list.append("menu :")
        restaurant_id = item["id"]
        time.sleep(1)
        response_menu = requests.get(f"https://www.yogiyo.co.kr/api/v1/restaurants/{restaurant_id}//menu/?add_photo_menu=android&add_one_dish_menu=true&order_serving_type=delivery",headers=headers, params=params)
        for item_menu in response_menu.json()[0]["items"]:
            temp_list.append(menu(item_menu))
        result_list.append(restaurant(item,temp_list))
    file_path = "D:/jingi/진기/소프트웨어 공학/DeleTO_data/restaurant_data.txt"
    with open(file_path, 'w',encoding='UTF-8') as outfile:
        json.dump(result_list, outfile, indent=4, ensure_ascii=False)
    return

parser = argparse.ArgumentParser(description="Arguments for Crawler")
parser.add_argument(
    "--order",
    required=False,
    default="rank",
    help="option for restaurant list order / choose one \
    -> [rank, review_avg, review_count, min_order_value, distance, estimated_delivery_time]",
)
parser.add_argument("--num", required=False, default=100, help="option for restaurant number")
parser.add_argument("--lat", required=False, default=37.2831587400464, help="latitude for search")
parser.add_argument("--lon", required=False, default=127.045818871424, help="longitude for search")
args = parser.parse_args()

ORDER_OPTION = args.order
RESTAURANT_COUNT = int(args.num)
LAT = float(args.lat)
LON = float(args.lon)
location = [LAT, LON]

print("시작")
get_restaurant_list(location[0], location[1],RESTAURANT_COUNT)
print("끝")
