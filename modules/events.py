import discord
from discord.ext import commands
from modules.logger import logger

class KemuEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Сначала обработать команды
        await self.bot.process_commands(message)
        
        if message.author.bot:
            return

        if hasattr(self.bot, 'drunk_manager'):
            drunk_manager = self.bot.drunk_manager
            if message.author.id in drunk_manager.users:
                logger.info(f"🍶 {message.author} отправил пьяное сообщение")
                drunk_content = drunk_manager.drunkify_text(message.content)
                
                try:
                    await message.delete()
                except discord.Forbidden:
                    logger.warning(f"🚫 Не удалось удалить сообщение от {message.author}")
                except discord.HTTPException as e:
                    logger.error(f"❌ Ошибка при удалении: {e}")
                else:
                    avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
                    embed = discord.Embed(
                        description=f"*{drunk_content}*",
                        color=0xe5d4c0,
                        timestamp=message.created_at
                    )
                    embed.set_author(
                        name=f"🍶 {message.author.display_name}",
                        icon_url=avatar_url
                    )
                    embed.set_footer(text="💫 Пьяное бормотание")
                    await message.channel.send(embed=embed)

async def setup_events(bot: commands.Bot):
    await bot.add_cog(KemuEvents(bot))