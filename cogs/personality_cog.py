import discord
from discord import app_commands
from discord.ext import commands
import json
import aiosqlite
from core.config import get_config, load_config

DB_PATH = "data/nexus.db"
TEST_PATH = "data/personality_test.json"


def load_test_data() -> dict:
    with open(TEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class QuestionView(discord.ui.View):
    """Shows one question with choice buttons. Calls back to the test session when answered."""

    def __init__(self, question: dict, session: "TestSession", question_index: int):
        super().__init__(timeout=300)
        self.question = question
        self.session = session
        self.question_index = question_index

        for i, choice in enumerate(question["choices"]):
            emoji = choice.get("emoji", "")
            label = f"{emoji} {choice['label']}"[:80]
            btn = discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.primary,
                custom_id=f"q_{question_index}_c_{i}"
            )
            btn.callback = self._make_callback(choice["scores"])
            self.add_item(btn)

    def _make_callback(self, scores: dict):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.session.user_id:
                await interaction.response.send_message("❌ هذا الاختبار ليس لك!", ephemeral=True)
                return

            # Disable all buttons after selection
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)

            # Add scores
            for arch, pts in scores.items():
                self.session.scores[arch] = self.session.scores.get(arch, 0) + pts

            # Advance to next question
            await self.session.next_question(interaction)

        return callback

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.session.cancel("⏰ انتهت مهلة الاختبار. يمكنك البدء من جديد بأمر /اختبار_الشخصية")
        except Exception:
            pass


class TestSession:
    """Tracks one user's test progress."""

    def __init__(self, user_id: int, questions: list, archetypes: dict, followup, cog: "PersonalityCog"):
        self.user_id = user_id
        self.questions = questions
        self.archetypes = archetypes
        self.followup = followup  # interaction.followup for sending next questions
        self.cog = cog
        self.scores: dict = {arch: 0 for arch in archetypes}
        self.current_index = 0
        self.cancelled = False

    async def next_question(self, interaction: discord.Interaction):
        self.current_index += 1

        if self.current_index >= len(self.questions):
            await self.show_result(interaction)
            return

        q = self.questions[self.current_index]
        view = QuestionView(q, self, self.current_index)
        embed = discord.Embed(
            title=f"❓ السؤال {self.current_index + 1} من {len(self.questions)}",
            description=q["text"],
            color=0x2E4057
        )
        embed.set_footer(text="اختر إجابتك — لديك 5 دقائق")
        await self.followup.send(embed=embed, view=view, ephemeral=True)

    async def show_result(self, interaction: discord.Interaction):
        try:
            # Find winning archetype
            winner = max(self.scores, key=lambda k: self.scores[k])
            archetype_data = self.archetypes.get(winner, {})

            color_str = archetype_data.get("color", "0x2E4057")
            try:
                color = int(color_str, 16)
            except Exception:
                color = 0x2E4057

            embed = discord.Embed(
                title=f"✨ نتيجة اختبارك: {archetype_data.get('name', winner)}",
                description=archetype_data.get("description", ""),
                color=color
            )
            embed.set_footer(text="تم تحديد شخصيتك — ستُمنح الرتبة المناسبة تلقائياً")
            await self.followup.send(embed=embed, ephemeral=True)

            # Assign role
            await self._assign_role(interaction, winner)

            # Update DB
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute("""
                        INSERT INTO players (user_id) VALUES (?)
                        ON CONFLICT(user_id) DO NOTHING
                    """, (self.user_id,))
                    await db.commit()
            except Exception:
                pass
        finally:
            self.cog.active_tests.pop(self.user_id, None)

    async def _assign_role(self, interaction: discord.Interaction, archetype_key: str):
        archetype_roles = get_config("archetype_roles", {})
        role_id = archetype_roles.get(archetype_key)
        if not role_id:
            await self.followup.send(
                "⚠️ لم يتم إعداد الرتب بعد. تواصل مع المشرفين.",
                ephemeral=True
            )
            return

        guild = interaction.guild
        member = guild.get_member(self.user_id) or await guild.fetch_member(self.user_id)
        role = guild.get_role(int(role_id))

        if not role:
            return

        # Remove all other archetype roles first
        other_ids = {int(v) for k, v in archetype_roles.items() if k != archetype_key and v}
        to_remove = [r for r in member.roles if r.id in other_ids]
        for r in to_remove:
            try:
                await member.remove_roles(r)
            except Exception:
                pass

        # Assign new role
        try:
            await member.add_roles(role)
            await self.followup.send(
                f"✅ تم منحك رتبة **{role.name}** بنجاح!", ephemeral=True
            )
        except discord.Forbidden:
            await self.followup.send(
                "⚠️ لا يملك البوت صلاحية منح الرتب. تواصل مع المشرفين.",
                ephemeral=True
            )

    async def cancel(self, message: str):
        self.cancelled = True
        try:
            await self.followup.send(message, ephemeral=True)
        except Exception:
            pass
        finally:
            self.cog.active_tests.pop(self.user_id, None)


class PersonalityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tests: dict = {}  # user_id -> TestSession

    @app_commands.command(name="اختبار_الشخصية", description="اكتشف شخصيتك في عالم The Nexus")
    async def personality_test(self, interaction: discord.Interaction):
        # Check if user already has an archetype role
        archetype_roles = get_config("archetype_roles", {})
        role_to_arch = {int(v): k for k, v in archetype_roles.items() if v}
        member_role_ids = [r.id for r in interaction.user.roles]
        existing = next((role_to_arch[rid] for rid in member_role_ids if rid in role_to_arch), None)

        if existing:
            from cogs.profile_cog import ARCHETYPE_NAMES
            arch_name = ARCHETYPE_NAMES.get(existing, existing)
            embed = discord.Embed(
                title="🧬 لديك شخصية بالفعل",
                description=f"شخصيتك الحالية هي: **{arch_name}**\n\nهل تريد إعادة الاختبار وتغيير شخصيتك؟",
                color=0x2E4057
            )
            view = RetestConfirmView(interaction.user.id, self)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return

        await self._start_test(interaction)

    async def _start_test(self, interaction: discord.Interaction):
        """Begin the test — send intro then first question."""
        if interaction.user.id in self.active_tests:
            await interaction.response.send_message(
                "⚠️ لديك اختبار نشط بالفعل. أكمله أو انتظر انتهاء مهلته.",
                ephemeral=True
            )
            return

        test_data = load_test_data()
        questions = test_data["questions"]
        archetypes = test_data["archetypes"]

        # Send intro embed
        intro_embed = discord.Embed(
            title="🌀 اختبار تحديد الشخصية",
            description=(
                "ستُجيب على **25 سؤالاً** تكشف شخصيتك الحقيقية في عالم The Nexus.\n\n"
                "لا توجد إجابات صح أو غلط — اختر ما يعبّر عنك أكثر.\n"
                "كل سؤال له مهلة 5 دقائق."
            ),
            color=0x2E4057
        )
        intro_embed.set_footer(text="السؤال الأول سيظهر تلقائياً...")
        await interaction.response.send_message(embed=intro_embed, ephemeral=True)

        # Create session
        session = TestSession(
            user_id=interaction.user.id,
            questions=questions,
            archetypes=archetypes,
            followup=interaction.followup,
            cog=self,
        )
        self.active_tests[interaction.user.id] = session

        # Send first question
        q = questions[0]
        view = QuestionView(q, session, 0)
        embed = discord.Embed(
            title=f"❓ السؤال 1 من {len(questions)}",
            description=q["text"],
            color=0x2E4057
        )
        embed.set_footer(text="اختر إجابتك — لديك 5 دقائق")
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class RetestConfirmView(discord.ui.View):
    """Confirms user wants to retake the test."""

    def __init__(self, user_id: int, cog: PersonalityCog):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.cog = cog

    @discord.ui.button(label="نعم، أعد الاختبار", style=discord.ButtonStyle.danger,
                       custom_id="retest_confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس اختبارك!", ephemeral=True)
            return
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        await self.cog._start_test(interaction)

    @discord.ui.button(label="لا، إبقَ على شخصيتي", style=discord.ButtonStyle.secondary,
                       custom_id="retest_cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس اختبارك!", ephemeral=True)
            return
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="تم الإلغاء. شخصيتك لم تتغير.", view=self
        )


async def setup(bot):
    await bot.add_cog(PersonalityCog(bot))
