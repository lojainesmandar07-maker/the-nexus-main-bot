import discord
from discord import app_commands
from discord.ext import commands
import zipfile
import io
import json
from datetime import datetime
from core.bot import StoryBot
from core.config_manager import set_config, get_config, update_nested_config
from core.db import get_all_players, DATABASE_FILE

class AdminCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot

    @app_commands.command(name="رسالة-البوت", description="إرسال رسالة من البوت إلى قناة محددة")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def bot_message(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, embed: bool = False):
        try:
            if embed:
                em = discord.Embed(description=message, color=discord.Color.blue())
                await channel.send(embed=em)
            else:
                await channel.send(message)
            await interaction.response.send_message("✅ تم إرسال الرسالة بنجاح.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ حدث خطأ: {e}", ephemeral=True)

    @app_commands.command(name="تعيين-عالم", description="تخصيص القناة الحالية لعالم معين")
    @app_commands.describe(world="اختر العالم")
    @app_commands.choices(world=[
        app_commands.Choice(name="الفانتازيا", value="fantasy"),
        app_commands.Choice(name="الماضي", value="past"),
        app_commands.Choice(name="المستقبل", value="future"),
        app_commands.Choice(name="الواقع البديل", value="alternate")
    ])
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def set_world_channel(self, interaction: discord.Interaction, world: str):
        channel_id = interaction.channel_id
        update_nested_config("world_channels", world, channel_id)
        await interaction.response.send_message(f"✅ تم تعيين هذه القناة لعالم: {world}", ephemeral=True)

    @app_commands.command(name="تعيين-اختبار", description="تخصيص القناة الحالية لاختبار الشخصية")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def set_test_channel(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        set_config("test_channel", channel_id)
        await interaction.response.send_message("✅ تم تعيين هذه القناة لاختبار الشخصية.", ephemeral=True)

    @app_commands.command(name="تعيين-رتبة", description="ربط شخصية (Archetype) برتبة في السيرفر")
    @app_commands.describe(archetype="اختر الشخصية", role="اختر الرتبة")
    @app_commands.choices(archetype=[
        app_commands.Choice(name="المخطط (The Strategist)", value="strategist"),
        app_commands.Choice(name="الحارس (The Guardian)", value="guardian"),
        app_commands.Choice(name="الظل (The Shadow)", value="shadow"),
        app_commands.Choice(name="المتمرد (The Rebel)", value="rebel"),
        app_commands.Choice(name="الباحث (The Seeker)", value="seeker"),
        app_commands.Choice(name="المحارب (The Warrior)", value="warrior"),
        app_commands.Choice(name="العرّاف (The Oracle)", value="oracle"),
        app_commands.Choice(name="التائه (The Wanderer)", value="wanderer"),
    ])
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def set_archetype_role(self, interaction: discord.Interaction, archetype: str, role: discord.Role):
        update_nested_config("archetype_roles", archetype, role.id)
        await interaction.response.send_message(f"✅ تم ربط شخصية '{archetype}' بالرتبة {role.mention}.", ephemeral=True)

    @app_commands.command(name="تعيين-امبيد-الشرح", description="إرسال امبيد الشرح للقناة الحالية")
    @app_commands.describe(embed_type="اختر نوع الشرح")
    @app_commands.choices(embed_type=[
        app_commands.Choice(name="شرح قصص العوالم", value="worlds"),
        app_commands.Choice(name="شرح القصص الفردية", value="solo"),
        app_commands.Choice(name="شرح القصص الجماعية", value="multi"),
        app_commands.Choice(name="شرح اختبار الشخصية", value="test"),
        app_commands.Choice(name="طريقة اللعب العامة", value="general"),
    ])
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def send_explanation_embed(self, interaction: discord.Interaction, embed_type: str):
        embeds = {
            "worlds": discord.Embed(title="🌍 قصص العوالم", description="في هذه القناة، يمكنك الانغماس في قصص مخصصة لهذا العالم. اختر مسارك بعناية.", color=discord.Color.gold()),
            "solo": discord.Embed(title="👤 القصص الفردية", description="قصص مصممة للاعب واحد. تعتمد على اختياراتك وذكائك، وكل قرار يهم. العب بالأمر `/قصص-فردية`.", color=0x1C1C1C),
            "multi": discord.Embed(title="👥 القصص الجماعية", description="القرارات هنا تؤخذ بالتصويت. مصير المجموعة يعتمد على رأي الأغلبية.", color=discord.Color.blue()),
            "test": discord.Embed(title="🧪 اختبار الشخصية", description="اكتشف شخصيتك الفريدة من بين 8 شخصيات مختلفة. اكتب الأمر `/اختبار-الشخصية` للبدء.", color=0x2E4057),
            "general": discord.Embed(title="🎮 طريقة اللعب", description="استخدم الأزرار والقوائم المنسدلة لاختيار مسارك. لا توجد نهايات صحيحة أو خاطئة، لكن لكل قرار عواقب.", color=discord.Color.green())
        }

        selected_embed = embeds.get(embed_type)
        if selected_embed:
            await interaction.channel.send(embed=selected_embed)
            await interaction.response.send_message("✅ تم إرسال الشرح بنجاح.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ نوع الشرح غير صالح.", ephemeral=True)

    @app_commands.command(name="نسخة-احتياطية", description="إنشاء نسخة احتياطية من قواعد البيانات والإعدادات")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def backup_data(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            # 1. Gather files
            config_data = {}
            with open("data/config.json", "r", encoding="utf-8") as f:
                config_data = f.read()

            db_data = b""
            with open(DATABASE_FILE, "rb") as f:
                db_data = f.read()

            # 2. Export players JSON
            players = await get_all_players()
            export_players_data = json.dumps(players, ensure_ascii=False, indent=4)

            # 3. Create Zip in memory
            zip_buffer = io.BytesIO()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            folder_name = f"backup_{timestamp}/"

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(f"{folder_name}config.json", config_data)
                zip_file.writestr(f"{folder_name}rpg.db", db_data)
                zip_file.writestr(f"{folder_name}export_players.json", export_players_data)

            zip_buffer.seek(0)

            file = discord.File(fp=zip_buffer, filename=f"backup_{timestamp}.zip")
            await interaction.followup.send("✅ تم تجهيز النسخة الاحتياطية بنجاح.", file=file, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ حدث خطأ أثناء إنشاء النسخة الاحتياطية: {e}", ephemeral=True)

async def setup(bot: StoryBot):
    await bot.add_cog(AdminCog(bot))
