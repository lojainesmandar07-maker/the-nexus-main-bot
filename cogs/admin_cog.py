import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import zipfile
import io
import json
from datetime import datetime
from core.config import load_config, save_config
from ui.embeds import EmbedBuilder

DB_PATH = "data/nexus.db"


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_admin(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    WORLD_CHOICES = [
        app_commands.Choice(name="الفانتازيا", value="fantasy"),
        app_commands.Choice(name="الماضي", value="past"),
        app_commands.Choice(name="المستقبل", value="future"),
        app_commands.Choice(name="الواقع البديل", value="alternate"),
    ]

    # ─────────────────────────────────────────
    # /رسالة_البوت
    # ─────────────────────────────────────────
    @app_commands.command(name="رسالة_البوت", description="أرسل رسالة من البوت إلى أي قناة (للمشرفين)")
    @app_commands.describe(channel="القناة المستهدفة", message="نص الرسالة")
    async def send_bot_message(self, interaction: discord.Interaction,
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
    @app_commands.choices(world=WORLD_CHOICES)
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
    # /نشر_شرح_العالم
    # ─────────────────────────────────────────
    @app_commands.command(name="نشر_شرح_العالم", description="انشر إمبد تعريفي لعالم محدد (للمشرفين)")
    @app_commands.describe(
        world="العالم المراد نشر شرحه",
        channel="قناة الشرح (اختياري). إن تُرك فارغاً سيتم الاعتماد على القناة الحالية.",
    )
    @app_commands.choices(world=WORLD_CHOICES)
    async def publish_world_explanation(
        self,
        interaction: discord.Interaction,
        world: app_commands.Choice[str],
        channel: discord.TextChannel | None = None,
    ):
        if not self._is_admin(interaction):
            await interaction.response.send_message("❌ هذا الأمر للمشرفين فقط.", ephemeral=True)
            return

        config = load_config()
        configured_channel_id = config.get("world_channels", {}).get(world.value)
        target_channel = channel or interaction.channel

        if target_channel is None:
            await interaction.response.send_message(
                "❌ تعذّر تحديد القناة المستهدفة. جرّب تحديد `channel` صراحةً.",
                ephemeral=True,
            )
            return

        if configured_channel_id and int(configured_channel_id) != target_channel.id:
            mention = f"<#{configured_channel_id}>"
            await interaction.response.send_message(
                f"❌ قناة هذا العالم مضبوطة على {mention}. "
                f"انشر الشرح هناك أو عدّل الربط عبر `/تعيين_عالم`.",
                ephemeral=True,
            )
            return

        if not configured_channel_id and channel is None:
            await interaction.response.send_message(
                "❌ لا يوجد ربط محفوظ لهذا العالم بعد. "
                "إمّا نفّذ `/تعيين_عالم` في قناة الشرح أولاً، أو مرّر `channel` مباشرة.",
                ephemeral=True,
            )
            return

        try:
            embed = EmbedBuilder.world_explanation_embed(world.value)
            await target_channel.send(embed=embed)
            await interaction.response.send_message(
                f"✅ تم نشر شرح **{world.name}** في {target_channel.mention}.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ البوت لا يملك صلاحية إرسال الرسائل أو الإمبد في القناة المستهدفة.",
                ephemeral=True,
            )

    # ─────────────────────────────────────────
    # /نشر_شروحات_العوالم
    # ─────────────────────────────────────────
    @app_commands.command(name="نشر_شروحات_العوالم", description="انشر جميع شروحات العوالم في قنواتها المضبوطة (للمشرفين)")
    async def publish_all_world_explanations(self, interaction: discord.Interaction):
        if not self._is_admin(interaction):
            await interaction.response.send_message("❌ هذا الأمر للمشرفين فقط.", ephemeral=True)
            return

        config = load_config()
        world_channels = config.get("world_channels", {})

        await interaction.response.defer(ephemeral=True, thinking=True)

        world_labels = {choice.value: choice.name for choice in self.WORLD_CHOICES}
        sent_worlds = []
        skipped_worlds = []

        for world_key, world_name in world_labels.items():
            channel_id = world_channels.get(world_key)
            if not channel_id:
                skipped_worlds.append(f"• {world_name}: لا توجد قناة مضبوطة")
                continue

            target_channel = interaction.guild.get_channel(int(channel_id)) if interaction.guild else None
            if target_channel is None:
                skipped_worlds.append(f"• {world_name}: القناة غير موجودة أو لا يمكن الوصول إليها")
                continue

            try:
                await target_channel.send(embed=EmbedBuilder.world_explanation_embed(world_key))
                sent_worlds.append(f"• {world_name} → {target_channel.mention}")
            except discord.Forbidden:
                skipped_worlds.append(f"• {world_name}: لا توجد صلاحية إرسال في {target_channel.mention}")

        if not sent_worlds:
            await interaction.followup.send(
                "❌ لم يتم نشر أي شرح.\n" + "\n".join(skipped_worlds),
                ephemeral=True,
            )
            return

        summary = "✅ تم نشر شروحات العوالم التالية:\n" + "\n".join(sent_worlds)
        if skipped_worlds:
            summary += "\n\n⚠️ عناصر لم تُنشر:\n" + "\n".join(skipped_worlds)
        await interaction.followup.send(summary, ephemeral=True)

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
