# Kairos

Kairos is an AI bot for LINE, powered by the ChatGPT API (`gpt-4o`) and deployed on [Render web service](https://render.com). It leverages Redis to manage conversational memory and provides smart chat summarization.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/DanyouTu/Line_Bot-Kairos)

## Features

- 🤖 **ChatGPT Integration:** Powered by `gpt-4o` for natural, context-aware conversations.
- 📝 **Smart Memory Management:** Uses Redis as the memory container to store chat history, automatically clearing records older than 2 days to optimize storage.
- 📊 **Chat Summarization:** Automatically summarizes the chat room's messages from today and yesterday.
- 🌐 **Web History View:** Includes a `/history` web endpoint to easily view recent chat logs in HTML format.
- 🚀 **Cloud Ready:** Easily deployable on Render web services.

## Commands

Kairos supports the following LINE commands:

* `/talk <message>` (or `/t <message>`): Chat directly with the AI and save the conversation history.
* `/sum` (or `/s`): Generate a concise, bulleted summary of the chat room's recent messages.
* `/help` (or `/?`): Display the available command list.

## Render Settings

### Build Command

```bash
pip install -r requirements.txt

```
### Start Command
```bash
gunicorn -w 4 -b 0.0.0.0:10000 bot:app

```
> [!NOTE]
> Ensure the start command matches your main Python file. If your file is bot.py, use bot:app instead of main:app

## Environment Variables
For security reasons, do not hardcode your API keys. Make sure to set the following environment variables in your Render web service:
 * PORT: Web service port (default is 5000)
 * OPENAI_API_KEY: Your OpenAI API Key
 * LINE_CHANNEL_SECRET: Your LINE Messaging API Channel Secret
 * LINE_CHANNEL_ACCESS_TOKEN: Your LINE Messaging API Channel Access Token
 * REDIS_HOST: Your Redis instance host URL
 * REDIS_PORT: Your Redis instance port
 * REDIS_PASSWORD: Your Redis password
## Dependencies
This project relies on several key packages:
 * line-bot-sdk
 * Flask
 * openai==0.28.0
 * gunicorn
 * redis>=5.0.0
 * Flask-Session
