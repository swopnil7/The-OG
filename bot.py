import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from discord import app_commands
import json
import os
import random
import datetime
import pathlib
import matplotlib.pyplot as plt

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_ROOT = "guild_data"

def get_guild_folder(guild_id):
    folder = os.path.join(DATA_ROOT, str(guild_id))
    os.makedirs(folder, exist_ok=True)
    return folder

def get_guild_file(guild_id, filename):
    return os.path.join(get_guild_folder(guild_id), filename)

def load_json_file(filepath, default=None):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    return default if default is not None else {}

def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def load_game_data(guild_id):
    return load_json_file(get_guild_file(guild_id, "game_usernames.json"), default={})

def save_game_data(guild_id, game_usernames):
    save_json_file(get_guild_file(guild_id, "game_usernames.json"), game_usernames)

def load_routine_data(guild_id):
    return load_json_file(get_guild_file(guild_id, "class_routine.json"), default={})

def save_routine_data(guild_id, class_routine):
    save_json_file(get_guild_file(guild_id, "class_routine.json"), class_routine)

def load_activity_data(guild_id):
    return load_json_file(get_guild_file(guild_id, "activity_data.json"), default={})

def save_activity_data(guild_id, activity_data):
    save_json_file(get_guild_file(guild_id, "activity_data.json"), activity_data)

def load_voice_activity_data(guild_id):
    return load_json_file(get_guild_file(guild_id, "voice_activity_data.json"), default={})

def save_voice_activity_data(guild_id, activity_data):
    save_json_file(get_guild_file(guild_id, "voice_activity_data.json"), activity_data)

# These will be set per-guild in each command/event
# Example: game_usernames[guild_id] = load_game_data(guild_id)
game_usernames = {}
class_routine = {}
activity_data = {}
voice_activity_data = {}

# Helper to get and cache per-guild data
def ensure_guild_data(guild_id):
    if guild_id not in game_usernames:
        game_usernames[guild_id] = load_game_data(guild_id)
    if guild_id not in class_routine:
        class_routine[guild_id] = load_routine_data(guild_id)
    if guild_id not in activity_data:
        activity_data[guild_id] = load_activity_data(guild_id)
    if guild_id not in voice_activity_data:
        voice_activity_data[guild_id] = load_voice_activity_data(guild_id)

def format_routine_table(day: str, schedule: str) -> str:
    rows = schedule.split(", ")
    table = f"**{day.capitalize()} Routine:**\n"
    for idx, subject in enumerate(rows, 1):
        table += f"**Period {idx}:** {subject}\n"
    return table

def format_weekly_routine_table(routine: dict) -> str:
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    lines = []
    for day in days:
        schedule = routine.get(day.lower(), "")
        periods = schedule.split(", ")
        while len(periods) < 4:
            periods.append("")
        lines.append(f"{day}:")
        for period_idx, subj in enumerate(periods):
            sub_subjects = [s.strip() for s in subj.split("/") if s.strip()]
            if sub_subjects:
                lines.append(f"  Period {period_idx+1}: {sub_subjects[0]}")
                for mini_subj in sub_subjects[1:]:
                    lines.append(f"      {mini_subj}")
            else:
                lines.append(f"  Period {period_idx+1}: ")
            if period_idx < 3:
                lines.append("  --------")
        lines.append("")
    result = '```' + '\n'.join(lines).strip() + '```'
    return result

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_guild_join(guild):
    ensure_guild_data(guild.id)

@bot.event
async def on_guild_available(guild):
    ensure_guild_data(guild.id)


@bot.tree.command(name="addgame", description="Add or update a game username for a user")
@app_commands.describe(game_name="The name of the game", username="Your username in the game", member="The user to add the game for (optional)")
async def add_game(interaction: discord.Interaction, game_name: str, username: str, member: discord.User = None):
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)

    if not member:
        member = interaction.user

    if not interaction.user.guild_permissions.administrator and member != interaction.user:
        await interaction.response.send_message("You do not have permission to add usernames for other users.", ephemeral=True)
        return

    user_id = str(member.id)
    game_name = game_name.lower()

    if game_name not in game_usernames[guild_id]:
        game_usernames[guild_id][game_name] = {}
    game_usernames[guild_id][game_name][user_id] = username
    save_game_data(guild_id, game_usernames[guild_id])
    await interaction.response.send_message(f"Added/Updated username for {member.name} in game '{game_name}'.")

