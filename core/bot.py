import traceback
import discord
from discord import app_commands
from discord.ext import commands
from engine.story_manager import StoryManager
from engine.event_manager import EventManager
from core.db import init_db
from ui.listing_view import MultiLibraryView, SoloLibraryView
from ui.solo_view import SoloView
from ui.views import VotingView
from core.config_manager import get_config

# Define a custom view store logic or adapt existing logic if needed for persistent views
# Here, we will just use standard discord.py functionality to keep views persistent

class StoryBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True # Required for reading member.roles dynamically

        # This bot currently uses slash/app commands only.
        # Using mention-only prefix avoids requiring privileged message content intent.
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

        self.story_manager = StoryManager()
        self.event_manager = EventManager(self, self.story_manager)

        # Setup global error handler
        self.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Global error handler for slash commands."""
        traceback.print_exception(type(error), error, error.__traceback__)
        try:
            error_msg = "حدث خطأ غير متوقع، يرجى المحاولة لاحقاً."
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)
        except Exception as e:
            print(f"Failed to send error message: {e}")

    async def setup_hook(self):
        # Initialize Database
        await init_db()
        print("Database initialized.")

        # Load cogs here
        await self.load_extension("cogs.event_cog")
        await self.load_extension("cogs.solo_cog")

        # New Cogs
        cogs_to_load = [
            "cogs.admin_cog",
            "cogs.world_cog",
            "cogs.test_cog",
            "cogs.npc_cog",
            "cogs.profile_cog"
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")

        # Re-register persistent views
        try:
            from collections import defaultdict
            from ui.listing_view import SoloCategorySelectView, WorldCategorySelectView
            from cogs.npc_cog import NPCTalkView, NPCTopicView

            # 1. World category views (need to reconstruct with their categories and world id)
            world_categories_data = {}
            for world in ["fantasy", "past", "future", "alternate"]:
                stories = [s for s in self.story_manager.get_all_stories().values() if s.game_mode == "single" and getattr(s, 'world_type', world) == world]
                categories = defaultdict(list)
                for s in stories:
                    categories[s.theme].append(s)
                if categories:
                    self.add_view(WorldCategorySelectView(categories, world))

            # 2. Solo category views
            solo_stories = self.story_manager.get_stories_by_mode("single")
            solo_categories = defaultdict(list)
            for s in solo_stories.values():
                solo_categories[s.theme].append(s)
            if solo_categories:
                self.add_view(SoloCategorySelectView(solo_categories))

            # 3. NPC Views
            # We can re-register them by looking at what's in the config
            npc_channels = get_config("npc_channels", {})
            for npc_id in npc_channels.keys():
                self.add_view(NPCTalkView(npc_id))
                self.add_view(NPCTopicView(npc_id))

            # MultiLibrary and SoloLibrary are handled differently if they don't have custom IDs yet,
            # but if they have static custom ids they could be registered here.
            # Currently the dynamic views (StorySelect, PerspectiveSelect) rely on custom IDs parsed
            # dynamically or fallback logic that is natively handled if they subclass Button/Select
            # and set custom_id manually without timeout, but discord.py requires the View to be added
            # for the components to route correctly.
            # For deeper dynamic component routing without creating 1000s of views, we use a global fallback.

            print("Registered persistent views.")
        except Exception as e:
            print(f"Error registering persistent views: {e}")

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

    async def on_ready(self):
        print(f"Logged in as {self.user.name} (ID: {self.user.id})")
        print("Ready to run interactive stories!")