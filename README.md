# Temp Mail API (Python)

Python client for temporary email via **mob2.temp-mail.org**.

Create a disposable inbox, list messages, read full mail bodies, and optionally wait until a new message arrives.

## Features

- Create a new temporary mailbox (JWT auth)
- List inbox messages
- Read a full message by id
- Poll / wait for new mail
- List public domains (`temp-mail.io`)

## Install

```bash
pip install requests
```

## Usage

```python
from tempmail import TempMail

bot = TempMail()
bot.run()  # creates mailbox and prints inbox
```

### Create mailbox only

```python
bot = TempMail()
print(bot.create_mailbox())
# → {"token": "...", "mailbox": "name@domain.com"}
```

### Wait for a message

```python
bot = TempMail()
bot.create_mailbox()
msg = bot.wait_for_message(timeout=120, interval=5, subject_contains="verify")
print(msg)
```

## API methods

| Method | Description |
|--------|-------------|
| `create_mailbox()` | Create temp email + token |
| `get_messages()` | List messages |
| `get_message(id)` | Full message body |
| `wait_for_message(...)` | Poll until new mail |
| `domains()` | Public domains list |
| `run()` | Create + show inbox |

## License

MIT
