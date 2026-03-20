import discord
from discord import app_commands
from discord.ext import commands
from core.bot import StoryBot
from core.config_manager import get_config

class TestAnswerButton(discord.ui.Button):
    def __init__(self, label: str, custom_id: str, choice_data: dict, parent_view: "TestView"):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=custom_id
        )
        self.choice_data = choice_data
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        await self.parent_view.process_answer(interaction, self.choice_data)

class TestView(discord.ui.View):
    def __init__(self, bot: StoryBot, questions: list, user_id: int):
        # We attach user_id to custom_id to ensure only the test-taker can click
        # Since state (scores, current_q) is in memory, true deep persistence for tests mid-way
        # isn't entirely practical across bot restarts without a database table.
        # But we format it to allow basic stateless recreation if needed, or simply let it expire.
        super().__init__(timeout=None)
        self.bot = bot
        self.questions = questions
        self.user_id = user_id
        self.current_q = 0
        self.scores = {
            "strategist": 0, "guardian": 0, "shadow": 0, "rebel": 0,
            "seeker": 0, "warrior": 0, "oracle": 0, "wanderer": 0
        }
        self._update_buttons()

    def _update_buttons(self):
        self.clear_items()
        if self.current_q >= len(self.questions):
            return

        q_data = self.questions[self.current_q]
        for i, choice in enumerate(q_data["choices"]):
            # Note: We include user_id in the custom_id to tie the state to the user temporarily.
            custom_id = f"rpg_test_{self.user_id}_q{self.current_q}_c{i}"
            btn = TestAnswerButton(
                label=choice["text"],
                custom_id=custom_id,
                choice_data=choice,
                parent_view=self
            )
            self.add_item(btn)

    def _build_embed(self) -> discord.Embed:
        q_data = self.questions[self.current_q]
        embed = discord.Embed(
            title=f"السؤال {self.current_q + 1} من {len(self.questions)}",
            description=q_data["text"],
            color=0x2E4057
        )
        return embed

    async def process_answer(self, interaction: discord.Interaction, choice_data: dict):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("هذا الاختبار ليس لك.", ephemeral=True)
            return

        archetype = choice_data.get("archetype")
        if archetype in self.scores:
            self.scores[archetype] += 1

        self.current_q += 1
        if self.current_q < len(self.questions):
            self._update_buttons()
            await interaction.response.edit_message(
                embed=self._build_embed(),
                view=self
            )
        else:
            await self._finish_test(interaction)

    async def _finish_test(self, interaction: discord.Interaction):
        # Determine highest score
        winner = max(self.scores, key=self.scores.get)

        archetype_names = {
            "strategist": "المخطط", "guardian": "الحارس", "shadow": "الظل",
            "rebel": "المتمرد", "seeker": "الباحث", "warrior": "المحارب",
            "oracle": "العرّاف", "wanderer": "التائه"
        }

        winner_name = archetype_names.get(winner, winner)

        embed = discord.Embed(
            title="🎯 اكتمل الاختبار!",
            description=f"لقد تم تحديد شخصيتك بناءً على قراراتك.\n\nأنت: **{winner_name}**",
            color=discord.Color.gold()
        )

        # Try to assign role
        roles_config = get_config("archetype_roles", {})
        role_id = roles_config.get(winner)

        msg = "تم تحديد شخصيتك بنجاح."

        if role_id:
            role = interaction.guild.get_role(role_id)
            if role:
                try:
                    await interaction.user.add_roles(role)
                    msg += f" وتم منحك رتبة {role.mention}."
                except Exception as e:
                    print(f"Failed to add role {role_id}: {e}")
                    msg += " ولكن تعذر إعطاء الرتبة (تأكد من صلاحيات البوت)."
            else:
                 msg += " ولكن الرتبة المخصصة غير موجودة في السيرفر."

        await interaction.response.edit_message(content=msg, embed=embed, view=None)


class TestCog(commands.Cog):
    def __init__(self, bot: StoryBot):
        self.bot = bot

    @app_commands.command(name="اختبار-الشخصية", description="ابدأ اختبار الشخصية التفاعلي لتحديد مسارك")
    async def start_test(self, interaction: discord.Interaction):
        test_channel_id = get_config("test_channel")
        if test_channel_id and interaction.channel_id != test_channel_id:
            await interaction.response.send_message(f"❌ هذا الأمر مخصص لقناة <#{test_channel_id}> فقط.", ephemeral=True)
            return

        # In Phase 2, this will load from a real JSON file. For now, we use a placeholder dict.
        dummy_questions = [
            {
                "text": "وجدت خريطة لكنز في مكتبة قديمة — ماذا تفعل؟",
                "choices": [
                    {"text": "أدرسها جيداً قبل التحرك", "archetype": "strategist"},
                    {"text": "أخفيها حتى لا تقع في أيدٍ شريرة", "archetype": "guardian"},
                    {"text": "أتبعها فوراً بدافع الفضول", "archetype": "seeker"},
                    {"text": "أحرقها لكسر لعنتها", "archetype": "rebel"}
                ]
            },
            {
                "text": "صديقك المقرب محاصر في معركة خاسرة — كيف تتصرف؟",
                "choices": [
                    {"text": "أندفع لإنقاذه بسيفي", "archetype": "warrior"},
                    {"text": "أراقبه وأتدخل في اللحظة الحاسمة", "archetype": "shadow"},
                    {"text": "أقرأ مستقبله لأعرف ما سيحدث", "archetype": "oracle"},
                    {"text": "أساعده ثم أرحل بصمت", "archetype": "wanderer"}
                ]
            }
        ]

        view = TestView(self.bot, dummy_questions, interaction.user.id)
        embed = view._build_embed()

        intro_embed = discord.Embed(
            title="🧪 اختبار الشخصية",
            description="أجب على الأسئلة القادمة بصدق. قراراتك ستحدد من أنت في هذا العالم.",
            color=0x2E4057
        )

        await interaction.response.send_message(embed=intro_embed, ephemeral=True)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

async def setup(bot: StoryBot):
    await bot.add_cog(TestCog(bot))
