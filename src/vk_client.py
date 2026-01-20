"""
Клиент для взаимодействия с VK API.
Использует пользовательский токен для реального поиска.
"""

import vk_api
from typing import List, Dict, Any


class VKClient:
    def __init__(self, user_token: str):
        self.api = vk_api.VkApi(token=user_token).get_api()

    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Получает данные пользователя: дата рождения, город, пол."""
        response = self.api.users.get(
            user_ids=user_id,
            fields="city,bdate,sex"
        )
        return response[0] if response else {}

    def search_users(self, age_from: int, age_to: int, sex: int, city_id: int, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Реальный поиск пользователей через VK API.
        """
        try:
            response = self.api.users.search(
                sort=0,
                count=50,
                offset=offset,
                age_from=age_from,
                age_to=age_to,
                sex=sex,
                city=city_id,
                has_photo=1,
                status=6,          # в активном поиске
                is_closed=False     # открытый профиль
            )
            return response.get("items", [])
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []

    def get_top_photos(self, owner_id: int, count: int = 3) -> List[str]:
        """Получает топ-N фото профиля по лайкам."""
        try:
            photos_response = self.api.photos.get(
                owner_id=owner_id,
                album_id="profile",
                extended=1
            )
            photos = photos_response.get("items", [])
            sorted_photos = sorted(
                photos,
                key=lambda x: x.get("likes", {}).get("count", 0),
                reverse=True
            )
            return [
                f"photo{photo['owner_id']}_{photo['id']}"
                for photo in sorted_photos[:count]
            ]
        except Exception as e:
            print(f"Ошибка получения фото {owner_id}: {e}")
            return []