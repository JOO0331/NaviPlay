from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os
import django
from django.db import transaction
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steam.settings')
django.setup()
from functions.models import Game

BATCH_SIZE = 100

def similar_games():
    total_game_count = Game.objects.count()
    
    all_games = Game.objects.all().only('app_id', 'tags')
    all_game_tags = []
    for game in all_games:
        cleaned_tags = [tag.strip() for tag in game.tags]
        all_game_tags.append(' '.join(cleaned_tags))
    
    vectorizer = CountVectorizer()
    all_tag_matrix = vectorizer.fit_transform(all_game_tags)
    
    for start in range(0, total_game_count, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total_game_count)
        batch_games = list(all_games[start:end])
        
        batch_cosine_sim = cosine_similarity(
            all_tag_matrix[start:end], 
            all_tag_matrix
        )
        
        with transaction.atomic():
            for i, game in enumerate(batch_games):
                sim_scores = list(enumerate(batch_cosine_sim[i]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                
                sim_scores = [score for score in sim_scores if all_games[score[0]].app_id != game.app_id][:10]
                
                recommendations = []
                for score in sim_scores:
                    similar_game = all_games[score[0]]
                    recommendations.append({
                        'app_id': similar_game.app_id
                    })
                
                Game.objects.filter(app_id=game.app_id).update(recommendations=recommendations)

similar_games()