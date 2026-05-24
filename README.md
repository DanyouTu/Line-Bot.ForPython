# Kairos

Kairos is an AI bot for LINE, powered by ChatGPT API 
and deployed on [Render web service](https://render.com).


## Features

- 🤖 Integrates ChatGPT for natural conversational responses.
- 🚀 Easily deployable on Render web services.
- 📝 Uses Redis as the memory container, separating group and private chats.

## Render Settings

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn -w 4 -b 0.0.0.0:10000 main:app
```

### Environment

- TZ: Timezone (e.g., Asia/Taipei)
- REDIS_URL: URL for your Redis instance (if using Redis for memory/caching)
- BASE_URL: The root URL of your deployed web service
- WEBHOOK_HANDLER: The endpoint path for LINE webhook


## License

[MIT](https://choosealicense.com/licenses/mit/)
