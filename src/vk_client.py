"""
Клиент для взаимодействия с VK API.
"""

import vk_api
from vk_api.exceptions import ApiError
from typing import List, Dict, Any, Optional


class VKClient:
    def __init__(self, token: str):
        self.vk = vk_api.VkApi(token=token)
        self.api = self.vk.get_api()

    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию о пользователе по ID."""
        try:
            response = self.api.users.get(
                user_ids=user_id,
                fields="city, bdate, sex"
            )
            return response[0] if response else None
        except ApiError as e:
            print(f"Ошибка при получении данных пользователя {user_id}: {e}")
            return None

    def search_users(self, age_from: int, age_to: int, sex: int, city_id: int, offset: int = 0) -> List[Dict[str, Any]]:
        """Ищет пользователей по критериям."""
        try:
            response = self.api.users.search(
                sort=0,  # сортировка по популярности
                count=50,
                offset=offset,
                age_from=age_from,
                age_to=age_to,
                sex=sex,
                city=city_id,
                has_photo=1,
                status=6,  # в активном поиске
                is_closed=False
            )
            return response.get("items", [])
        except ApiError as e:
            print(f"Ошибка при поиске пользователей: {e}")
            return []

    def get_top_photos(self, owner_id: int, count: int = 3) -> List[str]:
        """Получает топ-N фотографий по количеству лайков."""
        try:
            photos = self.api.photos.get(
                owner_id=owner_id,
                album_id="profile",
                extended=1  # чтобы получить лайки
            )
            # Сортируем по количеству лайков
            sorted_photos = sorted(
                photos["items"],
                key=lambda x: x.get("likes", {}).get("count", 0),
                reverse=True
            )
            # Формат attachment: photo{owner_id}_{media_id}
            return [
                f"photo{photo['owner_id']}_{photo['id']}"
                for photo in sorted_photos[:count]
            ]
        except ApiError as e:
            print(f"Ошибка при получении фото пользователя {owner_id}: {e}")
            return []