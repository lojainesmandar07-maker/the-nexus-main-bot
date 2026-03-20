import discord
from typing import List
from engine.models import Choice


class SoloChoiceButton(discord.ui.Button):
    def __init__(self, choice: Choice, index: int, solo_manager, user_id: int):
        style_map = {
            "secondary": discord.ButtonStyle.secondary,
            "success": discord.ButtonStyle.success,
            "danger": discord.ButtonStyle.danger,
        }
        style = style_map.get(choice.color, discord.ButtonStyle.primary)
        super().__init__(
            label=choice.text[:80],
            style=style,
            custom_id=f"solo_{user_id}_{index}"
        )
        self.choice_index = index
        self.solo_manager = solo_manager
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا الخيار ليس لك!", ephemeral=True)
            return

        session, error = self.solo_manager.process_choice(self.user_id, self.choice_index)

        if error:
            from ui.embeds import EmbedBuilder
            await interaction.response.send_message(
                embed=EmbedBuilder.error_embed(error), ephemeral=True
            )
            return

        from ui.embeds import EmbedBuilder
        story = session["story"]
        scene = session["scene"]
        points = session["points"]
        round_number = session["round"]

        embed = EmbedBuilder.solo_scene_embed(scene, round_number, story.title, points)

        view = None
        if not scene.is_ending and scene.choices:
            view = SoloView(self.solo_manager, self.user_id, scene.choices)
        else:
            self.solo_manager.end_solo_game(self.user_id)
            # Notify profile system of completion
            try:
                from cogs.profile_cog import on_story_complete
                await on_story_complete(self.user_id, interaction.channel)
            except Exception:
                pass

        await interaction.response.edit_message(embed=embed, view=view)


class SoloView(discord.ui.View):
    def __init__(self, solo_manager, user_id: int, choices: List[Choice]):
        super().__init__(timeout=600)
        self.solo_manager = solo_manager
        self.user_id = user_id

        for idx, choice in enumerate(choices):
            self.add_item(SoloChoiceButton(choice, idx, solo_manager, user_id))