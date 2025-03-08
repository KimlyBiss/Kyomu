import json
import random
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import discord
from discord.ext import commands
from modules.logger import logger

class DrunkManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "drunk_users.json"
        self.dict_file = self.data_dir / "drunk_dict.json"
        self.users: Dict[int, Dict] = {}
        self.char_map = {}
        self._ensure_files_exist()  # Создание файлов при инициализации
        self.load_data()

    def _ensure_files_exist(self):
        """Создает файлы данных, если они отсутствуют."""
        if not self.users_file.exists():
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
        if not self.dict_file.exists():
            # Используем предоставленный пользователем drunk_dict
            default_map = {
                "char_map": {
                    "а": ["а", "a", "@"],
                    "б": ["б", "6"],
                    "в": ["в", "v"],
                    "г": ["г", "r"],
                    "д": ["д", "d"],
                    "е": ["е", "e"],
                    "ё": ["ё", "e"],
                    "ж": ["ж", "zh"],
                    "з": ["з", "3"],
                    "и": ["и", "u"],
                    "й": ["й", "y"],
                    "к": ["к", "k"],
                    "л": ["л", "l"],
                    "м": ["м", "m"],
                    "н": ["н", "h"],
                    "о": ["о", "o", "0"],
                    "п": ["п", "n"],
                    "р": ["р", "p"],
                    "с": ["с", "c", "s"],
                    "т": ["т", "t"],
                    "у": ["у", "y"],
                    "ф": ["ф", "f"],
                    "х": ["х", "x"],
                    "ц": ["ц", "ts"],
                    "ч": ["ч", "ch"],
                    "ш": ["ш", "sh"],
                    "щ": ["щ", "shch"],
                    "ъ": ["ъ", ""],
                    "ы": ["ы", "i"],
                    "ь": ["ь", ""],
                    "э": ["э", "e"],
                    "ю": ["ю", "yu"],
                    "я": ["я", "ya"]
                }
            }
            with open(self.dict_file, "w", encoding="utf-8") as f:
                json.dump(default_map, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """Загружает данные из JSON-файлов."""
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                self.users = json.load(f) or {}
            with open(self.dict_file, "r", encoding="utf-8") as f:
                data = json.load(f) or {}
                self.char_map = data.get("char_map", {})
            logger.info("🌀 Данные опьянения загружены")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки: {e}")

    def save_data(self):
        """Сохраняет текущие данные в JSON."""
        try:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")

    def drunkify_text(self, text: str) -> str:
        """Искажает текст, используя словарь замены символов."""
        drunk_text = []
        for char in text:
            # Проверяем, есть ли символ в словаре замен
            lower_char = char.lower()
            if lower_char in self.char_map:
                replacements = self.char_map[lower_char]
                new_char = random.choice(replacements)
                # Сохраняем регистр оригинала
                drunk_text.append(new_char.upper() if char.isupper() else new_char)
            else:
                drunk_text.append(char)
        
        # Добавляем случайные пьяные эффекты
        if random.random() < 0.3:
            drunk_text.insert(random.randint(0, len(drunk_text)), random.choice([" *hic*", "…", " *burp*"]))
        
        return ''.join(drunk_text)

    async def process_drink(self, user: discord.Member, guild: discord.Guild, is_admin: bool) -> bool:
        """Обрабатывает команду /выпить."""
        if user.id in self.users:
            return False  # Пользователь уже пьян

        original_nick = user.display_name
        drunk_nick = self.drunkify_text(original_nick)[:32]  # Обрезка до 32 символов

        try:
            await user.edit(nick=drunk_nick)
        except discord.Forbidden:
            if not is_admin:
                raise
            logger.warning(f"⚠️ Не удалось изменить ник администратору {user}")

        self.users[user.id] = {
            "original_nick": original_nick,
            "sober_time": datetime.now().timestamp() + 600,  # 10 минут
            "guild_id": guild.id
        }
        self.save_data()

        asyncio.create_task(self.schedule_sober_up(user.id, 600))
        return True

    async def schedule_sober_up(self, user_id: int, delay: float):
        """Планирует восстановление ника через заданное время."""
        await asyncio.sleep(delay)
        await self.sober_up(user_id)

    async def sober_up(self, user_id: int):
        """Возвращает оригинальный ник пользователя."""
        if user_id not in self.users:
            return

        data = self.users[user_id]
        guild = self.bot.get_guild(data["guild_id"])

        if not guild:
            del self.users[user_id]
            return

        try:
            member = await guild.fetch_member(user_id)
            await member.edit(nick=data["original_nick"])
            logger.info(f"✅ Ник восстановлен: {member.display_name}")
        except discord.NotFound:
            logger.warning(f"🌀 Пользователь {user_id} не найден на сервере")
        except Exception as e:
            logger.error(f"❌ Ошибка восстановления: {e}")
        finally:
            if user_id in self.users:
                del self.users[user_id]
                self.save_data()

    async def restore_nicknames(self):
        """Восстанавливает ники при перезапуске бота."""
        now = datetime.now().timestamp()
        for user_id, data in list(self.users.items()):
            try:
                if data["sober_time"] <= now:
                    await self.sober_up(user_id)
                else:
                    delay = data["sober_time"] - now
                    asyncio.create_task(self.schedule_sober_up(user_id, delay))
            except Exception as e:
                logger.error(f"🌀 Ошибка восстановления: {e}")
        self.save_data()