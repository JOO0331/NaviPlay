from django.db import models

#기본키, 인덱스 필드 설정 부분 피드백

#게임 정보
class Game(models.Model):
    app_id = models.IntegerField(unique=True, primary_key=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    short_description = models.TextField()
    header_image = models.URLField()
    capsule_image = models.URLField()
    release_date = models.DateField(null=True)
    quarter = models.CharField(max_length=10, null=True, default=None)
    coming_soon = models.BooleanField(default=False)
    developers = models.CharField(max_length=500)
    publishers = models.CharField(max_length=500)
    tags = models.JSONField(default=list)
    positive_reviews = models.IntegerField(default=0)
    negative_reviews = models.IntegerField(default=0)
    supported_languages = models.TextField()
    pc_requirements = models.JSONField(default=list)
    initial_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percent = models.IntegerField(default=0)
    categories = models.JSONField(default=list)
    genres = models.JSONField(default=list)
    screenshots = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recommendations = models.JSONField(default=list)

    # class Meta:
    #     indexes = [
    #         models.Index(fields=['app_id', 'name']),
    #         models.Index(fields=['created_at']),
    #         models.Index(fields=['updated_at']),
    #         models.Index(fields=['release_date']),  # 출시일 정렬
    #         models.Index(fields=['final_price']),  # 가격 정렬 및 범위 필터링
    #         models.Index(fields=['discount_percent']),  # 할인율 정렬
    #     ]
    class Meta:
        db_table = 'steam_game_game'

    # db.game.createIndex({"categories": 1})  # 멀티플레이 여부 필터
    # db.game.createIndex({"genres": 1})  # 장르 필터
    # db.game.createIndex({"tags": 1})  # 태그 필터

    def __str__(self):
        return self.name

    # def from_db_value(self, value, expression, connection):
    #     if isinstance(value, list):  # 만약 value가 list라면
    #         return json.dumps(value)  # 이를 JSON 문자열로 변환
    #     return value  # 그렇지 않으면 원래 값을 반환

    # def from_db_value(self, value, expression, connection):
    #     if isinstance(value, list):  # 만약 value가 list라면
    #         return value  # JSON 문자열로 변환하지 않고 list 그대로 반환
    #     return value  # 그렇지 않으면 원래 값을 반환

#게임 리뷰
# class GameReview(models.Model):
#     game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
#     review_id = models.CharField(max_length=100, db_index=True, unique=True)
#     review_text = models.TextField()
#     updated_at = models.DateTimeField(db_index=True)
#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['game', 'review_id']),
#             models.Index(fields=['game', 'created_at']),
#             models.Index(fields=['game', 'updated_at']),
#         ]

#     def __str__(self):
#         return f"Review {self.review_id} for {self.game.name}"
# #
# #리뷰 감성분석 내용
# class ReviewAnalysis(models.Model):
#     game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='review_analysis')
#     period_analysis = models.JSONField(default=list)
#     all_analysis = models.JSONField(default=list)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     # class Meta:
#     #     indexes = [
#     #         models.Index(fields=['created_at']),
#     #         models.Index(fields=['updated_at']),
#     #     ]
#
#     def __str__(self):
#         return f"Analysis for {self.game.name}"
#
# #유튜브 리뷰영상 요약 내용
class Youtube(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='youtube')  # 앱아이디
    video_id = models.CharField(max_length=100, default=None)  # 중복 방지
    thumbnails = models.URLField()
    title = models.CharField(max_length=200, db_index=True)
    channelImage = models.URLField(default='https://example.com/default-image.jpg')
    channelName = models.CharField(max_length=100, db_index=True)
    publishedAt = models.DateTimeField(db_index=True)
    viewCount = models.BigIntegerField(default=0)
    summary = models.TextField()
#
#     # class Meta:
#     #     indexes = [
#     #         models.Index(fields=['game']),  # 특정 게임의 유튜브 정보 조회
#     #         models.Index(fields=['publishedAt']),  # 게시일 정렬
#     #         models.Index(fields=['viewCount']),  # 조회수 정렬
#     #     ]
#
    def __str__(self):
        return f"{self.title} ({self.channelName})"

