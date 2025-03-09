import discord
import datetime
from discord import app_commands
from discord.ext import commands

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="tanuki_curse", 
        description="Наложить проклятие тануки на участника 🔮"
    )
    @app_commands.default_permissions(administrator=True)  # Видна только админам
    @app_commands.describe(
        user="Кого проклянуть?", 
        duration="Длительность проклятия в минутах (1-1440)"
    )
    async def tanuki_curse(
        self, 
        interaction: discord.Interaction,
        user: discord.Member,
        duration: app_commands.Range[int, 1, 1440] = 5
    ):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "🚫 Только избранные тануки-админы могут использовать эту команду!",
                ephemeral=True
            )

        try:
            await user.edit(
                timed_out_until=discord.utils.utcnow() + datetime.timedelta(minutes=duration),
                reason=f"Проклятие от {interaction.user.name}"
            )
            await interaction.response.send_message(
                f"🎭 **Кёму хлопает в лапки!** {user.mention} теперь проклят на {duration} минут.\n"
                f"*Причина: «Слишком громко смеялся над животиком тануки»* 🐾"
            )
        except Exception as e:
            self.bot.logger.error(f"Ошибка в tanuki_curse: {e}")
            await interaction.response.send_message("⚠️ Что-то пошло не так...")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))