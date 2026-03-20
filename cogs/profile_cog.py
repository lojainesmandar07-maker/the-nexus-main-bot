import discord
from discord import app_commands
from discord.ext import commands
from core.bot import StoryBot
from core.config_manager import get_config
from core.db import get_player_profile, register_player

class ProfileCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot

    @app_commands.command(name="بروفايل", description="عرض ملفك الشخصي ولقبك وإنجازاتك")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user

        # Ensure player exists in DB
        await register_player(target_user.id)

        # Get DB data
        title, stories_completed, joined_at = await get_player_profile(target_user.id)

        # Determine archetype from roles
        archetype_roles = get_config("archetype_roles", {})
        member_role_ids = [r.id for r in target_user.roles]

        # Reverse map to find archetype name
        archetype_key = next((k for k, v in archetype_roles.items() if v in member_role_ids), None)

        archetype_names = {
            "strategist": "المخطط", "guardian": "الحارس", "shadow": "الظل",
            "rebel": "المتمرد", "seeker": "الباحث", "warrior": "المحارب",
            "oracle": "العرّاف", "wanderer": "التائه"
        }

        archetype_display = archetype_names.get(archetype_key, "غير محدد")

        embed = discord.Embed(
            title=f"ملف اللاعب: {target_user.display_name}",
            color=0x4B0082
        )
        embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)

        embed.add_field(name="🧬 الشخصية", value=archetype_display, inline=True)
        embed.add_field(name="🏷️ اللقب", value=title or "بدون لقب", inline=True)
        embed.add_field(name="📖 القصص المكتملة", value=str(stories_completed), inline=True)

        # Format join date beautifully
        if joined_at:
            try:
                from datetime import datetime
                join_date = datetime.fromisoformat(joined_at)
                embed.add_field(name="📅 انضم منذ", value=discord.utils.format_dt(join_date, style="R"), inline=False)
            except:
                pass

        if not archetype_key:
            embed.set_footer(text="لم تحدد شخصيتك بعد! استخدم الأمر /اختبار-الشخصية")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: StoryBot):
    await bot.add_cog(ProfileCog(bot))
