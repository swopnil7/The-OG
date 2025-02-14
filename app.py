import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import random
import datetime

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
        "sunday": "Calculus, Digital Logic, Problem Solving Techniques, Leisure",
        "monday": "C, Calculus, Digital Logic, Discrete Maths",
        "tuesday": "Calculus, Digital Logic, Drawing Practical (A)/Digital Logic Practical (B), Drawing Practical (A)/C Practical (B)",
        "wednesday": "Discrete Maths, Calculus, Problem Solving Techniques, Digital Logic Practical (A)/C Practical (B)",
        "thursday": "Workshop (A)/Drawing Practical (B), C Practical (A)/Drawing Practical (B), C, Problem Solving Techniques",
        "friday": "Discrete Maths, C, C Practical (A)/Workshop (B), Leisure",
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

@bot.command(name="viewweek")
async def view_week(ctx):
    response = ""
    for day, schedule in class_routine.items():
        response += format_routine_table(day.capitalize(), schedule) + "\n"
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

    **Rock-Paper-Scissors Commands:**
    1. `!rps`: Play a single-player game of Rock-Paper-Scissors.
    2. `!rpsmulti @user`: Challenge another user to a game of Rock-Paper-Scissors.

    **Heads or Tails Commands:**
    1. `!flip`: Play a single-player game of Heads or Tails.
    2. `!flipmulti @user`: Challenge another user to a game of Heads or Tails.
    """
    await ctx.send(help_text)

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
        # User joined a voice channel
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
        # User left a voice channel
        if "voice_log" not in voice_activity_data:
            voice_activity_data["voice_log"] = {}
        if str(before.channel.id) not in voice_activity_data["voice_log"]:
            voice_activity_data["voice_log"][str(before.channel.id)] = []
        voice_activity_data["voice_log"][str(before.channel.id)].append({
            "user": member.name,
            "action": "left",
            "timestamp": str(discord.utils.utcnow() + datetime.timedelta(hours=0, minutes=0))
        })
        
        # Check if the voice channel is now empty
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

bot.run("bot_token")
