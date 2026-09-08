# TempMail-API

Python client for temporary email.

Create disposable addresses, list domains, read inbox, and log in with a token key.

## Install

```bash
pip install requests
```

## Quick start

```bash
python main.py
```

## Usage

```python
from tempmail import TempMail

bot = TempMail()

# domains
print(bot.list_domain_names())

# create mailbox (optional domain)
bot.create_mailbox(domain="ozsaip.com")
print(bot.mailbox, bot.token)

# inbox
print(bot.get_messages())

# login with key
bot2 = TempMail()
bot2.login(token=bot.token, email=bot.mailbox)
print(bot2.get_messages())

# wait for mail
msg = bot.wait_for_message(timeout=120, interval=5)
print(msg)
```

## Methods

| Method | Description |
|--------|-------------|
| `domains()` | Full domains response |
| `list_domain_names()` | Domain names only |
| `create_mailbox(domain=None)` | New email + token |
| `login(token, email=None)` | Use existing key |
| `get_messages()` | List inbox |
| `get_message(id)` | Read one message |
| `wait_for_message(...)` | Poll until new mail |
| `run()` | Full demo flow |

## API

- Primary: `https://api.internal.temp-mail.io`
- Optional backend: `mob2.temp-mail.org` (`backend="mob2"`)

## License

MIT
