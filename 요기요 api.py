
import json
import requests
import argparse
import warnings
warnings.filterwarnings("ignore")

FILE_PATH = "D:/jingi/datajson.txt"
# FILE_PATH = "D:/joey_workspace/2022/아주대/1학기/소프트웨어공학/팀프로젝트/코드/datajson.json"


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
    response = requests.get(url, headers=headers, params=params)

    rest_list = ["restaurant :"]  # 최종 결과 저장
    for i, restaurant in enumerate(response.json()["restaurants"]):
        print(i)
        path = f"/api/v1/restaurants/{restaurant['id']}//menu/"
        option = "?add_photo_menu=android"\
            + "&add_one_dish_menu=true"\
            + "&order_serving_type=delivery"
        url = YOGIYO + path + option
        response_menu = requests.get(url, headers=headers, params=params)

        rest = ["info :"]
        rest.append(parse_rest_info(restaurant))

        rest.append("menu :")
        for menu in response_menu.json()[0]["items"]:
            rest.append(parse_menu(menu))

        rest_list.append(rest)
    return rest_list


def save(rest_list):
    # TODO: 현재 rest_list 가 json형식에 맞지 않는다.
    file_path = FILE_PATH
    with open(file_path, 'w', encoding='UTF-8') as outfile:
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

    print("시작")
    save(get_restaurant_list(location[0], location[1], RESTAURANT_COUNT))
    print("끝")
