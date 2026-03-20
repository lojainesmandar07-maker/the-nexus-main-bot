import discord
from discord import app_commands
from discord.ext import commands
import json
from core.config import get_config

NPC_PATHS = {
    "fantasy":   "data/npcs/fantasy_npcs.json",
    "past":      "data/npcs/past_npcs.json",
    "future":    "data/npcs/future_npcs.json",
    "alternate": "data/npcs/alternate_npcs.json",
}

WORLD_NAMES = {
    "fantasy":   "الفانتازيا",
    "past":      "الماضي",
    "future":    "المستقبل",
    "alternate": "الواقع البديل",
}

ARCHETYPE_NAMES = {
    "warrior": "المحارب", "guardian": "الحارس", "strategist": "المخطط",
    "shadow": "الظل", "rebel": "المتمرد", "seeker": "الباحث",
    "oracle": "العرّاف", "wanderer": "التائه",
}


def load_npcs(world: str) -> list:
    path = NPC_PATHS.get(world, "")
    if not path:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def get_member_archetype(member: discord.Member) -> str | None:
    archetype_roles = get_config("archetype_roles", {})
    role_to_arch = {int(v): k for k, v in archetype_roles.items() if v}
    for role in member.roles:
        if role.id in role_to_arch:
            return role_to_arch[role.id]
    return None


class TopicSelectMenu(discord.ui.Select):
    def __init__(self, npc: dict, member_archetype: str | None):
        self.npc = npc
        self.member_archetype = member_archetype

        options = [
            discord.SelectOption(
                label=t["label"][:100],
                value=t["id"],
                emoji=t.get("emoji", "💬")
            )
            for t in npc.get("topics", [])
        ]
        super().__init__(
            placeholder="اختر موضوعاً للحديث عنه...",
            options=options,
            min_values=1,
            max_values=1,
            custom_id=f"npc_topic_{npc['id']}"
        )

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]
        topics = {t["id"]: t for t in self.npc.get("topics", {})}
        topic = topics.get(selected_id)

        if not topic:
            await interaction.response.send_message("❌ موضوع غير موجود.", ephemeral=True)
            return

        # Use archetype-specific response if available
        response = topic["response"]
        if self.member_archetype:
            arch_resp = self.npc.get("archetype_responses", {}).get(self.member_archetype)
            if arch_resp and selected_id == "ask_advice":
                response = arch_resp

        embed = discord.Embed(
            title=f"💬 {self.npc['name']}",
            description=f"*{self.npc.get('personality', '')}*\n\n{response}",
            color=0x4B3D60
        )
        if self.npc.get("image_url"):
            embed.set_thumbnail(url=self.npc["image_url"])

        await interaction.response.send_message(embed=embed, ephemeral=True)


class NPCView(discord.ui.View):
    def __init__(self, npc: dict, member_archetype: str | None):
        super().__init__(timeout=180)
        self.add_item(TopicSelectMenu(npc, member_archetype))


class NPCCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="شخصيات", description="تفاعل مع شخصيات عالم The Nexus")
    @app_commands.choices(world=[
        app_commands.Choice(name="الفانتازيا",    value="fantasy"),
        app_commands.Choice(name="الماضي",         value="past"),
        app_commands.Choice(name="المستقبل",       value="future"),
        app_commands.Choice(name="الواقع البديل", value="alternate"),
    ])
    async def show_npcs(self, interaction: discord.Interaction,
                         world: app_commands.Choice[str]):
        npcs = load_npcs(world.value)
        if not npcs:
            await interaction.response.send_message(
                f"❌ لا توجد شخصيات مسجلة لعالم {world.name} بعد.", ephemeral=True
            )
            return

        member_archetype = get_member_archetype(interaction.user)

        # Show first NPC — user can run command again for others
        # For simplicity: show all NPCs as a select first, then show chosen NPC
        options = [
            discord.SelectOption(
                label=npc["name"][:100],
                value=npc["id"],
                description=npc.get("title", "")[:100],
                emoji="🧙"
            )
            for npc in npcs
        ]

        class NPCPickView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                select = discord.ui.Select(
                    placeholder="اختر شخصية...",
                    options=options,
                    custom_id=f"npc_pick_{world.value}"
                )
                async def on_select(inter: discord.Interaction):
                    chosen_id = select.values[0]
                    chosen_npc = next((n for n in npcs if n["id"] == chosen_id), None)
                    if not chosen_npc:
                        await inter.response.send_message("❌ لم يُعثر على الشخصية.", ephemeral=True)
                        return

                    embed = discord.Embed(
                        title=f"🧙 {chosen_npc['name']}",
                        description=(
                            f"**{chosen_npc.get('title', '')}**\n\n"
                            f"*{chosen_npc.get('personality', '')}*\n\n"
                            f"اختر موضوعاً للحديث عنه:"
                        ),
                        color=0x4B3D60
                    )
                    if chosen_npc.get("image_url"):
                        embed.set_image(url=chosen_npc["image_url"])

                    npc_view = NPCView(chosen_npc, member_archetype)
                    await inter.response.edit_message(embed=embed, view=npc_view)

                select.callback = on_select
                self.add_item(select)

        embed = discord.Embed(
            title=f"🌍 شخصيات عالم {world.name}",
            description="اختر الشخصية التي تريد التحدث معها:",
            color=0x4B3D60
        )
        await interaction.response.send_message(embed=embed, view=NPCPickView(), ephemeral=True)


async def setup(bot):
    await bot.add_cog(NPCCog(bot))