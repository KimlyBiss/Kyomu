import json
import random
from pathlib import Path
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class InventoryManager:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
        self.items = self._load_items()
        self.inventories = self._load_inventories()
        logger.info(f"🌀 Загружено {len(self.items)} предметов")
        logger.info(f"🎒 Загружено {len(self.inventories)} инвентарей")

    def _load_items(self) -> dict:
        """Загрузка предметов из файла items_library.json"""
        try:
            items_path = self.data_path / "items_library.json"
            
            # Создать файл, если не существует
            if not items_path.exists():
                logger.warning("Создан пустой файл items_library.json")
                with open(items_path, "w", encoding="utf-8") as f:
                    json.dump({"items": {}}, f)
                return {}

            with open(items_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("items", {})

        except json.JSONDecodeError:
            logger.error("Ошибка формата items_library.json!")
            return {}
        except Exception as e:
            logger.error(f"Ошибка загрузки предметов: {str(e)}")
            return {}

    def _load_inventories(self) -> dict:
        """Загрузка инвентарей игроков из файла inventories.json"""
        try:
            inv_path = self.data_path / "inventories.json"
            
            # Создать файл, если не существует
            if not inv_path.exists():
                logger.warning("Создан пустой файл inventories.json")
                with open(inv_path, "w", encoding="utf-8") as f:
                    json.dump({}, f)
                return {}

            with open(inv_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except json.JSONDecodeError:
            logger.error("Ошибка формата inventories.json!")
            return {}
        except Exception as e:
            logger.error(f"Ошибка загрузки инвентарей: {str(e)}")
            return {}

    def save_inventories(self):
        """Сохранение всех инвентарей в файл"""
        try:
            with open(self.data_path / "inventories.json", "w", encoding="utf-8") as f:
                json.dump(self.inventories, f, indent=4, ensure_ascii=False)
            logger.debug("💾 Инвентари успешно сохранены")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {str(e)}")

    def get_user_inventory(self, user_id: str) -> dict:
        """Получение инвентаря пользователя с валидацией"""
        user_inv = self.inventories.get(user_id, {})
        
        # Фильтрация несуществующих предметов
        valid_items = {
            item_id: count 
            for item_id, count in user_inv.items() 
            if item_id in self.items
        }
        
        # Обновить инвентарь при изменении
        if len(valid_items) != len(user_inv):
            self.inventories[user_id] = valid_items
            self.save_inventories()
            
        return valid_items

    def get_item_info(self, item_id: str) -> dict:
        """Получение информации о предмете по ID"""
        return self.items.get(item_id, {
            "name": "❌ Неизвестный предмет",
            "description": "Этот артефакт потерян в тумане времени...",
            "rarity": "unknown"
        })

    def give_random_item(self, user_id: str) -> dict:
        """Выдача случайного предмета игроку"""
        try:
            # Вероятности редкостей
            rarities = {
                "common": 0.5,
                "uncommon": 0.3,
                "rare": 0.15,
                "legendary": 0.05
            }
            
            # Выбор редкости
            chosen_rarity = random.choices(
                list(rarities.keys()),
                weights=list(rarities.values()),
                k=1
            )[0]
            
            # Фильтрация предметов по редкости
            available = [
                item_id 
                for item_id, data in self.items.items() 
                if data.get("rarity") == chosen_rarity
            ]
            
            if not available:
                logger.warning(f"Нет предметов редкости {chosen_rarity}!")
                return None
                
            # Выдача предмета
            item_id = random.choice(available)
            self.inventories.setdefault(user_id, {})[item_id] = \
                self.inventories[user_id].get(item_id, 0) + 1
            self.save_inventories()
            
            logger.info(f"🎁 {user_id} получил {item_id}")
            return self.items[item_id]
            
        except Exception as e:
            logger.error(f"💥 Ошибка выдачи предмета: {str(e)}")
            return None

    def get_items_for_choices(self) -> list:
        """Генерация списка для выбора предметов (автодополнение)"""
        return [
            app_commands.Choice(
                name=f"{item['name']} ({item['rarity']})", 
                value=item_id
            )
            for item_id, item in self.items.items()
        ][:25]  # Ограничение Discord на 25 элементов