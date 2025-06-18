import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import random
import datetime
import matplotlib.pyplot as plt

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GAME_FILE = "game_usernames.json"
ROUTINE_FILE = "class_routine.json"
ACTIVITY_FILE = "activity_data.json"
VOICE_ACTIVITY_FILE = "voice_activity_data.json"

def load_game_data():
    if os.path.exists(GAME_FILE):
        with open(GAME_FILE, "r") as file:
            return json.load(file)
    return {}

def save_game_data():
    with open(GAME_FILE, "w") as file:
        json.dump(game_usernames, file, indent=4)

def load_routine_data():
    if os.path.exists(ROUTINE_FILE):
        with open(ROUTINE_FILE, "r") as file:
            return json.load(file)
    return {
    	"sunday": "AG, OOP, WT, AP",
    	"monday": "AG, OOP, MCA Lab (A)/WT Lab (B), OOP Lab (A)/AP Lab (B)",
    	"tuesday": "OOP, MCA, CT, WT",
    	"wednesday": "AP, AG, AP Lab (A)/OOP Lab(B), MCA",
    	"thursday": " , MCA, WT, AG",
    	"friday": "AP, OOP Lab(A)/AP Lab(B), WT Lab (A)/OOP Lab (B), CT",
    }

def save_routine_data():
    with open(ROUTINE_FILE, "w") as file:
        json.dump(class_routine, file, indent=4)
        
def load_activity_data():
    if os.path.exists(ACTIVITY_FILE):
        with open(ACTIVITY_FILE, "r") as file:
            return json.load(file)
    return {}

def save_activity_data():
    with open(ACTIVITY_FILE, "w") as file:
        json.dump(activity_data, file, indent=4)

def load_voice_activity_data():
    if os.path.exists(VOICE_ACTIVITY_FILE):
        with open(VOICE_ACTIVITY_FILE, "r") as file:
            return json.load(file)
    return {}

def save_voice_activity_data(activity_data):
    with open(VOICE_ACTIVITY_FILE, "w") as file:
        json.dump(activity_data, file, indent=4)
        
game_usernames = load_game_data()
class_routine = load_routine_data()
activity_data = load_activity_data()
voice_activity_data = load_voice_activity_data()

def format_routine_table(day: str, schedule: str) -> str:
    abbreviations = {
        "Digital Logic": "DL",
        "Drawing Practical": "Drawing",
        "Problem Solving Techniques": "PST",
        "Discrete Maths": "DS",
    }

    for full_name, abbr in abbreviations.items():
        schedule = schedule.replace(full_name, abbr)

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

@bot.command(name="addgame")
async def add_game(ctx, game_name: str, username: str, member: discord.User = None):
    if not member:
        member = ctx.author

    if not ctx.author.guild_permissions.administrator and member != ctx.author:
        await ctx.send("You do not have permission to add usernames for other users.")
        return

    user_id = member.id
    game_name = game_name.lower()

    if game_name not in game_usernames:
        game_usernames[game_name] = {}
    game_usernames[game_name][str(user_id)] = username
    save_game_data()
    await ctx.send(f"Added/Updated username for {member.name} in game '{game_name}'.")

@bot.command(name="view")
async def view_usernames(ctx, game_name: str):
    game_name = game_name.lower()

    if game_name not in game_usernames or not game_usernames[game_name]:
        await ctx.send(f"No usernames found for game '{game_name}'.")
        return

    response = f"Usernames for game '{game_name}':\n"
    for user_id, username in game_usernames[game_name].items():
        user = await bot.fetch_user(int(user_id))
        response += f"- {user.name}: {username}\n"
    await ctx.send(response)

@bot.command(name="games")
async def list_games(ctx):
    if not game_usernames:
        await ctx.send("No games have been added yet.")
        return

    response = "Games with usernames:\n"
    for game in game_usernames.keys():
        response += f"• {game}\n"
    await ctx.send(response)

