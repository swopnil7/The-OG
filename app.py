import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GAME_FILE = "game_usernames.json"
ROUTINE_FILE = "class_routine.json"
ACTIVITY_FILE = "activity_data.json"

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
        
game_usernames = load_game_data()
class_routine = load_routine_data()
activity_data = load_activity_data()

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
    """
    await ctx.send(help_text)

bot.run("bot_token")
