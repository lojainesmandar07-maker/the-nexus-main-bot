import discord
from discord.ext import commands
from engine.story_manager import StoryManager
from engine.event_manager import EventManager


class StoryBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()

        # This bot currently uses slash/app commands only.
        # Using mention-only prefix avoids requiring privileged message content intent.
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

        self.story_manager = StoryManager()
        self.story_manager.apply_loading_rules()
        self.event_manager = EventManager(self, self.story_manager)

    async def setup_hook(self):
        # Re-register persistent views BEFORE loading cogs
        from ui.listing_view import SoloLibraryView, MultiLibraryView
        from ui.world_browser import WorldSelectView
        self.add_view(SoloLibraryView({}, timeout=None))
        self.add_view(MultiLibraryView({}, timeout=None))
        self.add_view(WorldSelectView())

        # Load daily pulse views and decision views
        import aiosqlite
        import json
        import os
        if os.path.exists("data/nexus.db"):
            try:
                async with aiosqlite.connect("data/nexus.db") as db:
                    cursor = await db.execute("SELECT id, options_json FROM daily_pulse WHERE is_closed = 0")
                    rows = await cursor.fetchall()
                    from cogs.daily_cog import DailyPulseView
                    for pulse_id, options_json in rows:
                        options = json.loads(options_json)
                        self.add_view(DailyPulseView(pulse_id, options))

                    # Also load collective decision views
                    d_cursor = await db.execute("SELECT id, options_json FROM collective_decisions WHERE is_active = 1")
                    d_rows = await d_cursor.fetchall()
                    from cogs.social_cog import DecisionVoteView
                    for decision_id, options_json in d_rows:
                        options = json.loads(options_json)
                        self.add_view(DecisionVoteView(decision_id, options))
            except Exception as e:
                print(f"Error loading persistent views: {e}")

        # Load cogs here
        await self.load_extension("cogs.event_cog")
        await self.load_extension("cogs.solo_cog")
        await self.load_extension("cogs.profile_cog")
        await self.load_extension("cogs.admin_cog")
        await self.load_extension("cogs.personality_cog")
        await self.load_extension("cogs.npc_cog")
        await self.load_extension("cogs.setup_cog")
        await self.load_extension("cogs.daily_cog")
        await self.load_extension("cogs.challenge_cog")
        await self.load_extension("cogs.social_cog")
        await self.load_extension("cogs.stats_cog")

        # Sync commands
        from core.config import GUILD_ID
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Synced commands to guild {GUILD_ID}")
        else:
            await self.tree.sync()
            print("Synced global commands")

        print("Bot setup complete. Commands loaded.")

    async def on_application_command_error(self, interaction: discord.Interaction, error):
        msg = "⚠️ حدث خطأ غير متوقع، يرجى المحاولة لاحقاً."
        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception:
            pass
        import traceback
        print(f"[ERROR] {traceback.format_exc()}")

    async def on_ready(self):
        print(f"Logged in as {self.user.name} (ID: {self.user.id})")
        print("Ready to run interactive stories!")