@bot.command(name="viewuser")
async def view_user_usernames(ctx, member: discord.User):
    user_id = str(member.id)
    user_games = [(game, users[user_id]) for game, users in game_usernames.items() if user_id in users]

    if not user_games:
        await ctx.send(f"{member.name} does not have any usernames registered.")
        return

    response = f"Usernames for {member.name}:\n"
    for game, username in user_games:
        response += f"- {game}: {username}\n"
    await ctx.send(response)

@bot.command(name="viewsunday")
async def view_sunday(ctx):
    schedule = class_routine.get("sunday", "No routine found.")
    table = format_routine_table("Sunday", schedule)
    await ctx.send(table)

@bot.command(name="viewmonday")
async def view_monday(ctx):
    schedule = class_routine.get("monday", "No routine found.")
    table = format_routine_table("Monday", schedule)
    await ctx.send(table)

@bot.command(name="viewtuesday")
async def view_tuesday(ctx):
    schedule = class_routine.get("tuesday", "No routine found.")
    table = format_routine_table("Tuesday", schedule)
    await ctx.send(table)

@bot.command(name="viewwednesday")
async def view_wednesday(ctx):
    schedule = class_routine.get("wednesday", "No routine found.")
    table = format_routine_table("Wednesday", schedule)
    await ctx.send(table)

@bot.command(name="viewthursday")
async def view_thursday(ctx):
    schedule = class_routine.get("thursday", "No routine found.")
    table = format_routine_table("Thursday", schedule)
    await ctx.send(table)

@bot.command(name="viewfriday")
async def view_friday(ctx):
    schedule = class_routine.get("friday", "No routine found.")
    table = format_routine_table("Friday", schedule)
    await ctx.send(table)

