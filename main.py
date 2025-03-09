import os
import sys
import time
import signal
import logging
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands
from pypresence import Presence
from modules.logger import setup_logger
from modules.drunk import DrunkManager
from modules.inventory import InventoryManager
from modules.events import setup_events
from modules.commands import setup_commands

# Инициализация систем
logger = setup_logger()
load_dotenv()
BOT_ID = os.getenv("BOT_ID")

class PresenceManager:
    def __init__(self, bot):
        self.bot = bot
        self.rpc = None
        self.client_id = BOT_ID
        self.start_time = int(time.time())

    async def setup_presence(self):
        try:
            await self.bot.loop.run_in_executor(None, self._connect_rpc)
            await self._update_presence()
            logger.info("⭐ Discord RPC успешно активирован")
            return True
        except Exception as e:
            logger.error(f"RPC Error: {str(e)}")
            return False

    def _connect_rpc(self):
        self.rpc = Presence(self.client_id)
        self.rpc.connect()

    async def _update_presence(self, drinks: int = 4):
        activity = {
            "state": f"🍶 Выпито саке: {drinks}",
            "details": "🌸 Присматривает за Кёму",
            "large_image": "1",
            "large_text": "Кёму",
            "start": self.start_time
        }
        await self.bot.loop.run_in_executor(
            None, lambda: self.rpc.update(**activity)
        )

class KemuBot(commands.Bot):
    def __init__(self):
        self.logger = logger
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='/',
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="🍡 Ритуальные практики"
            ),
            status=discord.Status.idle
        )
        self.drunk_manager = DrunkManager(self)
        self.inventory_manager = InventoryManager()
        self.presence_manager = PresenceManager(self)
        self.ready_flag = False
        self.ready_lock = asyncio.Lock()

    async def setup_hook(self):
        try:
            logger.info("🟢 Инициализация систем...")
            if not os.path.exists("data"):
                os.makedirs("data")
                logger.warning("📂 Создана папка data")

            await self.load_extension("modules.admin")
            
            await asyncio.wait_for(setup_commands(self), timeout=10)
            await asyncio.wait_for(setup_events(self), timeout=10)
            await asyncio.wait_for(self.drunk_manager.restore_nicknames(), timeout=30)
            
            synced = await self.tree.sync()
            logger.info(f"🌸 Синхронизировано команд: {len(synced)}")
            logger.info(f"📦 Загружено предметов: {len(self.inventory_manager.items)}")
            logger.info(f"🎒 Загружено инвентарей: {len(self.inventory_manager.inventories)}")

        except asyncio.TimeoutError:
            logger.critical("🚨 Превышено время инициализации!")
        except Exception as e:
            logger.critical(f"🚨 Критический сбой: {e}")
            raise

    async def on_ready(self):
        async with self.ready_lock:
            if self.ready_flag:
                return
            self.ready_flag = True
            logger.info(f"✅ Активен как {self.user}")
            logger.info(f"🌐 Серверов: {len(self.guilds)}")
            try:
                await self.presence_manager.setup_presence()
            except Exception as e:
                logger.error(f"❌ Ошибка RPC: {e}")

    async def close(self):
        logger.info("⛔ Завершение процессов...")
        try:
            self.inventory_manager.save_inventories()
            logger.info("💾 Инвентари сохранены")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
        
        # Безопасное закрытие RPC
        if self.presence_manager.rpc:
            try:
                self.presence_manager.rpc.close()
            except Exception as e:
                logger.error(f"❌ Ошибка закрытия RPC: {e}")
        
        await super().close()

def handle_exit(signum, frame):
    asyncio.create_task(bot.close())

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    discord.utils.setup_logging(handler=logging.NullHandler())
    bot = KemuBot()
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    try:
        bot.run(os.getenv('DISCORD_TOKEN'), log_handler=None)
    except discord.LoginFailure:
        logger.critical("🔑 Неверный токен Discord!")
    except KeyboardInterrupt:
        logger.info("🚫 Принудительное завершение")
    except Exception as e:
        logger.critical(f"💀 Фатальная ошибка: {str(e)}")