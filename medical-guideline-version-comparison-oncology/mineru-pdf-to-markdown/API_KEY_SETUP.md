# MinerU API Key Setup

This skill requires a personal MinerU API key. Do not commit the key or save it in `API.txt`.

1. Visit the [MinerU website](https://mineru.net/) and register or sign in.
2. Open the account's API management page and create an API key.
3. Store the key only in the current terminal session or a local secret manager.

## Windows PowerShell

```powershell
$env:MINERU_API_KEY = "your_api_key"
python mineru-pdf-to-markdown/convert.py input/ output/markdown_output en
```

## macOS or Linux

```bash
export MINERU_API_KEY=your_api_key
python mineru-pdf-to-markdown/convert.py input/ output/markdown_output en
```

The repository's `.gitignore` deliberately excludes `API.txt` and `.env` files. Never add an API key to a commit, report, screenshot, or email attachment.