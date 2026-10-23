# Discord Channel Message Scraper

A Python script to fetch message history from a specific Discord channel and save it as a CSV file. It uses an official Discord bot account and supports filtering by date ranges.

### Prerequisites
- Python 3.8 or higher
- A registered Discord Bot with the **Message Content Intent** enabled.

### Setup
1. Install the required dependencies:
   `pip install discord.py python-dotenv`
2. Create a `.env` file in the same directory as the script and add your bot token:
   `BOT_TOKEN=your_secret_token_here`
3. Ensure the bot is invited to your server and has **View Channel** and **Read Message History** permissions for the target channel.

### Usage
Run the script via the command line, providing the target channel ID. You can optionally provide start and end dates (ISO 8601 format).

`python fetch_messages.py -c 123456789012345678`
`python fetch_messages.py -c 123456789012345678 -s "2024-01-01T00:00:00Z" -e "2024-06-30T23:59:59Z"`