@bot.tree.command(name="view", description="View all registered usernames of a specific game")
@app_commands.describe(game_name="The name of the game to view usernames for")
async def view_usernames(interaction: discord.Interaction, game_name: str):
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)

    game_name = game_name.lower()

    if game_name not in game_usernames[guild_id] or not game_usernames[guild_id][game_name]:
        await interaction.response.send_message(f"No usernames found for game '{game_name}'.")
        return

    response = f"Usernames for game '{game_name}':\n"
    for user_id, username in game_usernames[guild_id][game_name].items():
        user = await bot.fetch_user(int(user_id))
        response += f"- {user.name}: {username}\n"
    await interaction.response.send_message(response)

@bot.tree.command(name="games", description="List all games with usernames")
async def list_games(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)

    if not game_usernames[guild_id]:
        await interaction.response.send_message("No games have been added yet.")
        return

    response = "Games with usernames:\n"
    for game in game_usernames[guild_id].keys():
        response += f"• {game}\n"
    await interaction.response.send_message(response)

@bot.tree.command(name="viewuser", description="View all usernames registered for a user across all games")
@app_commands.describe(member="The user to view the usernames of")
async def view_user_usernames(interaction: discord.Interaction, member: discord.User):
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)
    user_id = str(member.id)
    user_games = [
        (game, users[user_id])
        for game, users in game_usernames[guild_id].items()
        if user_id in users
    ]

    if not user_games:
        await interaction.response.send_message(f"{member.name} does not have any usernames registered.")
        return

    response = f"Usernames for {member.name}:\n"
    for game, username in user_games:
        response += f"- {game}: {username}\n"
    await interaction.response.send_message(response)

@bot.tree.command(name="routineday", description="View the class routine for a specific day")
@app_commands.describe(day="Day of the week (e.g., sunday, monday, ...)")
async def routine_day(interaction: discord.Interaction, day: str):
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)
    day_lower = day.lower()
    valid_days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday"]
    if day_lower not in valid_days:
        await interaction.response.send_message(
            "Invalid day. Please choose from: Sunday, Monday, Tuesday, Wednesday, Thursday, Friday.",
            ephemeral=True
        )
        return
    schedule = class_routine[guild_id].get(day_lower, "No routine found.")
    table = format_routine_table(day.capitalize(), schedule)
    await interaction.response.send_message(table)

@bot.tree.command(name="routineweek", description="View the entire week's class routine as text.")
async def routineweek_slash(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)
    table = format_weekly_routine_table(class_routine[guild_id])
    await interaction.response.send_message(table, ephemeral=True)

@bot.tree.command(name="changeday", description="Change the routine for a specific day")
@app_commands.describe(day="Day of the week (e.g., sunday, monday, ...)", schedule="The new schedule for the day")
async def change_day(interaction: discord.Interaction, day: str, schedule: str):
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)
    valid_days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday"]
    day_lower = day.lower()
    if day_lower not in valid_days:
        await interaction.response.send_message(
            "Invalid day. Please choose from: Sunday, Monday, Tuesday, Wednesday, Thursday, Friday.",
            ephemeral=True
        )
        return
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to modify the routine.", ephemeral=True)
        return
    class_routine[guild_id][day_lower] = schedule
    save_routine_data(guild_id, class_routine[guild_id])
    await interaction.response.send_message(f"{day.capitalize()}'s routine updated successfully!")

PROMOTIONS = {
    "The Boys": ("The Men", 102),
    "The Girls": ("The Ladies", 102),
    "The Men": ("The Patriarchs", 400),
    "The Ladies": ("The Matriarchs", 400),
}

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    guild_id = message.guild.id
    ensure_guild_data(guild_id)
    user_id = str(message.author.id)

    if user_id not in activity_data[guild_id]:
        activity_data[guild_id][user_id] = {"messages": 0}

    activity_data[guild_id][user_id]["messages"] += 1
    save_activity_data(guild_id, activity_data[guild_id])

    await check_promotion(message.author, message.guild, guild_id)
    await bot.process_commands(message)

