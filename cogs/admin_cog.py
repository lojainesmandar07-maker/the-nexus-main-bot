import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import zipfile
import io
import json
from datetime import datetime
from core.config import load_config, save_config

DB_PATH = "data/nexus.db"


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_admin(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    # ─────────────────────────────────────────
    # /رسالة_البوت
    # ─────────────────────────────────────────
    @app_commands.command(name="رسالة_البوت", description="أرسل رسالة من البوت إلى أي قناة (للمشرفين)")
    @app_commands.describe(channel="القناة المستهدفة", message="نص الرسالة")
    async def bot_message(self, interaction: discord.Interaction,
                           channel: discord.TextChannel, message: str):
        if not self._is_admin(interaction):
            await interaction.response.send_message("❌ هذا الأمر للمشرفين فقط.", ephemeral=True)
            return
        try:
            await channel.send(message)
            await interaction.response.send_message(
                f"✅ تم إرسال الرسالة إلى {channel.mention}", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ البوت لا يملك صلاحية الإرسال في تلك القناة.", ephemeral=True
            )

    # ─────────────────────────────────────────
    # /تعيين_عالم
    # ─────────────────────────────────────────
    @app_commands.command(name="تعيين_عالم", description="عيّن هذه القناة لعالم قصصي (للمشرفين)")
    @app_commands.choices(world=[
        app_commands.Choice(name="الفانتازيا",     value="fantasy"),
        app_commands.Choice(name="الماضي",          value="past"),
        app_commands.Choice(name="المستقبل",        value="future"),
        app_commands.Choice(name="الواقع البديل",  value="alternate"),
    ])
    async def assign_world(self, interaction: discord.Interaction,
                            world: app_commands.Choice[str]):
        if not self._is_admin(interaction):
            await interaction.response.send_message("❌ هذا الأمر للمشرفين فقط.", ephemeral=True)
            return
        config = load_config()
        config["world_channels"][world.value] = interaction.channel_id
        save_config(config)
        await interaction.response.send_message(
            f"✅ تم تعيين هذه القناة لعالم **{world.name}** بنجاح.", ephemeral=True
        )

    # ─────────────────────────────────────────
    # /تعيين_رتبة
    # ─────────────────────────────────────────
    @app_commands.command(name="تعيين_رتبة", description="اربط شخصية بالرتبة المناسبة (للمشرفين)")
    @app_commands.describe(role="الرتبة التي ستُعطى لأصحاب هذه الشخصية")
    @app_commands.choices(archetype=[
        app_commands.Choice(name="المحارب",  value="warrior"),
        app_commands.Choice(name="الحارس",   value="guardian"),
        app_commands.Choice(name="المخطط",   value="strategist"),
        app_commands.Choice(name="الظل",     value="shadow"),
        app_commands.Choice(name="المتمرد",  value="rebel"),
        app_commands.Choice(name="الباحث",   value="seeker"),
        app_commands.Choice(name="العرّاف",  value="oracle"),
        app_commands.Choice(name="التائه",   value="wanderer"),
    ])
    async def assign_role(self, interaction: discord.Interaction,
                           archetype: app_commands.Choice[str],
                           role: discord.Role):
        if not self._is_admin(interaction):
            await interaction.response.send_message("❌ هذا الأمر للمشرفين فقط.", ephemeral=True)
            return
        config = load_config()
        config["archetype_roles"][archetype.value] = role.id
        save_config(config)
        await interaction.response.send_message(
            f"✅ تم ربط شخصية **{archetype.name}** بالرتبة {role.mention}",
            ephemeral=True
        )

    # ─────────────────────────────────────────
    # /نسخة_احتياطية
    # ─────────────────────────────────────────
    @app_commands.command(name="نسخة_احتياطية", description="تنزيل نسخة احتياطية كاملة من بيانات البوت (للمشرفين)")
    async def backup(self, interaction: discord.Interaction):
        if not self._is_admin(interaction):
            await interaction.response.send_message("❌ هذا الأمر للمشرفين فقط.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        buf = io.BytesIO()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        folder = f"backup_{timestamp}"

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

            # 1. SQLite database
            try:
                with open(DB_PATH, "rb") as f:
                    zf.writestr(f"{folder}/nexus.db", f.read())
            except FileNotFoundError:
                pass

            # 2. config.json
            try:
                with open("data/config.json", "r", encoding="utf-8") as f:
                    zf.writestr(f"{folder}/config.json", f.read())
            except FileNotFoundError:
                pass

            # 3. Human-readable players export
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute("SELECT * FROM players") as cursor:
                        players = [dict(row) async for row in cursor]
                zf.writestr(
                    f"{folder}/export_players.json",
                    json.dumps(players, ensure_ascii=False, indent=2)
                )
            except Exception:
                pass

        buf.seek(0)
        file = discord.File(buf, filename=f"nexus_backup_{timestamp}.zip")
        await interaction.followup.send(
            f"✅ تم إنشاء النسخة الاحتياطية بنجاح.\n"
            f"📦 تحتوي على: قاعدة البيانات + الإعدادات + بيانات اللاعبين.",
            file=file,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(AdminCog(bot))