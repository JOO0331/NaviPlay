from django.db import models
import json

class MongoSafeJSONField(models.JSONField):
    """MongoDB용 안전한 JSONField"""

    def from_db_value(self, value, expression, connection):
        # 이미 리스트나 딕셔너리면 그대로 반환
        if isinstance(value, (list, dict)):
            return value
        # 문자열이라면 JSON 파싱
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
