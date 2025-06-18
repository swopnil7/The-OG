# The-OG

A bot I made for my class's discord server 'The OGs'. Kinda cool bot that can do a bunch of things like managing game usernames, tracking class routines, logging voice channel activity, auto-promoting users based on their activities, playing games like Rock-Paper-Scissors and Heads or Tails, making announcements, creating files from text content and many more..

## Features

- **Game Username Management**
  - Add or update usernames for different games (for yourself or others, if admin).
  - View all usernames registered for a specific game.
  - List all games with registered usernames.
  - View all usernames a user has registered across games.

- **Class Routine Management**
  - View the class routine for a specific day.
  - View the entire week's routine as formatted text.
  - Get the weekly routine as an image or styled PDF.
  - Modify the class routine for a specific day (Admin only).

- **Activity Tracking & Auto-Promotion**
  - Track the number of messages sent by users.
  - Automatically promote users to new roles based on their activity.

- **Rock-Paper-Scissors Game**
  - Play a single-player or multiplayer game of Rock-Paper-Scissors with interactive buttons.

- **Heads or Tails Game**
  - Play a single-player or multiplayer game of Heads or Tails with interactive buttons.

- **Voice Channel Activity Logging**
  - Log when users join or leave voice channels.
  - Send a log message when a voice channel becomes empty, including a summary of activity.

- **Announcements**
  - Announce messages to any channel (Admin only).

- **File Posting**
  - Create and post a file with any extension and custom content via a modal.

- **Help Command**
  - Display a help message listing all available commands.

## Commands

### Game Username Commands

- `/addgame <game_name> <username> [@user]` — Add or update a username for a game (optionally for another user if admin).
- `/view <game_name>` — View all usernames registered for a specific game.
- `/games` — List all games with registered usernames.
- `/viewuser @user` — View all usernames a user has registered across games.

### Routine Commands

- `/routineday <day>` — View the class routine for a specific day.
- `/routineweek` — View the entire week's routine as formatted text.
- `/changeday <day> <schedule>` — Modify the class routine for a specific day (Admin only).
- `/routine` — Get the weekly routine as an image.
- `/routinepdf` — Get the weekly routine as a styled PDF.

### Activity Commands

- `/activity [@user]` — View activity stats (number of messages sent) for a user.

### Rock-Paper-Scissors Commands

- `/rps [@opponent]` — Play a single-player or multiplayer game of Rock-Paper-Scissors.

### Heads or Tails Commands

- `/flip [@opponent]` — Play a single-player or multiplayer game of Heads or Tails.

### Announcement Command

- `/announce <#channel> <message>` — Announce a message to a channel (Admin only).

### File Posting Command

- `/postfile <filename>` — Create and post a file with any extension and custom content.

### Help Command

- `/helpme` — Display the help message listing all available commands.

## Setup

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a .env file and add your bot token:
    ```
    DISCORD_BOT_TOKEN=your_bot_token
    ```
4. Run the bot:
    ```bash
    python app.py
    ```