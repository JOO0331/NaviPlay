from django.shortcuts import render
from .models import Game, Youtube, ReviewAnalysis
import re
import json
import random
from datetime import datetime

from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def preprocess_pc_requirements(pc_requirements_html):
    if isinstance(pc_requirements_html, (list, dict)):
        pc_requirements_html = str(pc_requirements_html)
    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(pc_requirements_html, 'html.parser')
    # <ul> 내의 <li> 항목을 추출하여 리스트로 반환
    requirements = [li.get_text(strip=True) for li in soup.find_all('li')]
    return requirements

def main_view(request):
    # URL 파라미터에서 카테고리를 가져옴. 기본값은 'popular'
    category = request.GET.get('category', 'popular')

    # 필터링 조건 설정
    if category == 'popular':
        games = Game.objects.all().order_by('-positive_reviews')[:100]
    elif category == 'free':
        games = Game.objects.filter(final_price=0)[:100]
    elif category == 'discounted':
        games = Game.objects.filter(discount_percent__gt=0)[:100]
    elif category == 'single':
        games = Game.objects.filter(categories__icontains={'description': '싱글 플레이어'})[:100]
    elif category == 'multi':
        games = Game.objects.filter(categories__icontains={'description': '멀티플레이어'})[:100]
    else:
        games = Game.objects.all()[:100]

    # 가격 정수 변환
    for game in games:
        game.final_price_int = int(float(game.final_price)) if game.final_price else 0
        game.initial_price_int = int(float(game.initial_price)) if game.initial_price else 0

    return render(request, "main.html", {'games': games})

def search_view(request):
    review_analysis = ReviewAnalysis.objects.first()
    period_analysis = review_analysis.period_analysis
    all_analysis = review_analysis.all_analysis

    total_positive = all_analysis[0]['positive']
    total_negative = all_analysis[0]['negative']
    total_reviews = total_positive + total_negative

    if total_reviews > 10:
        positive_ratio = int(total_positive / total_reviews * 100)
    else:
        positive_ratio = 0


    query = request.GET.get('search', '')

    sort_order = request.GET.get('sort', '')
    number_of_players = request.GET.get('players', '')
    price_range = request.GET.get('price', '')
    release_status = request.GET.get('status', None)

    games = Game.objects.all()

    if query:
        games = games.filter(name__icontains=query)

    sort_mappings = {
        'price_desc': '-final_price',
        'price_asc': 'final_price',
        'discount_desc': '-discount_percent',
        'discount_asc': 'discount_percent',
    }
    if sort_order in sort_mappings:
        games = games.order_by(sort_mappings[sort_order])

    player_category_mappings = {
        'single_player': 2,
        'multi_player': 1,
        'online_coop': 38,
    }
    if number_of_players in player_category_mappings:
        category_id = player_category_mappings[number_of_players]
        games = [game for game in games if any(category['id'] == category_id for category in game.categories)]

    price_ranges = {
        '_3': (None, 30000),
        '3_5': (30000, 50000),
        '5_7': (50000, 70000),
        '7_10': (70000, 100000),
        '10_': (100000, None),
    }
    if price_range in price_ranges:
        min_price, max_price = price_ranges[price_range]
        games = [
            game for game in games
            if (min_price is None or int(float(str(game.final_price))) >= min_price) and
               (max_price is None or int(float(str(game.final_price))) < max_price)
        ]

    if release_status == 'released':
        games = [game for game in games if not game.coming_soon]
    elif release_status == 'upcoming':
        games = [game for game in games if game.coming_soon]

    for game in games:
        game.final_price_int = int(float(str(game.final_price)))
        game.initial_price_int = int(float(str(game.initial_price)))

    page = request.GET.get('page', 1)
    paginator = Paginator(games, 20)  # 1페이지당 20개씩

    try:
        paginated_games = paginator.page(page)
    except PageNotAnInteger:
        paginated_games = paginator.page(1)
    except EmptyPage:
        paginated_games = paginator.page(paginator.num_pages)

    # 페이지 그룹: 10개 단위로 나누기
    current_page = paginated_games.number
    total_pages = paginator.num_pages
    page_group = (current_page - 1) // 10 + 1
    start_page = (page_group - 1) * 10 + 1
    end_page = min(start_page + 9, total_pages)

    # 쿼리 파라미터 유지
    context = {
        'games': paginated_games,
        'positive_ratio': positive_ratio,
        'search_query': query,
        'sort_order': sort_order,
        'release_status': release_status,
        'number_of_players': number_of_players,
        'price_range': price_range,
        'total_pages': total_pages,
        'start_page': start_page,
        'end_page': end_page,
        'current_page': current_page,
    }

    return render(request, "search.html", context)

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

def tags_view(request):
    # URL 파라미터에서 tag_name을 가져옵니다. 기본값은 'Indie'
    tag_name = request.GET.get('tag', 'Indie')

    # Game 모델에서 해당 태그를 포함하는 게임 필터링
    games = Game.objects.filter(tags__icontains=tag_name).order_by('name')

    # Paginator로 페이지네이션 (9개씩)
    paginator = Paginator(games, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 태그 리스트
    tags = [
        "Indie", "Action", "Adventure", "Singleplayer", "Casual", "Simulation", "Strategy",
        "RPG", "Multiplayer", "Great Soundtrack", "Atmospheric", "2D",
        "Puzzle", "Early Access", "Open World", "Story Rich", "Co-op",
        "Difficult", "Shooter", "Sci-fi"
    ]

    # 템플릿에 전달할 컨텍스트
    context = {
        'tags': tags,
        'selected_tag': tag_name,
        'page_obj': page_obj,
    }

    return render(request, 'tags.html', context)