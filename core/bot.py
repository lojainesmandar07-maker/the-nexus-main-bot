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
        self.event_manager = EventManager(self, self.story_manager)

    async def setup_hook(self):
        # Re-register persistent views BEFORE loading cogs
        from ui.listing_view import SoloLibraryView, MultiLibraryView
        self.add_view(SoloLibraryView({}, timeout=None))
        self.add_view(MultiLibraryView({}, timeout=None))

        # Load cogs here
        await self.load_extension("cogs.event_cog")
        await self.load_extension("cogs.solo_cog")
        await self.load_extension("cogs.profile_cog")
        await self.load_extension("cogs.admin_cog")
        await self.load_extension("cogs.personality_cog")
        await self.load_extension("cogs.npc_cog")

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