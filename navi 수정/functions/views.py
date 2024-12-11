from django.shortcuts import render
from .models import Game, Youtube, ReviewAnalysis
import re
import json
import random
from datetime import datetime

from bs4 import BeautifulSoup

def preprocess_pc_requirements(pc_requirements_html):
    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(pc_requirements_html, 'html.parser')
    # <ul> 내의 <li> 항목을 추출하여 리스트로 반환
    requirements = [li.get_text(strip=True) for li in soup.find_all('li')]
    return requirements

def main_view(request):
    games = Game.objects.all()
    for game in games:
        game.final_price_int = int(float(str(game.final_price)))
        game.initial_price_int = int(float(str(game.initial_price)))
    return render(request, "main.html", {'games': games})

def search_view(request):
    query = request.GET.get('search', '')
    games = Game.objects.all()

    if query:
        games = games.filter(name__icontains=query)

    for game in games:
        game.final_price_int = int(float(str(game.final_price)))
        game.initial_price_int = int(float(str(game.initial_price)))
    #     total_reviews = game.positive_reviews + game.negative_reviews
    #     if total_reviews > 110:
    #         positive_ratio = int(game.positive_reviews / total_reviews * 100)
    #     else:
    #         positive_ratio = negative_ratio = 0  # 리뷰 부족하면 0->?
    
    return render(request, "search.html", {'games': games})

def dashboard_view(request, app_id):
    game = Game.objects.get(app_id=app_id)
    game.final_price_int = int(float(str(game.final_price)))
    game.initial_price_int = int(float(str(game.initial_price)))
    game.pc_requirements = preprocess_pc_requirements(game.pc_requirements)

    review_analysis = ReviewAnalysis.objects.first()
    period_analysis = review_analysis.period_analysis
    all_analysis = review_analysis.all_analysis
    
    total_positive = all_analysis[0]['positive']
    total_negative = all_analysis[0]['negative']
    
    positive_keywords = []
    negative_keywords = []
    
    for keyword_dict in all_analysis[0]['positive_keywords']:
        for keyword, count in keyword_dict.items():
            positive_keywords.append((keyword, count))
    
    for keyword_dict in all_analysis[0]['negative_keywords']:
        for keyword, count in keyword_dict.items():
            negative_keywords.append((keyword, count))
    
    positive_keywords = sorted(positive_keywords, key=lambda x: x[1], reverse=True)
    negative_keywords = sorted(negative_keywords, key=lambda x: x[1], reverse=True)
    
    
    total_reviews = total_positive + total_negative
    if total_reviews > 10:
        positive_ratio = int(total_positive / total_reviews * 100)
    else:
        positive_ratio = 0

    youtubes = Youtube.objects.filter(game=game)
    for youtube in youtubes:
        youtube.publishedAt = youtube.publishedAt.strftime("%Y년 %m월 %d일")

    if isinstance(game.tags, str):
        game.tags = [tag.strip() for tag in game.tags.split(',')]
    
    if isinstance(game.supported_languages, str):
        clean_text = re.sub('<[^<]+?>', '', game.supported_languages)
        main_languages = clean_text.split('languages with full audio support')[0]
        languages = [lang.strip() for lang in main_languages.split(',')]
        game.supported_languages = [lang.replace('*', '').strip() for lang in languages]
    
    if isinstance(game.developers, str):
        game.developers = [dev.strip() for dev in game.developers.split(',')]
    
    if isinstance(game.publishers, str):
        game.publishers = [pub.strip() for pub in game.publishers.split(',')]

    recommendations = game.recommendations
    
    first_id = recommendations[0]['app_id']
    first_game = Game.objects.get(app_id=first_id)
    first_game.final_price_int = int(float(str(first_game.final_price)))
    first_game.initial_price_int = int(float(str(first_game.initial_price)))
    
    remain_ids = [rec['app_id'] for rec in recommendations[1:]]
    random_ids = random.sample(remain_ids, 2)
    random_games = [Game.objects.get(app_id=rec_id) for rec_id in random_ids]
    for random_game in random_games:
        random_game.final_price_int = int(float(str(random_game.final_price)))
        random_game.initial_price_int = int(float(str(random_game.initial_price)))
    
    years = set()
    period_data = {}
    
    for item in period_analysis:
        date_str = item['period'].split('~')[0]
        date = datetime.strptime(date_str, '%Y-%m-%d')
        year = date.year
        month = date.month
        
        if year not in period_data:
            period_data[year] = {}
        
        years.add(year)
        period_data[year][month] = {
            'positive': item['positive'],
            'negative': item['negative'],
            'positive_keywords': item['positive_keywords'],
            'negative_keywords': item['negative_keywords']
        }
    
    current_year = datetime.now().year
    
    context = {
        'game': game,
        'first_recommendation': first_game,
        'random_recommendations': random_games,
        'youtubes': youtubes,
        'all_analysis': all_analysis,
        'positive_ratio': positive_ratio,
        'positive_keywords' : positive_keywords,
        'negative_keywords' : negative_keywords,
        'period_data': json.dumps(period_data),
        'years': sorted(list(years)),
        'current_year': current_year
    }
    
    return render(request, 'dashboard.html', context)
