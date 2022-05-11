from tqdm import tqdm  # progress bar
import os
import json
import requests
import argparse
import warnings
warnings.filterwarnings("ignore")

FILE_NAME = "dist/restaurant_data.json"

AJOU_LAT = 37.2831587400464
AJOU_LON = 127.045818871424


class YogiyoAPI:
    def __init__(self, lat, lng, n=100) -> None:
        self.host = "https://www.yogiyo.co.kr"

        self.headers = {
            "referer": self.host+"/mobile/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
            "Accept": "application/json",
            "x-apikey": "iphoneap",
            "x-apisecret": "fe5183cc3dea12bd0ce299cf110a75a2",
        }
        self.params = {
            "items": n,
            "lat": lat,
            "lng": lng,
            "order": "rank",
            "page": 0,
            "search": "",
        }

    def get_restaurant(self) -> dict:
        url = self.host + "/api/v1/restaurants-geo/?catagory="
        return requests.get(url, headers=self.headers, params=self.params).json()["restaurants"]

    def get_menu(self, rest_id) -> list:
        path = f"/api/v1/restaurants/{rest_id}//menu/"
        option = "?add_photo_menu=android"\
            + "&add_one_dish_menu=true"\
            + "&order_serving_type=delivery"
        url = self.host + path + option
        return requests.get(url, headers=self.headers, params=self.params).json()[0]["items"]


def parse_menu(item):
    # print(json.dumps(item,indent=4, ensure_ascii=False))
    key_list = ['original_image', 'image', 'description', 'price', 'name']
    rest_menu = {}
    for key in key_list:
        if key in item:
            rest_menu[key] = item[key]
        else:
            rest_menu[key] = "No Image"
    return rest_menu


def parse_rest_info(item):
    key_list = ['id', 'name', 'review_avg', 'begin', 'end', 'lat', 'lng', 'min_order_amount', 'estimated_delivery_time',
                'adjusted_delivery_fee', 'phone', 'address', 'logo_url', 'categories']
    rest_info = {}
    for key in key_list:
        rest_info[key] = item[key]
    return rest_info


def get_restaurant_list(yogiyoAPI: YogiyoAPI) -> dict:
    rest_list = []
    for restaurant in tqdm(yogiyoAPI.get_restaurant()):
        rest = {}
        rest["info"] = parse_rest_info(restaurant)
        menu_list = []
        for menu in yogiyoAPI.get_menu(restaurant['id']):
            menu_list.append(parse_menu(menu))
        rest["menu"] = menu_list
        rest_list.append(rest)
    return {"restaurant": rest_list}


def save(rest_list):
    os.makedirs(os.path.dirname(FILE_NAME), exist_ok=True)
    with open(FILE_NAME, 'w', encoding='UTF-8') as outfile:
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
    parser.add_argument("--num", required=False, default=100,
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

    yogiyoAPI = YogiyoAPI(*location, RESTAURANT_COUNT)
    save(get_restaurant_list(yogiyoAPI))
