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
collection = db['functions_youtube']  # 컬렉션 이름

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


# 데이터 변환 및 Django ORM 삽입
for document in collection.find():

    # MongoDB에서 데이터를 가져와 Django 모델에 저장
    Game.objects.create(
        game=document['game'],
        video_id=document['video_id'],
        thumbnails=document.get('thumbnails', ''),
        title=document.get('title', ''),
        channelImage=document.get('channelImage', ''),
        channelName=document.get('channelName',''),
        publishedAt=document.get('publishedAt', ''),
        viewCount=document.get('viewCount', ''),
        summary = data.get('developers', []),
    )
    print(f"Inserted: {document['game']} - {document['video_id']}")

print("Data migration completed.")


game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='youtube')  # 앱아이디
    video_id = models.CharField(max_length=100, default=None)  # 중복 방지
    thumbnails = models.URLField()
    title = models.CharField(max_length=200, db_index=True)
    channelImage = models.URLField(default='https://example.com/default-image.jpg')
    channelName = models.CharField(max_length=100, db_index=True)
    publishedAt = models.DateTimeField(db_index=True)
    viewCount = models.BigIntegerField(default=0)
    summary = models.TextField()
