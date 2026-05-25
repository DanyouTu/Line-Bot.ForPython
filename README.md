# Kairos

Kairos is an AI bot for LINE, powered by ChatGPT API 
and deployed on [Render web service](https://render.com).


## Features

- 🤖 Integrates ChatGPT for natural conversational responses.
- 🚀 Easily deployable on Render web services.
- 📝 Uses Redis as the memory container.

## Render Settings

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn -w 4 -b 0.0.0.0:10000 main:app
```
