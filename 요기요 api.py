import os
import json
from bs4 import ResultSet
import requests
import argparse
import warnings
warnings.filterwarnings("ignore")

FILE_PATH = "dist/restaurant_data.json"


YOGIYO = "https://www.yogiyo.co.kr"

AJOU_LAT = 37.2831587400464
AJOU_LON = 127.045818871424


def parse_menu(item):
    #print(json.dumps(item,indent=4, ensure_ascii=False))
    key_list = ['original_image', 'image', 'description', 'price', 'name']
    rest_menu = {}
    for key in key_list:
        if key in item:
            rest_menu[key] = item[key]
        else:
            rest_menu[key] = "No Image"
    return rest_menu


def parse_rest_info(item):
    key_list = ['id', 'name', 'review_avg', 'begin', 'end', 'min_order_amount', 'estimated_delivery_time',
                'adjusted_delivery_fee', 'phone', 'address', 'logo_url', 'categories']
    rest_info = {}
    for key in key_list:
        rest_info[key] = item[key]  # TODO: 이동만 하고 있음 구지 않해도 될수도 filter 이용
    return rest_info


def get_restaurant_list(lat, lng, n=70):
    # 헤더 선언 및 referer, User-Agent 전송
    headers = {
        "referer": YOGIYO+"/mobile/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Accept": "application/json",
        "x-apikey": "iphoneap",
        "x-apisecret": "fe5183cc3dea12bd0ce299cf110a75a2",
    }
    params = {
        "items": n,
        "lat": lat,
        "lng": lng,
        "order": "rank",
        "page": 0,
        "search": "",
    }

    url = YOGIYO + "/api/v1/restaurants-geo/?catagory="
    response_restaurant = requests.get(url, headers=headers, params=params)

    rest_list = []
    for i, restaurant in enumerate(response_restaurant.json()["restaurants"]):
        print(i)
        path = f"/api/v1/restaurants/{restaurant['id']}//menu/"
        option = "?add_photo_menu=android"\
            + "&add_one_dish_menu=true"\
            + "&order_serving_type=delivery"
        url = YOGIYO + path + option
        response_menu = requests.get(url, headers=headers, params=params)

        # TODO: 현재 rest_list 가 json형식에 맞지 않는다.
        rest = {}
        rest["info"] = parse_rest_info(restaurant)

        menu_list = []
        for menu in response_menu.json()[0]["items"]:
            menu_list.append(parse_menu(menu))
        rest["menu"] = menu_list

        rest_list.append(rest)
    return {"restaurant": rest_list}


def save(rest_list):
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, 'w', encoding='UTF-8') as outfile:
        json.dump(rest_list, outfile, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Arguments for Crawler")
    parser.add_argument(
        "--order",
        required=False,
        default="rank",
        help="option for restaurant list order / choose one \
        -> [rank, review_avg, review_count, min_order_value, distance, estimated_delivery_time]",
    )
    parser.add_argument("--num", required=False, default=10,
                        help="option for restaurant number")
    parser.add_argument("--lat", required=False,
                        default=AJOU_LAT, help="latitude for search")
    parser.add_argument("--lon", required=False,
                        default=AJOU_LON, help="longitude for search")
    args = parser.parse_args()

    ORDER_OPTION = args.order
    RESTAURANT_COUNT = int(args.num)
    LAT = float(args.lat)
    LON = float(args.lon)
    location = [LAT, LON]

    print("시작")
    save(get_restaurant_list(location[0], location[1], RESTAURANT_COUNT))
    print("끝")
