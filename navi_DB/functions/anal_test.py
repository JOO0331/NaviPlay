import sys
import os
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steam.settings')
django.setup()
from functions.models import Game, Youtube, ReviewAnalysis

try:
    review_analysis = ReviewAnalysis.objects.first()
    period_analysis = review_analysis.period_analysis
    all_analysis = review_analysis.all_analysis
    
    total_positive = all_analysis[0]['positive']
    total_negative = all_analysis[0]['negative']
    positive_keywords = all_analysis[0]['positive_keywords']
    negative_keywords = all_analysis[0]['negative_keywords']
except:
    period_analysis = []
    all_analysis = []
    total_positive = 0
    total_negative = 0
    positive_keywords = []
    negative_keywords = []

print(positive_keywords)
