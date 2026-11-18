import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

import os
import random
import asyncio

# =========================================================
#                     LOAD ENV
# =========================================================

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID"))

# =========================================================
#                     INTENTS
# =========================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================================================
#                   BOT ADMINS
# =========================================================

bot_admins = set()

# =========================================================
#                    HELPERS
# =========================================================

def is_bot_owner(user_id: int):
    return user_id == BOT_OWNER_ID

def is_bot_admin(user_id: int):
    return user_id in bot_admins

def has_permission(interaction: discord.Interaction):
    return (
        interaction.user.id == interaction.guild.owner_id
        or is_bot_owner(interaction.user.id)
        or is_bot_admin(interaction.user.id)
    )

# =========================================================
#                    READY EVENT
# =========================================================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print("===================================")
    print(f"Logged in as: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("===================================")

# =========================================================
#                       /DMONE
# =========================================================

@bot.tree.command(
    name="dmone",
    description="Send DM to one member"
)
@app_commands.describe(
    user="User to DM",
    message="Message to send"
)
async def dmone(
    interaction: discord.Interaction,
    user: discord.User,
    message: str
):

    if not has_permission(interaction):
        return await interaction.response.send_message(
            "❌ You don't have permission.",
            ephemeral=True
        )

    try:

        await user.send(message)

        await interaction.response.send_message(
            f"✅ DM sent to {user.mention}"
        )

    except Exception as e:

        await interaction.response.send_message(
            f"❌ Failed to send DM.\n{e}"
        )

# =========================================================
#                       /DMALL
# =========================================================

@bot.tree.command(
    name="dmall",
    description="DM all server members"
)
@app_commands.describe(
    message="Message to send"
)
async def dmall(
    interaction: discord.Interaction,
    message: str
):

    if not has_permission(interaction):
        return await interaction.response.send_message(
            "❌ You don't have permission.",
            ephemeral=True
        )

    members = [
        m for m in interaction.guild.members
        if not m.bot
    ]

    total = len(members)

    success = 0
    failed = 0
    processed = 0

    await interaction.response.send_message(
        f"📨 Starting DM Process...\n\n"
        f"Total Members: {total}"
    )

    progress_message = await interaction.original_response()

    for member in members:

        try:

            await member.send(message)

            success += 1

        except:

            failed += 1

        processed += 1

        # LIVE UPDATE
        if processed % 5 == 0 or processed == total:

            await progress_message.edit(
                content=
                f"📨 Sending DMs...\n\n"
                f"✅ Sent: {success}\n"
                f"❌ Failed: {failed}\n"
                f"📊 Progress: {processed}/{total}\n"
                f"⏳ Remaining: {total - processed}"
            )

        # Anti Rate Limit Delay
        await asyncio.sleep(1)

    await progress_message.edit(
        content=
        f"🎉 DMALL FINISHED!\n\n"
        f"✅ Successfully Sent: {success}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total Processed: {total}"
    )

# =========================================================
#                    /DM-DISCORD
# =========================================================

@bot.tree.command(
    name="dm-discord",
    description="DM random members with giveaway embed"
)
@app_commands.describe(
    member_count="Number of random members",
    message="Giveaway message",
    claim_link="Claim server/link",
    embed="Use embed?",
    title="Embed title",
    description="Embed description"
)
async def dm_discord(
    interaction: discord.Interaction,
    member_count: int,
    message: str,
    claim_link: str,
    embed: bool,
    title: str = None,
    description: str = None
):

    if not has_permission(interaction):
        return await interaction.response.send_message(
            "❌ You don't have permission.",
            ephemeral=True
        )

    members = [
        m for m in interaction.guild.members
        if not m.bot
        and m.id != interaction.user.id
    ]

    if len(members) == 0:
        return await interaction.response.send_message(
            "❌ No valid members found."
        )

    random_members = random.sample(
        members,
        min(member_count, len(members))
    )

    total = len(random_members)

    success = 0
    failed = 0
    processed = 0

    await interaction.response.send_message(
        f"🎉 Starting Giveaway DM Process...\n\n"
        f"Target Members: {total}"
    )

    progress_message = await interaction.original_response()

    # BUTTON

    view = discord.ui.View()

    button = discord.ui.Button(
        label="🎉 Claim Prize",
        url=claim_link
    )

    view.add_item(button)

    for member in random_members:

        try:

            # EMBED MODE
            if embed:

                embed_msg = discord.Embed(
                    title=title if title else "🎉 Giveaway Winner!",
                    description=description if description else message,
                    color=discord.Color.orange()
                )

                embed_msg.add_field(
                    name="Prize",
                    value=message,
                    inline=False
                )

                embed_msg.set_footer(
                    text=f"Hosted by {interaction.guild.name}"
                )

                embed_msg.set_thumbnail(
                    url=interaction.guild.icon.url
                    if interaction.guild.icon
                    else None
                )

                await member.send(
                    embed=embed_msg,
                    view=view
                )

            # NORMAL MODE
            else:

                await member.send(
                    f"{message}\n\n{claim_link}"
                )

            success += 1

        except:

            failed += 1

        processed += 1

        # LIVE UPDATE
        if processed % 5 == 0 or processed == total:

            await progress_message.edit(
                content=
                f"🎉 Giveaway DMs Sending...\n\n"
                f"✅ Sent: {success}\n"
                f"❌ Failed: {failed}\n"
                f"📊 Progress: {processed}/{total}\n"
                f"⏳ Remaining: {total - processed}"
            )

        # Anti Rate Limit Delay
        await asyncio.sleep(1)

    await progress_message.edit(
        content=
        f"🎉 GIVEAWAY DM FINISHED!\n\n"
        f"✅ Successfully Sent: {success}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total Processed: {total}"
    )

# =========================================================
#                  /BOTADMIN_ADD
# =========================================================

@bot.tree.command(
    name="botadmin_add",
    description="Add bot admin"
)
@app_commands.describe(
    user="User to add"
)
async def botadmin_add(
    interaction: discord.Interaction,
    user: discord.User
):

    if not is_bot_owner(interaction.user.id):
        return await interaction.response.send_message(
            "❌ Only bot owner can use this.",
            ephemeral=True
        )

    bot_admins.add(user.id)

    await interaction.response.send_message(
        f"✅ {user.mention} added as bot admin."
    )

# =========================================================
#                /BOTADMIN_REMOVE
# =========================================================

@bot.tree.command(
    name="botadmin_remove",
    description="Remove bot admin"
)
@app_commands.describe(
    user="User to remove"
)
async def botadmin_remove(
    interaction: discord.Interaction,
    user: discord.User
):

    if not is_bot_owner(interaction.user.id):
        return await interaction.response.send_message(
            "❌ Only bot owner can use this.",
            ephemeral=True
        )

    bot_admins.discard(user.id)

    await interaction.response.send_message(
        f"❌ {user.mention} removed from bot admin."
    )

# =========================================================
#                      RUN BOT
# =========================================================

bot.run(TOKEN)