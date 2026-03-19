import discord
from typing import List, Dict
from engine.models import Choice

class SoloView(discord.ui.View):
    def __init__(self, solo_manager, user_id: int, choices: List[Choice]):
        super().__init__(timeout=600)  # Long timeout for reading
        self.solo_manager = solo_manager
        self.user_id = user_id

        for idx, choice in enumerate(choices):
            style = discord.ButtonStyle.primary
            if choice.color == "secondary": style = discord.ButtonStyle.secondary
            elif choice.color == "success": style = discord.ButtonStyle.success
            elif choice.color == "danger": style = discord.ButtonStyle.danger

            button = discord.ui.Button(label=choice.text, style=style, custom_id=f"soloc_{idx}")
            button.callback = self.make_callback(idx)
            self.add_item(button)

    def make_callback(self, choice_index: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("هذا الخيار ليس لك!", ephemeral=True)
                return

            # Process the choice
            session, error = self.solo_manager.process_choice(self.user_id, choice_index)

            if error:
                from ui.embeds import EmbedBuilder
                await interaction.response.send_message(embed=EmbedBuilder.error_embed(error), ephemeral=True)
                return

            # Advance to next scene
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
                self.solo_manager.end_solo_game(self.user_id) # Clean up finished game

            # Edit the message to show new scene
            await interaction.response.edit_message(embed=embed, view=view)

        return callback
