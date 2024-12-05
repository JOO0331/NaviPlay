import os
import django
from pymongo import MongoClient
from datetime import datetime
from decimal import Decimal
from bson import Decimal128
import json

# Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "steam.settings")  # 프로젝트명 설정
django.setup()

from functions.models import Game  # Game 모델 import

# MongoDB 연결
client = MongoClient('127.0.0.1', 27017)
db = client['steam_test']  # 데이터베이스 이름
collection = db['functions_game']  # 컬렉션 이름

def get_json_value(value):
    """
    MongoDB에서 가져온 값을 Django JSONField에 맞게 변환.
    JSON 문자열이 아닌 경우 그대로 반환.
    """
    if isinstance(value, (list, dict)):  # 리스트나 딕셔너리인 경우 그대로 반환
        return value
    try:
        return json.loads(value)  # JSON 문자열인 경우 파싱
    except (TypeError, ValueError):
        return []  # 기본값으로 빈 리스트 반환

def get_decimal_value(value, default=None):
    """
    MongoDB의 Decimal128 값을 Python의 Decimal로 변환.
    잘못된 값이나 None인 경우 기본값 반환.
    """
    if value is None:
        return default
    try:
        if isinstance(value, Decimal128):
            return Decimal(str(value.to_decimal()))  # Decimal128 -> Decimal
        return Decimal(str(value))  # 일반 숫자형이나 문자열
    except (TypeError, ValueError):
        return default

def parse_date(date_string):
    """
    날짜 문자열을 YYYY-MM-DD 형식으로 변환.
    MongoDB의 'release_date' 필드에서 다양한 형식을 처리.
    """
    if not date_string:
        return None  # 날짜가 없는 경우 None 반환

    try:
        # 형식: "2013년 7월 9일"
        return datetime.strptime(date_string, "%Y년 %m월 %d일").date()
    except ValueError:
        pass

    try:
        # 형식: "2013-07-09"
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        pass

    # 기타 형식이 있는 경우 처리 추가 가능
    return None  # 변환 실패 시 None 반환

# 데이터 변환 및 Django ORM 삽입
for document in collection.find():
    release_date = parse_date(document.get('release_date', ''))

    # MongoDB에서 데이터를 가져와 Django 모델에 저장
    Game.objects.create(
        app_id=document['app_id'],
        name=document['name'],
        short_description=document.get('short_description', ''),
        capsule_image=document.get('capsule_image', ''),
        header_image=document.get('header_image', ''),
        release_date=release_date,
        quarter=document.get('quarter', ''),
        coming_soon=document.get('coming_soon', False),
        developers=document.get('developers', []),
        publishers=document.get('publishers', []),
        tags=get_json_value(document.get('tags', [])),
        supported_languages=document.get('supported_languages', ''),
        pc_requirements=get_json_value(document.get('pc_requirements', [])),
        discount_percent=document.get('discount_percent', 0),
        initial_price=get_decimal_value(document.get('initial_price'), None),
        final_price=get_decimal_value(document.get('final_price'), None),
        categories=get_json_value(document.get('categories', [])),
        genres=get_json_value(document.get('genres', [])),
        screenshots=get_json_value(document.get('screenshots', []))
    )
    print(f"Inserted: {document['app_id']} - {document['name']}")

print("Data migration completed.")
