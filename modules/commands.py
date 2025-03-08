import discord
import random
import asyncio
import os
from dotenv import load_dotenv
from discord.ui import Button, View
from discord import app_commands
from discord.ext import commands
from modules.logger import logger

load_dotenv()
USER_ID = os.getenv("USER_ID")

class BioEmbed(discord.Embed):
    pass

class BattleView(View):
    def __init__(self, player1, player2, inventory_manager):
        super().__init__(timeout=90)
        self.player1 = player1
        self.player2 = player2
        self.inventory_manager = inventory_manager
        self.message_delay = 3  # задержка в 3 секунды между событиями

    async def determine_winner(self):
        """Определяет победителя с 20% шансом ничьей"""
        if random.random() < 0.2:
            return None
        return random.choice([self.player1, self.player2])

    async def give_reward(self, winner):
        # Шанс награды % на получение артефакта
        if random.random() < 0.1:
            rarities = {"common": 0.6, "uncommon": 0.3, "rare": 0.1}
            rarity = random.choices(list(rarities.keys()), weights=list(rarities.values()))[0]
            items = [k for k, v in self.inventory_manager.items.items() if v["rarity"] == rarity]
            
            if not items:
                return "🌀 Кёму потерял награду!"
                
            item_id = random.choice(items)
            user_id = str(winner.id)
            self.inventory_manager.inventories.setdefault(user_id, {})
            self.inventory_manager.inventories[user_id][item_id] = self.inventory_manager.inventories[user_id].get(item_id, 0) + 1
            self.inventory_manager.save_inventories()
            return f"**Награда:** {self.inventory_manager.items[item_id]['name']}"
        else:
            praises = [
                "Луна восхищается твоей доблестью! 🌙",
                "Духи дарят тебе свою благодать! 🎎",
                "Кёму вручает тебе символический веер! 🪭"
            ]
            return f"**Похвала:** {random.choice(praises)}"

    def generate_actions(self):
        """Возвращает список действий (атаки и взаимодействия) от игроков и общие события"""
        return [
            # Действия игрока 1
            lambda: f"{self.player1.mention} запускает град желудей! 🌰💥",
            lambda: f"{self.player1.mention} превращается в гигантский чайник! 🫖🔥",
            lambda: f"{self.player1.mention} вызывает танец фейерверков! 🎆✨",
            lambda: f"{self.player1.mention} наносит сокрушительный удар! 🥊",
            lambda: f"{self.player1.mention} метко бьет противника! 🎯",
            # Действия игрока 2
            lambda: f"{self.player2.mention} парирует удар бумажным зонтом! ☂️🌀",
            lambda: f"{self.player2.mention} создает барьер из рисовых лепешек! 🍘🛡️",
            lambda: f"{self.player2.mention} атакует роем светлячков! ✨🦟",
            lambda: f"{self.player2.mention} увертывается от мощного удара! 🏃‍♂️💨",
            lambda: f"{self.player2.mention} наносит ответный удар! ⚡️",
            # Общие взаимодействия
            lambda: "🌸 Лепестки сакуры запутывают противников!",
            lambda: "⚡️ Статическое электричество шокирует обоих бойцов!",
            lambda: "🎏 Карпы кои образуют водяной смерч! 🐟🌪️",
            lambda: "🍵 Внезапный дождь чайных листьев затрудняет видимость!",
            lambda: "🎎 Куклы-терракота оживают и вмешиваются в бой! 🏺",
            lambda: "🌙 Лунный свет усиливает магические способности!",
            lambda: "🍶 Бочонок саке взрывается, окутывая поле боя паром!",
            lambda: "🦊 Хвост кицунэ сметает всё на своём пути!",
            lambda: "🌀 Тайфун осенних листьев поднимается вокруг бойцов!",
            lambda: "🎑 Ночные цикады начинают оглушительное пение! 🦗"
        ]
    
    def kemyu_reactions(self):
        """Возвращает расширенный список реакций Кёму"""
        return [
            "『 Кёму удивлён! 』😮",
            "『 Кёму хмурится! 』😠",
            "『 Кёму смеётся! 』😂",
            "『 Кёму улыбается! 』😊",
            "『 Кёму в восторге! 』😃",
            "『 Кёму задумчив! 』🤔"
        ]
    
    def player_reactions(self):
        """Возвращает расширенный список реакций игроков"""
        return [
            f"{self.player1.mention} поднимает кулак в знак решимости!",
            f"{self.player2.mention} отвечает броском в ответ!",
            f"{self.player1.mention} с улыбкой принимает вызов!",
            f"{self.player2.mention} готовится к контратаке!",
            f"{self.player1.mention} выкрикивает боевой клич!",
            f"{self.player2.mention} с усмешкой встречает атаку!",
            f"{self.player1.mention} уверенно шагает вперёд!",
            f"{self.player2.mention} быстро реагирует на удар!"
        ]

    async def battle_animation(self, msg):
        phases = [
            "**🌀 Подготовка к бою:** Духи природы наблюдают...",
            "**⚔️ Раунд 1:** Первые атаки!",
            "**🌪️ Раунд 2:** Эскалация конфликта!",
            "**💥 Раунд 3:** Решающая схватка!",
            "**🎇 Финал:** Последний рывок!"
        ]
        
        for phase in phases:
            await msg.edit(content=f"{msg.content}\n\n{phase}")
            await asyncio.sleep(self.message_delay)
            
            # За фазу выводятся два действия – по одному от каждого участника или случайные события
            action1 = random.choice(self.generate_actions())()
            action2 = random.choice(self.generate_actions())()
            await msg.edit(content=f"{msg.content}\n{action1}\n{action2}")
            await asyncio.sleep(self.message_delay)
            
            # Добавляем реакцию игроков с вероятностью 50%
            if random.random() < 0.5:
                player_reaction = random.choice(self.player_reactions())
                await msg.edit(content=f"{msg.content}\n{player_reaction}")
                await asyncio.sleep(self.message_delay)
            
            # Реакция Кёму с вероятностью 50%
            if random.random() < 0.5:
                kemu_reaction = random.choice(self.kemyu_reactions())
                await msg.edit(content=f"{msg.content}\n{kemu_reaction}")
                await asyncio.sleep(self.message_delay)
                
                # Дополнительная реакция Кёму с вероятностью 40%
                if random.random() < 0.4:
                    extra_reactions = [
                        "『 Кёму жуёт моти и аплодирует! 』🍡👏",
                        "『 Кёму машет флагом с символом храма! 』⛩️",
                        "『 Кёму играет на сякухати! 』🎶🎍",
                        "『 Кёму восторженно кричит! 』😆",
                        "『 Кёму слегка подмигивает! 』😉"
                    ]
                    await msg.edit(content=f"{msg.content}\n{random.choice(extra_reactions)}")
                    await asyncio.sleep(self.message_delay)

    @discord.ui.button(label="Начать бой!", style=discord.ButtonStyle.green, emoji="⚔️")
    async def start_battle(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        
        # Начальная анимация
        embed = discord.Embed(description="🕒 **Подготовка арены...**")
        msg = await interaction.followup.send(embed=embed)
        
        await asyncio.sleep(self.message_delay)
        await msg.edit(embed=discord.Embed(
            title="⚔️ Бой Начинается!",
            description=f"{self.player1.mention} vs {self.player2.mention}",
            color=0xe5d4c0
        ))
        
        await self.battle_animation(msg)
        
        winner = await self.determine_winner()
        if not winner:
            result = "🌸 Бой закончился вничью! Оба достойны уважения."
        else:
            reward = await self.give_reward(winner)
            result = f"""🎌 **ПОБЕДИТЕЛЬ:** {winner.mention}
{reward}
『 Кёму совершает ритуальный поклон 』🙇"""
        
        result_embed = discord.Embed(
            title="🍁 Итоги Сражения",
            description=result,
            color=0xe5d4c0
        ).set_thumbnail(url="https://i.pinimg.com/originals/7a/ed/30/7aed30356cb8df5aea46c7b3a82d1f52.gif")
        
        await msg.edit(embed=result_embed)
        self.stop()

class KemuCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.drunk_manager = bot.drunk_manager
        self.inventory_manager = bot.inventory_manager

    @app_commands.command(name="биография", description="Показать биографию Кёму 🎴")
    async def biography(self, interaction: discord.Interaction):
        try:
            with open("data/biography.txt", "r", encoding="utf-8") as f:
                bio_text = f.read()
        except Exception as e:
            bio_text = "Биография временно недоступна."
            logger.error(f"❌ Ошибка загрузки биографии: {e}")

        embed = BioEmbed()
        embed.color = 0xe5d4c0
        embed.description = (
            f"*«Цветок сакуры не торопится распуститься»*\n\n"
            f"{bio_text}\n\n"
            f"🍙 **Присматривает:** {interaction.user.mention}"
        )
        embed.set_thumbnail(url="https://i.pinimg.com/736x/b2/b0/4b/b2b04b4ce6c3ee97035bd29c64306131.jpg")
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Благодарность",
            style=discord.ButtonStyle.primary,
            emoji="🌸",
            url=f"https://discord.com/users/{USER_ID}"
        ))
        
        await interaction.response.send_message(embed=embed, view=view)
        logger.info(f"📜 {interaction.user} запросил биографию")

    @app_commands.command(name="выпить", description="Выпить ритуальное саке 🍶")
    async def drink(self, interaction: discord.Interaction):
        try:
            if not interaction.guild.me.guild_permissions.manage_nicknames:
                await interaction.response.send_message(
                    "🌀 Кёму не имеет прав изменять ники!",
                    ephemeral=True
                )
                return

            is_admin = interaction.user.guild_permissions.administrator
            success = await self.drunk_manager.process_drink(interaction.user, interaction.guild, is_admin)
            
            if not success:
                await interaction.response.send_message(
                    "🌀 Вы уже под воздействием саке!",
                    ephemeral=True
                )
                return

            drunk_messages = [
                "под кайфом от саке начинает рассказывать древние легенды!",
                "с легкой неразберихой в голосе заявляет: 'Саке дарует мне вдохновение!'",
                "его смех разносится по залу, словно звон бокалов!",
                "на мгновение забывает о мире, погружаясь в сакральное веселье!"
            ]
            embed = discord.Embed(
                title="🍶 Ритуал Очищения",
                description=f"{interaction.user.mention} {random.choice(drunk_messages)}",
                color=0xe5d4c0
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                "🌀 Ритуал прерван — духи саке не отвечают!",
                ephemeral=True
            )
            logger.error(f"Ошибка в команде /выпить: {e}")

    @app_commands.command(name="инвентарь", description="Показать коллекцию артефактов 🎎")
    async def inventory(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            user_id = str(interaction.user.id)
            inventory = self.inventory_manager.get_user_inventory(user_id)
            
            embed = discord.Embed(
                title="🗃️ Тайное Хранилище",
                color=0xe5d4c0
            ).set_thumbnail(url="https://i.pinimg.com/originals/e2/62/eb/e262ebb7707f8b83cb282c2f63cd4993.gif")
            
            if not inventory:
                embed.description = "Пусто... Даже пылинки нет! 🍂"
            else:
                for item_id, count in inventory.items():
                    item = self.inventory_manager.get_item_info(item_id)
                    embed.add_field(
                        name=f"{item['name']} ×{count}",
                        value=f"*{item['description']}*",
                        inline=False
                    )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Ошибка инвентаря: {e}")

    @app_commands.command(name="бои_тануки", description="Вызов на ритуальный бой 🍃")
    @app_commands.describe(оппонент="Выберите соперника")
    async def tanuki_battle(self, interaction: discord.Interaction, оппонент: discord.Member):
        if оппонент == interaction.user:
            return await interaction.response.send_message("🌀 Нельзя сражаться со своим отражением!", ephemeral=True)
            
        view = BattleView(interaction.user, оппонент, self.inventory_manager)
        embed = discord.Embed(
            title="⚔️ Вызов Принят!",
            description=f"{interaction.user.mention} вызывает {оппонент.mention} на священный бой!",
            color=0xe5d4c0
        ).set_image(url="https://i.pinimg.com/originals/52/9f/9c/529f9ce3e4bdd0fd5eccc2ee36134c87.gif")
        
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="помощь", description="Открыть руководство мудрости 📜")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎴 Свиток Знаний Кёму",
            description="```diff\n+ Доступные Ритуалы:\n```",
            color=0xe5d4c0
        ).add_field(
            name="🍶 Основные Практики",
            value="• `/биография` - История духа\n• `/выпить` - Ритуальное очищение\n• `/инвентарь` - Сокровищница",
            inline=False
        ).add_field(
            name="🎌 Боевые Искусства",
            value="• `/бои_тануки` - Вызов на поединок",
            inline=False
        ).set_image(url="https://i.pinimg.com/originals/e8/2d/89/e82d895dcb38cf4fcee7d5dad950183e.gif")
        
        await interaction.response.send_message(embed=embed)

async def setup_commands(bot: commands.Bot):
    await bot.add_cog(KemuCommands(bot))