@bot.command(name="changesunday")
async def change_sunday(ctx, *, schedule: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to modify the routine.")
        return
    class_routine["sunday"] = schedule
    save_routine_data()
    await ctx.send("Sunday's routine updated successfully!")

@bot.command(name="changemonday")
async def change_monday(ctx, *, schedule: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to modify the routine.")
        return
    class_routine["monday"] = schedule
    save_routine_data()
    await ctx.send("Monday's routine updated successfully!")

@bot.command(name="changetuesday")
async def change_tuesday(ctx, *, schedule: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to modify the routine.")
        return
    class_routine["tuesday"] = schedule
    save_routine_data()
    await ctx.send("Tuesday's routine updated successfully!")

@bot.command(name="changewednesday")
async def change_wednesday(ctx, *, schedule: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to modify the routine.")
        return
    class_routine["wednesday"] = schedule
    save_routine_data()
    await ctx.send("Wednesday's routine updated successfully!")

@bot.command(name="changethursday")
async def change_thursday(ctx, *, schedule: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to modify the routine.")
        return
    class_routine["thursday"] = schedule
    save_routine_data()
    await ctx.send("Thursday's routine updated successfully!")

@bot.command(name="changefriday")
async def change_friday(ctx, *, schedule: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to modify the routine.")
        return
    class_routine["friday"] = schedule
    save_routine_data()
    await ctx.send("Friday's routine updated successfully!")

PROMOTIONS = {
    "The Boys": ("The Men", 102),
    "The Girls": ("The Ladies", 102),
    "The Men": ("The Patriarchs", 400),
    "The Ladies": ("The Matriarchs", 400),
}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    if user_id not in activity_data:
        activity_data[user_id] = {"messages": 0}

    activity_data[user_id]["messages"] += 1

    save_activity_data()

    await check_promotion(message.author, message.guild)

    await bot.process_commands(message)

async def check_promotion(member, guild):
    """Check if a user qualifies for promotion."""
    user_id = str(member.id)
    user_activity = activity_data.get(user_id, {})
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

@bot.command(name="activity")
async def view_activity(ctx, member: discord.Member = None):
    """View activity stats for a user."""
    member = member or ctx.author
    user_id = str(member.id)
    user_activity = activity_data.get(user_id, {"messages": 0})
    await ctx.send(f"{member.mention} has sent {user_activity['messages']} messages.")

@bot.event
async def on_shutdown():
    save_activity_data()
    
class RPSButton(Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        view: RPSView = self.view
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
        if self.player2:
            p1_choice = self.choices[self.player1]
            p2_choice = self.choices[self.player2]
            result = self.determine_winner(p1_choice, p2_choice)
            await interaction.followup.send(f"{self.player1.mention} chose {p1_choice}, {self.player2.mention} chose {p2_choice}. {result}")
        else:
            p1_choice = self.choices[self.player1]
            bot_choice = random.choice(["rock", "paper", "scissors"])
            result = self.determine_winner(p1_choice, bot_choice)
            await interaction.followup.send(f"You chose {p1_choice}, I chose {bot_choice}. {result}")

    def determine_winner(self, choice1, choice2):
        if choice1 == choice2:
            return "It's a tie!"
        elif (choice1 == "rock" and choice2 == "scissors") or (choice1 == "paper" and choice2 == "rock") or (choice1 == "scissors" and choice2 == "paper"):
            return f"{self.player1.mention} wins!" if self.player2 else "You win!"
        else:
            return f"{self.player2.mention} wins!" if self.player2 else "You lose!"

@bot.command(name="rps")
async def rps_single(ctx):
    view = RPSView(player1=ctx.author)
    await ctx.send("Choose your move:", view=view)

@bot.command(name="rpsmulti")
async def rps_multi(ctx, opponent: discord.User):
    if opponent == ctx.author:
        await ctx.send("You cannot challenge yourself.")
        return
    view = RPSView(player1=ctx.author, player2=opponent)
    await ctx.send(f"{opponent.mention}, you have been challenged to a game of Rock-Paper-Scissors! Choose your move:", view=view)

class FlipButton(Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        view: FlipView = self.view
        await view.handle_choice(interaction, self.custom_id)

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
            p1_choice = self.choices[self.player1]
            p2_choice = self.choices[self.player2]
            result = self.determine_winner(p1_choice, p2_choice, coin_result)
            await interaction.followup.send(f"The coin landed on {coin_result}. {result}")
        else:
            p1_choice = self.choices[self.player1]
            result = "You win!" if p1_choice == coin_result else "You lose!"
            await interaction.followup.send(f"The coin landed on {coin_result}. {result}")

    def determine_winner(self, choice1, choice2, coin_result):
        if choice1 == coin_result and choice2 == coin_result:
            return "It's a tie!"
        elif choice1 == coin_result:
            return f"{self.player1.mention} wins!"
        else:
            return f"{self.player2.mention} wins!"

@bot.command(name="flip")
async def flip_single(ctx):
    view = FlipView(player1=ctx.author)
    await ctx.send("Choose Heads or Tails:", view=view)

@bot.command(name="flipmulti")
async def flip_multi(ctx, opponent: discord.User):
    if opponent == ctx.author:
        await ctx.send("You cannot challenge yourself.")
        return
    view = FlipView(player1=ctx.author, player2=opponent)
    await ctx.send(f"{opponent.mention}, you have been challenged to a game of Heads or Tails! Choose your side:", view=view)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if "voice_log" not in voice_activity_data:
            voice_activity_data["voice_log"] = {}
        if str(after.channel.id) not in voice_activity_data["voice_log"]:
            voice_activity_data["voice_log"][str(after.channel.id)] = []
        voice_activity_data["voice_log"][str(after.channel.id)].append({
            "user": member.name,
            "action": "joined",
            "timestamp": str(discord.utils.utcnow() + datetime.timedelta(hours=0, minutes=0))
        })
    elif before.channel is not None and after.channel is None:
        if "voice_log" not in voice_activity_data:
            voice_activity_data["voice_log"] = {}
        if str(before.channel.id) not in voice_activity_data["voice_log"]:
            voice_activity_data["voice_log"][str(before.channel.id)] = []
        voice_activity_data["voice_log"][str(before.channel.id)].append({
            "user": member.name,
            "action": "left",
            "timestamp": str(discord.utils.utcnow() + datetime.timedelta(hours=0, minutes=0))
        })
        
        if before.channel.members == []:
            log_channel = member.guild.get_channel(1308408556961136680)
            if log_channel:
                log_entries = voice_activity_data["voice_log"].pop(str(before.channel.id), [])
                log_message = f"Voice channel '{before.channel.name}' log:\n"
                for entry in log_entries:
                    timestamp = discord.utils.format_dt(discord.utils.parse_time(entry['timestamp']), style='t')
                    log_message += f"{timestamp} - {entry['user']} {entry['action']} the channel.\n"
                await log_channel.send(log_message)
                
    save_voice_activity_data(voice_activity_data)

@bot.command(name="announce")
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message: str):
    parts = message.split()
    potential_channel = parts[0]
    if potential_channel.startswith('<#') and potential_channel.endswith('>'):
        channel_id = int(potential_channel[2:-1])
        channel = bot.get_channel(channel_id)
        if channel is None:
            await ctx.send("Invalid channel mention.")
            return
        message = ' '.join(parts[1:])
    else:
        channel = ctx.channel
    await channel.send(message)
    await ctx.message.delete()

@bot.command(name="helpme")
async def help_command(ctx):
    help_text = """
    **Game Username Commands:**
    1. `!addgame <game_name> <username> [@user]`: Add or update a username.
    2. `!view <game_name>`: View usernames for a game.
    3. `!games`: List all games.
    4. `!viewuser @user`: View a user's usernames across games.

    **Routine Commands:**
    1. `!viewsunday` - `!viewfriday`: View routine for a specific day.
    2. `!viewweek`: View the entire week's routine.
    3. `!changesunday` - `!change<day>`: Modify a day's routine (Admin only).
    4. `!routine`: Get the weekly routine as an image.
    5. `!routinepdf`: Get the weekly routine as a styled PDF.

    **Activity Commands:**
    1. `!activity [@user]`: View activity stats for a user.

    **Rock-Paper-Scissors Commands:**
    1. `!rps`: Play a single-player game of Rock-Paper-Scissors.
    2. `!rpsmulti @user`: Challenge another user to a game of Rock-Paper-Scissors.

    **Heads or Tails Commands:**
    1. `!flip`: Play a single-player game of Heads or Tails.
    2. `!flipmulti @user`: Challenge another user to a game of Heads or Tails.

    **Other Commands:**
    1. `!announce <#channel> <message>`: Announce a message to a channel (Admin only).
    2. `!helpme`: Show this help message.
    """
    await ctx.send(help_text)

@bot.command(name="viewweek")
async def view_week(ctx):
    table = format_weekly_routine_table(class_routine)
    await ctx.send(table)

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

    fig, ax = plt.subplots(figsize=(11, 4))
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
    for (row, col), cell in table.get_celld().items():
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

@bot.command(name="routine")
async def routine_image(ctx):
    filename = "routine.png"
    generate_routine_image(class_routine, filename)
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            await ctx.send(file=discord.File(f, filename))
    else:
        await ctx.send("Routine screenshot not found on the server.")

@bot.command(name="routinepdf")
async def routine_pdfimg(ctx):
    filename = "routine.pdf"
    generate_routine_image_pdf(class_routine, filename)
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            await ctx.send(file=discord.File(f, filename))
    else:
        await ctx.send("Routine PDF not found on the server.")

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

    fig, ax = plt.subplots(figsize=(14, 6))
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

    for (row, col), cell in table.get_celld().items():
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

bot.run(os.getenv("DISCORD_BOT_TOKEN"))

# Ensure the environment variable DISCORD_BOT_TOKEN is set before running the bot
# You can set it in your terminal or in a .env file
# Example: export DISCORD_BOT_TOKEN="your_token_here"
# Make sure to install the required libraries: discord.py, matplotlib, and any others you need
# You can install them using pip:
# pip install -r requirements.txt
# This bot is designed to be run in a Discord server where you have the necessary permissions to manage roles and send messages in the channels.
# You can extend the functionality further by adding more commands and features as per your requirements.
