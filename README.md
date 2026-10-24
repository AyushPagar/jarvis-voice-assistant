# Jarvis

A voice controlled assistant written in Python.

## API keys

Copy `.env.example` to `.env`, then replace each placeholder with your own key:

- `NEWSAPI_KEY`: your NewsAPI key, used for headlines.
- `OPENAI_API_KEY`: your OpenAI API key, used by `client.py`.

Keep `.env` private. It is listed in `.gitignore` and should never be committed.

The project currently reads environment variables directly. In PowerShell, set them for the current terminal before starting the app:

```powershell
$env:NEWSAPI_KEY = "Enter your NewsAPI key here"
$env:OPENAI_API_KEY = "Enter your OpenAI API key here"
python main.py
```

Replace the example text with your actual keys. `client.py` uses the OpenAI key when you run it directly.
