import discord
from discord import app_commands
from discord.ext import commands
from core.bot import StoryBot
from core.config_manager import get_config, update_nested_config

class NPCTopic1Button(discord.ui.Button):
    def __init__(self, npc_id: str):
        super().__init__(
            label="اسأله عن العالم",
            style=discord.ButtonStyle.primary,
            custom_id=f"rpg_npc_topic1_{npc_id}"
        )
        self.npc_id = npc_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("العالم هنا قاسي، وعليك الاعتماد على ذكائك للنجاة.", ephemeral=True)


class NPCTopic2Button(discord.ui.Button):
    def __init__(self, npc_id: str):
        super().__init__(
            label="اطلب نصيحة",
            style=discord.ButtonStyle.success,
            custom_id=f"rpg_npc_topic2_{npc_id}"
        )
        self.npc_id = npc_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("النصيحة الوحيدة هي: لا تثق بأحد في الظلام.", ephemeral=True)


class NPCTopicView(discord.ui.View):
    def __init__(self, npc_id: str):
        super().__init__(timeout=None)
        self.add_item(NPCTopic1Button(npc_id))
        self.add_item(NPCTopic2Button(npc_id))


class NPCTalkButton(discord.ui.Button):
    def __init__(self, npc_id: str):
        super().__init__(
            label="تحدث معه",
            style=discord.ButtonStyle.secondary,
            custom_id=f"rpg_talk_npc_{npc_id}"
        )
        self.npc_id = npc_id

    async def callback(self, interaction: discord.Interaction):
        # Read player archetype to flavor response
        member_roles = [r.id for r in interaction.user.roles]
        roles_config = get_config("archetype_roles", {})

        # reverse lookup
        archetype = next((k for k, v in roles_config.items() if v in member_roles), None)

        flavor = "أهلاً بك أيها الغريب."
        if archetype == "strategist":
            flavor = "أرى في عينيك التخطيط... قل لي، هل لديك حل لهذه المملكة؟"
        elif archetype == "warrior":
            flavor = "محارب! أخيراً شخص يمتلك الشجاعة الكافية لإنقاذنا."

        view = NPCTopicView(self.npc_id)
        await interaction.response.send_message(f"**الملك التائه:** {flavor}", view=view, ephemeral=True)


class NPCTalkView(discord.ui.View):
    def __init__(self, npc_id: str):
        super().__init__(timeout=None)
        self.add_item(NPCTalkButton(npc_id))


class NPCCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot

    @app_commands.command(name="تعيين-شخصية", description="وضع شخصية تفاعلية (NPC) في القناة الحالية")
    @app_commands.describe(npc_id="معرف الشخصية (مثال: fantasy_king)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def set_npc(self, interaction: discord.Interaction, npc_id: str):
        channel_id = interaction.channel_id
        update_nested_config("npc_channels", npc_id, channel_id)

        embed = discord.Embed(
            title="👤 شخصية تفاعلية: الملك التائه",
            description="يبدو عليه التعب، وكأنه يحمل عبء المملكة على كتفيه...",
            color=0x8B4513
        )

        view = NPCTalkView(npc_id)

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ تم وضع الشخصية في القناة.", ephemeral=True)

async def setup(bot: StoryBot):
    await bot.add_cog(NPCCog(bot))
