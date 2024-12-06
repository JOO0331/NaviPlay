import html
from datetime import datetime

# 제목에서 HTML 엔티티 제거
def clean_title(title):
    return html.unescape(title)

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steam.settings')  # 프로젝트 이름을 입력하세요.
django.setup()

from functions.models import Game, Youtube
games = Game.objects.filter(app_id=1172470) #일단 하나만 가져와서 해봄..

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# API 키 객체 생성
DEVELOPER_KEY = ""
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# build(googleapiclient.discovery) 객체 생성
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
# =========================================================================================
import re
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

def get_youtube_transcript(video_id):
    # 한국어 자막을 요청
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
    return transcript

def summarize_with_genai(text):
    api_key = ""
    genai.configure(api_key=api_key)

    prompt= f"다음 내용은 게임리뷰에 관한 영상의 자막이야. 이 내용을 요약해서 게임 구매를 고민하는 사람에게 적절한 정보를 5줄~7줄로 내용을 정리해줘.: {text}"
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    return response.text  # 요약된 텍스트 반환

for g in games:
    # 비디오 검색
    search_response = youtube.search().list(
        q=g.name+" 리뷰",
        order="relevance",
        part="snippet",
        type="video",
        videoDuration="medium",
        maxResults=2
    ).execute()

    for i in range(2):
        game = g
        search_result = search_response.get("items", [])[i]
        video_id = search_result["id"]["videoId"] #video_url = f"https://www.youtube.com/watch?v={video_id}"
        title = search_result["snippet"]["title"]
        thumbnails = search_result["snippet"]["thumbnails"]['high']['url']
        publishedAt = search_result["snippet"]["publishedAt"]
        channelName = search_result["snippet"]["channelTitle"]

        channel_id = search_result["snippet"]["channelId"]
        channel_response = youtube.channels().list(
            part="snippet",
            id=channel_id
        ).execute()
        channel_snippet = channel_response["items"][0]["snippet"]
        channelImage = channel_snippet["thumbnails"]["high"]["url"]

        video_response = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()
        video_statistics = video_response["items"][0]["statistics"]
        viewCount = video_statistics.get("viewCount", "조회수 없음")
        #===========================================================
        # 자막 가져오기
        transcript = get_youtube_transcript(video_id)

        # 자막을 텍스트로 변환
        full_text = ' '.join([entry['text'] for entry in transcript])

        # genai를 사용하여 자막 요약
        summary = summarize_with_genai(full_text)

        new_Youtube = Youtube.objects.create(
            game=game, #인스턴스
            video_id = video_id,
            thumbnails=thumbnails,
            title = clean_title(title),
            channelImage=channelImage,
            channelName = channelName,
            publishedAt=publishedAt,
            viewCount = viewCount,
            summary = summary
        )

