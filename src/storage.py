"""
Модуль для работы с файлом favorites.json.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

FAVORITES_FILE = "favorites.json"


def load_favorites() -> List[Dict[str, Any]]:
    """Загружает список избранных пользователей из файла."""
    if not os.path.exists(FAVORITES_FILE):
        save_favorites([])  # создаём пустой файл, если его нет
        return []

    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Ошибка при чтении {FAVORITES_FILE}: {e}")
        return []


def save_favorites(data: List[Dict[str, Any]]) -> None:
    """Сохраняет список избранных пользователей в файл."""
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Ошибка при записи в {FAVORITES_FILE}: {e}")


def add_to_favorites(user_data: Dict[str, Any]) -> None:
    """
    Добавляет пользователя в избранное.

    Ожидается, что user_data содержит:
    - vk_id (int)
    - first_name (str)
    - last_name (str)
    - profile_url (str)
    - photos (list[str])
    """
    favorites = load_favorites()

    # Проверяем, не добавлен ли уже этот пользователь
    if any(user["vk_id"] == user_data["vk_id"] for user in favorites):
        return  # уже есть — не дублируем

    user_data["saved_at"] = datetime.now().isoformat()
    favorites.append(user_data)
    save_favorites(favorites)


def get_favorites() -> List[Dict[str, Any]]:
    """Возвращает список избранных пользователей."""
    return load_favorites()