async def check_promotion(member, guild, guild_id):
    """Check if a user qualifies for promotion."""
    user_id = str(member.id)
    user_activity = activity_data[guild_id].get(user_id, {})
    message_count = user_activity.get("messages", 0)

    roles_channel = guild.get_channel(1309835417570377728)
    if not roles_channel:
        print("Roles channel not found.")
        return

    for current_role_name, (new_role_name, threshold) in PROMOTIONS.items():
        current_role = discord.utils.get(guild.roles, name=current_role_name)
        new_role = discord.utils.get(guild.roles, name=new_role_name)

        if current_role in member.roles and message_count >= threshold:
            await member.remove_roles(current_role)
            await member.add_roles(new_role)
            await roles_channel.send(
                f"🎉 Congratulations {member.mention}! You've been promoted to **{new_role_name}**!"
            )

@bot.tree.command(name="activity", description="View activity stats for a user.")
@app_commands.describe(member="The user to view activity stats for (optional)")
async def activity(interaction: discord.Interaction, member: discord.Member = None):
    """View activity stats for a user."""
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)
    member = member or interaction.user
    user_id = str(member.id)
    user_activity = activity_data[guild_id].get(user_id, {"messages": 0})
    await interaction.response.send_message(f"{member.mention} has sent {user_activity['messages']} messages.")

