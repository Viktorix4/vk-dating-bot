# src/vk_client.py
import vk_api
from typing import List, Dict, Any


class VKClient:
    def __init__(self, token: str):
        self.api = vk_api.VkApi(token=token).get_api()

    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        return self.api.users.get(user_ids=user_id, fields="city,bdate,sex")[0]

    def search_users(self, age_from: int, age_to: int, sex: int, city_id: int) -> List[Dict[str, Any]]:
        resp = self.api.users.search(
            age_from=age_from,
            age_to=age_to,
            sex=sex,
            city=city_id,
            has_photo=1,
            count=50
        )
        return resp.get("items", [])

    def get_top_photos(self, owner_id: int, count: int = 3) -> List[str]:
        try:
            photos = self.api.photos.get(owner_id=owner_id, album_id="profile", extended=1)
            sorted_photos = sorted(
                photos["items"],
                key=lambda x: x.get("likes", {}).get("count", 0),
                reverse=True
            )
            return [f"photo{p['owner_id']}_{p['id']}" for p in sorted_photos[:count]]
        except Exception:
            return []