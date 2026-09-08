import requests
import time

class TempMail:
    """
    Client for mob2.temp-mail.org (Temp Mail API).
    Flow: create mailbox → poll messages → read message.
    """

    def __init__(self, token=None):
        self.token = token
        self.mailbox = None
        self.base_url = "https://mob2.temp-mail.org"
        self.session = requests.Session()
        self.headers = {
            'accept': 'application/json',
            'user-agent': 'TempMail/1022 CFNetwork/1568.100.1 Darwin/24.0.0',
        }
        if token:
            self.headers['authorization'] = token

    def _headers(self):
        h = self.headers.copy()
        if self.token:
            h['authorization'] = self.token
        return h

    def create_mailbox(self):
        """POST /mailbox — create new temp email, returns token + address"""
        r = self.session.post(
            f'{self.base_url}/mailbox',
            headers=self._headers(),
            timeout=30
        )
        try:
            data = r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}
        self.token = data.get('token')
        self.mailbox = data.get('mailbox')
        if self.token:
            self.headers['authorization'] = self.token
            print(f"[+] mailbox: {self.mailbox}")
            print("[+] token saved")
        return data

    def get_messages(self):
        """GET /messages — list inbox"""
        r = self.session.get(
            f'{self.base_url}/messages',
            headers=self._headers(),
            timeout=30
        )
        try:
            return r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}

    def get_message(self, message_id):
        """GET /messages/{id} — full message body"""
        r = self.session.get(
            f'{self.base_url}/messages/{message_id}',
            headers=self._headers(),
            timeout=30
        )
        try:
            return r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}

    def domains(self):
        """Public domains list (temp-mail.io)"""
        r = self.session.get(
            'https://api.internal.temp-mail.io/api/v4/domains',
            headers={'accept': 'application/json'},
            timeout=30
        )
        try:
            return r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}

    def wait_for_message(self, timeout=120, interval=5, subject_contains=None):
        """Poll inbox until a message arrives (or timeout)."""
        deadline = time.time() + timeout
        seen = set()
        while time.time() < deadline:
            data = self.get_messages()
            msgs = data.get('messages') or []
            for m in msgs:
                mid = m.get('_id')
                if mid in seen:
                    continue
                seen.add(mid)
                subj = m.get('subject') or ''
                if subject_contains and subject_contains.lower() not in subj.lower():
                    continue
                print(f"[+] new mail: {subj} from {m.get('from')}")
                full = self.get_message(mid)
                return full
            print(f"[*] waiting... ({int(deadline - time.time())}s left)")
            time.sleep(interval)
        return None

    def run(self):
        """Create mailbox and show inbox once."""
        if not self.token:
            created = self.create_mailbox()
            print("Create:", created)
        else:
            print(f"[*] using existing token | mailbox={self.mailbox}")

        inbox = self.get_messages()
        print("Inbox:", inbox)
        msgs = inbox.get('messages') or []
        for m in msgs:
            mid = m.get('_id')
            print(f"\n--- message {mid} ---")
            print(self.get_message(mid))
        return inbox


if __name__ == "__main__":
    bot = TempMail()
    bot.run()
