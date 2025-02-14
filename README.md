# The-OG

A bot I made for my class's discord server 'The OGs'. Kinda cool bot that can do a bunch of things like managing game usernames, tracking class routines, logging voice channel activity, auto-promoting users based on their activities, and even playing games like Rock-Paper-Scissors and Heads or Tails.

## Features

- **Game Username Management**
  - Add or update usernames for different games.
  - View usernames for a specific game.
  - List all games with usernames.
  - View a user's usernames across games.

- **Class Routine Management**
  - View the class routine for a specific day.
  - View the entire week's routine.
  - Modify the class routine for a specific day (Admin only).

- **Activity Tracking**
  - Track the number of messages sent by users.
  - Promote users based on their activity.

- **Rock-Paper-Scissors Game**
  - Play a single-player game of Rock-Paper-Scissors.
  - Challenge another user to a game of Rock-Paper-Scissors.

- **Heads or Tails Game**
  - Play a single-player game of Heads or Tails.
  - Challenge another user to a game of Heads or Tails.

- **Voice Channel Activity Logging**
  - Log when users join or leave voice channels.
  - Send a log message when a voice channel becomes empty.

## Commands

### Game Username Commands

- `!addgame <game_name> <username> [@user]`: Add or update a username.
- `!view <game_name>`: View usernames for a game.
- `!games`: List all games.
- `!viewuser @user`: View a user's usernames across games.

### Routine Commands

- `!viewsunday` - `!viewfriday`: View routine for a specific day.
- `!viewweek`: View the entire week's routine.
- `!changesunday` - `!change<day>`: Modify a day's routine (Admin only).

### Activity Commands

- `!activity [@user]`: View activity stats for a user.

### Rock-Paper-Scissors Commands

- `!rps`: Play a single-player game of Rock-Paper-Scissors.
- `!rpsmulti @user`: Challenge another user to a game of Rock-Paper-Scissors.

### Heads or Tails Commands

- `!flip`: Play a single-player game of Heads or Tails.
- `!flipmulti @user`: Challenge another user to a game of Heads or Tails.

### Help Command

- `!helpme`: Display the help message with all available commands.

## Setup

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install requirements.txt
3. Create a .env file and add your bot token:
    ```bash
    DISCORD_BOT_TOKEN=your_bot_token
4. Run the bot:
    ```bash
    python app.py