class RPSButton(Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        view: RPSView = self.view
        # Ensure per-guild data is loaded if needed
        if interaction.guild:
            ensure_guild_data(interaction.guild.id)
        if interaction.user in view.choices:
            await interaction.response.send_message("You have already made your choice.", ephemeral=True)
            return
        await view.handle_choice(interaction, self.custom_id)

class RPSView(View):
    def __init__(self, player1, player2=None):
        super().__init__(timeout=60)
        self.player1 = player1
        self.player2 = player2
        self.choices = {}
        self.add_item(RPSButton(label="Rock", custom_id="rock"))
        self.add_item(RPSButton(label="Paper", custom_id="paper"))
        self.add_item(RPSButton(label="Scissors", custom_id="scissors"))

    async def handle_choice(self, interaction: discord.Interaction, choice: str):
        user = interaction.user
        # Ensure per-guild data is loaded if needed
        if interaction.guild:
            ensure_guild_data(interaction.guild.id)
        if user not in [self.player1, self.player2] and self.player2 is not None:
            await interaction.response.send_message("You are not part of this game.", ephemeral=True)
            return

        self.choices[user] = choice
        await interaction.response.send_message(f"You chose {choice}.", ephemeral=True)

        if self.player2:
            if len(self.choices) == 2:
                await self.resolve_game(interaction)
        else:
            await self.resolve_game(interaction)

    async def resolve_game(self, interaction: discord.Interaction):
        # Ensure per-guild data is loaded if needed
        if interaction.guild:
            ensure_guild_data(interaction.guild.id)
        if self.player2:
            p1_choice = self.choices.get(self.player1)
            p2_choice = self.choices.get(self.player2)
            result = self.determine_winner(p1_choice, p2_choice)
            await interaction.followup.send(
                f"{self.player1.mention} chose {p1_choice}, {self.player2.mention} chose {p2_choice}. {result}"
            )
        else:
            p1_choice = self.choices.get(self.player1)
            bot_choice = random.choice(["rock", "paper", "scissors"])
            result = self.determine_winner(p1_choice, bot_choice)
            await interaction.followup.send(
                f"You chose {p1_choice}, I chose {bot_choice}. {result}",
                ephemeral=True
            )

    def determine_winner(self, choice1, choice2):
        if choice1 == choice2:
            return "It's a tie!"
        elif (choice1 == "rock" and choice2 == "scissors") or (choice1 == "paper" and choice2 == "rock") or (choice1 == "scissors" and choice2 == "paper"):
            return f"{self.player1.mention} wins!" if self.player2 else "You win!"
        else:
            return f"{self.player2.mention} wins!" if self.player2 else "You lose!"

@bot.tree.command(name="rps", description="Play Rock-Paper-Scissors (single or multi-player).")
@app_commands.describe(opponent="The user you want to challenge (optional)")
async def rps(interaction: discord.Interaction, opponent: discord.User = None):
    """Play Rock-Paper-Scissors (single or multi-player)"""
    if interaction.guild:
        ensure_guild_data(interaction.guild.id)
    if opponent and opponent == interaction.user:
        await interaction.response.send_message("You cannot challenge yourself.", ephemeral=True)
        return
    if opponent:
        view = RPSView(player1=interaction.user, player2=opponent)
        await interaction.response.send_message(
            f"{opponent.mention}, you have been challenged to a game of Rock-Paper-Scissors! Choose your move:",
            view=view
        )
    else:
        view = RPSView(player1=interaction.user)
        await interaction.response.send_message("Choose your move:", view=view, ephemeral=True)

class FlipButton(Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        view: FlipView = self.view
        # Ensure per-guild data is loaded if needed
        if interaction.guild:
            ensure_guild_data(interaction.guild.id)
        # Prevent double choice
        if interaction.user in view.choices:
            await interaction.response.send_message("You have already made your choice.", ephemeral=True)
class FlipView(View):
    def __init__(self, player1, player2=None):
        super().__init__(timeout=60)
        self.player1 = player1
        self.player2 = player2
        self.choices = {}
        self.add_item(FlipButton(label="Heads", custom_id="heads"))
        self.add_item(FlipButton(label="Tails", custom_id="tails"))

    async def handle_choice(self, interaction: discord.Interaction, choice: str):
        user = interaction.user
        # Ensure per-guild data is loaded if needed
        if interaction.guild:
            ensure_guild_data(interaction.guild.id)
        if user not in [self.player1, self.player2]:
            await interaction.response.send_message("You are not part of this game.", ephemeral=True)
            return

        self.choices[user] = choice
        await interaction.response.send_message(f"You chose {choice}.", ephemeral=True)

        if self.player2:
            if len(self.choices) == 2:
                await self.resolve_game(interaction)
        else:
            await self.resolve_game(interaction)

    async def resolve_game(self, interaction: discord.Interaction):
        coin_result = random.choice(["heads", "tails"])
        if self.player2:
            p1_choice = self.choices.get(self.player1)
            p2_choice = self.choices.get(self.player2)
            result = self.determine_winner(p1_choice, p2_choice, coin_result)
            await interaction.followup.send(f"The coin landed on {coin_result}. {result}")
        else:
            p1_choice = self.choices.get(self.player1)
            result = "You win!" if p1_choice == coin_result else "You lose!"
            await interaction.followup.send(f"The coin landed on {coin_result}. {result}", ephemeral=True)

    def determine_winner(self, choice1, choice2, coin_result):
        if choice1 == coin_result and choice2 == coin_result:
            return "It's a tie!"
        elif choice1 == coin_result:
            return f"{self.player1.mention} wins!"
        elif choice2 == coin_result:
            return f"{self.player2.mention} wins!"
        else:
            return "No one wins!"

@bot.tree.command(name="flip", description="Play Heads or Tails (single or multi-player).")
@app_commands.describe(opponent="The user you want to challenge (optional)")
async def flip_slash(interaction: discord.Interaction, opponent: discord.User = None):
    guild_id = interaction.guild.id if interaction.guild else None
    if guild_id:
        ensure_guild_data(guild_id)
    if opponent and opponent == interaction.user:
        await interaction.response.send_message("You cannot challenge yourself.", ephemeral=True)
        return
    if opponent:
        view = FlipView(player1=interaction.user, player2=opponent)
        await interaction.response.send_message(
            f"{opponent.mention}, you have been challenged to a game of Heads or Tails! Choose your side:",
            view=view
        )
    else:
        view = FlipView(player1=interaction.user)
        await interaction.response.send_message("Choose Heads or Tails:", view=view, ephemeral=True)

@bot.event
async def on_voice_state_update(member, before, after):
    guild_id = member.guild.id
    ensure_guild_data(guild_id)
    vad = voice_activity_data[guild_id]

    if before.channel is None and after.channel is not None:
        if "voice_log" not in vad:
            vad["voice_log"] = {}
        if str(after.channel.id) not in vad["voice_log"]:
            vad["voice_log"][str(after.channel.id)] = []
        vad["voice_log"][str(after.channel.id)].append({
            "user": member.name,
            "action": "joined",
            "timestamp": str(discord.utils.utcnow() + datetime.timedelta(hours=0, minutes=0))
        })
    elif before.channel is not None and after.channel is None:
        if "voice_log" not in vad:
            vad["voice_log"] = {}
        if str(before.channel.id) not in vad["voice_log"]:
            vad["voice_log"][str(before.channel.id)] = []
        vad["voice_log"][str(before.channel.id)].append({
            "user": member.name,
            "action": "left",
            "timestamp": str(discord.utils.utcnow() + datetime.timedelta(hours=0, minutes=0))
        })
        
        if before.channel.members == []:
            log_channel = member.guild.get_channel(1308408556961136680)
            if log_channel:
                log_entries = vad["voice_log"].pop(str(before.channel.id), [])
                log_message = f"Voice channel '{before.channel.name}' log:\n"
                for entry in log_entries:
                    timestamp = discord.utils.format_dt(discord.utils.parse_time(entry['timestamp']), style='t')
                    log_message += f"{timestamp} - {entry['user']} {entry['action']} the channel.\n"
                await log_channel.send(log_message)
                
    save_voice_activity_data(guild_id, vad)

@bot.tree.command(name="announce", description="Announce a message to a channel (Admin only).")
@app_commands.describe(message="The announcement message", channel="The channel to announce in (optional)")
async def announce_slash(interaction: discord.Interaction, message: str, channel: discord.TextChannel = None):

    guild_id = interaction.guild.id if interaction.guild else None

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need to be an admin to use this command.", ephemeral=True)
        return

    if channel is None:
        channel = interaction.channel

    await channel.send(message)
    await interaction.response.send_message("Announcement sent!", ephemeral=True)


def strip_ab_label(subject):
    # Remove trailing ' (A)' or ' (B)' or '(A)' or '(B)' (with or without space)
    return subject.rstrip().replace(' (A)', '').replace(' (B)', '').replace('(A)', '').replace('(B)', '').strip()

def generate_routine_image(routine, filename="routine.png"):
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods = [f"Period {i}" for i in range(1, 5)]
    data = []
    for day in days:
        schedule = routine.get(day.lower(), "")
        period_cells = []
        for p in schedule.split(", "):
            ab = [s.strip() for s in p.split("/") if s.strip()]
            if len(ab) == 2:
                a = strip_ab_label(ab[0])
                b = strip_ab_label(ab[1])
                period_cells.append(f"A: {a}\nB: {b}")
            elif ab:
                period_cells.append(ab[0])
            else:
                period_cells.append("")
        while len(period_cells) < 4:
            period_cells.append("")
        data.append([day] + period_cells)

    _, ax = plt.subplots(figsize=(11, 4))
    ax.axis('off')
    table = ax.table(
        cellText=data,
        colLabels=["Day"] + periods,
        cellLoc='center',
        loc='center',
        colColours=["#2d415a"] + ["#4f6d7a"]*4
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.6)

    # Style header
    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_fontsize(13)
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2d415a')
        elif row % 2 == 1:
            cell.set_facecolor('#f2f2f2')
        else:
            cell.set_facecolor('#e0e7ef')
        cell.set_linewidth(1.5)
        cell.set_edgecolor('#4f6d7a')
        cell.set_height(0.15)

    plt.title("Weekly Class Routine", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout(pad=2.0)
    plt.savefig(filename, bbox_inches='tight', dpi=200)
    plt.close()

@bot.tree.command(name="routine", description="Get the weekly routine as an image.")
async def routine_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    filename = "routine.png"
    guild_id = interaction.guild.id if interaction.guild else None
    if guild_id:
        ensure_guild_data(guild_id)
        generate_routine_image(class_routine[guild_id], filename)
    else:
        generate_routine_image({}, filename)
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            await interaction.followup.send(file=discord.File(f, filename))
    else:
        await interaction.followup.send("Routine screenshot not found on the server.", ephemeral=True)

def generate_routine_image_pdf(routine, filename="routine.pdf"):
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods = [f"Period {i}" for i in range(1, 5)]
    data = []
    for day in days:
        schedule = routine.get(day.lower(), "")
        period_cells = []
        for p in schedule.split(", "):
            ab = [s.strip() for s in p.split("/") if s.strip()]
            if len(ab) == 2:
                a = strip_ab_label(ab[0])
                b = strip_ab_label(ab[1])
                period_cells.append(f"A: {a}\nB: {b}")
            elif ab:
                period_cells.append(ab[0])
            else:
                period_cells.append("")
        while len(period_cells) < 4:
            period_cells.append("")
        data.append([day] + period_cells)

    _, ax = plt.subplots(figsize=(14, 6))
    ax.axis('off')
    table = ax.table(
        cellText=data,
        colLabels=["Day"] + periods,
        cellLoc='center',
        loc='center',
        colColours=["#2d415a"] + ["#4f6d7a"]*4,
        bbox=[0, 0.08, 1, 0.80]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(15)
    table.scale(1.5, 2.0)

    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_fontsize(16)
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2d415a')
        elif row % 2 == 1:
            cell.set_facecolor('#f2f2f2')
        else:
            cell.set_facecolor('#e0e7ef')
        cell.set_linewidth(1.5)
        cell.set_edgecolor('#4f6d7a')
        cell.set_height(0.18)

    plt.subplots_adjust(top=0.92)
    plt.title("Weekly Class Routine", fontsize=22, fontweight='bold', pad=10)
    plt.tight_layout(pad=1.0)
    plt.savefig(filename, bbox_inches='tight', dpi=250, format='pdf')
    plt.close()

@bot.tree.command(name="routinepdf", description="Get the weekly routine as a styled PDF.")
async def routinepdf_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    filename = "routine.pdf"
    if not interaction.guild:
        await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
        return
    guild_id = interaction.guild.id
    ensure_guild_data(guild_id)
    generate_routine_image_pdf(class_routine[guild_id], filename)
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            await interaction.followup.send(file=discord.File(f, filename))
    else:
        await interaction.followup.send("Routine PDF not found on the server.", ephemeral=True)

class FileModal(Modal, title="Post a File"):
    def __init__(self, filename: str, guild_id: int = None):
        super().__init__()
        self.filename = filename
        self.guild_id = guild_id
        self.content = TextInput(
            label="File Content",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )
        self.add_item(self.content)

    async def on_submit(self, interaction: discord.Interaction):
        # Optionally, you can use self.guild_id here if you want to save per-guild
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(self.content.value)
        with open(self.filename, "rb") as f:
            await interaction.response.send_message(file=discord.File(f, self.filename))
        os.remove(self.filename)

@bot.tree.command(name="postfile", description="Create any extension file with text content.")
@app_commands.describe(filename="The name of the file (with extension)")
async def postfilemodal(interaction: discord.Interaction, filename: str):
    if "/" in filename or "\\" in filename:
        await interaction.response.send_message("Invalid filename.", ephemeral=True)
        return
    guild_id = interaction.guild.id if interaction.guild else None
    await interaction.response.send_modal(FileModal(filename, guild_id=guild_id))

@bot.tree.command(name="helpme", description="Show help for all commands.")
async def helpme_slash(interaction: discord.Interaction):
    help_text = """
**Game Username Commands:**
- `/addgame <game_name> <username> [@user]`: Add or update a username.
- `/view <game_name>`: View usernames for a game.
- `/games`: List all games.
- `/viewuser @user`: View a user's usernames across games.

**Routine Commands:**
- `/routineday <day>`: View routine for a specific day.
- `/routineweek`: View the entire week's routine as text.
- `/changeday <day>`: Modify a day's routine (Admin only).
- `/routine`: Get the weekly routine as an image.
- `/routinepdf`: Get the weekly routine as a styled PDF.

**Activity Commands:**
- `/activity [@user]`: View activity stats for a user.

**Rock-Paper-Scissors Commands:**
- `/rps`: Play a single-player or Multiplayer game of Rock-Paper-Scissors.

**Heads or Tails Commands:**
- `/flip`: Play a single-player or Multiplayer game of Heads or Tails.

**Other Commands:**
- `/announce <#channel> <message>`: Announce a message to a channel (Admin only).
- `/helpme`: Show this help message.
"""
    await interaction.response.send_message(help_text, ephemeral=True)

bot.run(os.getenv("DISCORD_BOT_TOKEN")

# Ensure the bot token is set in the environment variable DISCORD_BOT_TOKEN
# You can set it in your terminal or in a .env file if you're using dotenv.
# Example: export DISCORD_BOT_TOKEN="your_token_here"
# Make sure to install the required libraries:
# pip install -r requirements.txt
# rename bot.py to app.py if you want to deploy it on a server.
# Also, ensure you have the necessary permissions for the bot in your Discord server.
# The bot requires permissions to read messages, send messages, manage roles, and view channels.
# If you want to run this bot, make sure you have a valid Discord bot token and the necessary intents enabled.
# You can create a bot and get the token from the Discord Developer Portal.
# Make sure to handle the bot token securely and not expose it in public repositories.
# You can also modify and add more features and commands to the bot as per your requirements.