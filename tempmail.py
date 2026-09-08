import requests
import time

class TempMail:
    def __init__(self, token=None, email=None, backend='tempmail_io'):
        self.token = token
        self.mailbox = email
        self.backend = backend
        self.base_io = "https://api.internal.temp-mail.io"
        self.base_mob2 = "https://mob2.temp-mail.org"
        self.session = requests.Session()
        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36',
        }

    def _headers(self):
        h = self.headers.copy()
        if self.token:
            h['Authorization'] = self.token
        return h

    def domains(self):
        r = self.session.get(
            f'{self.base_io}/api/v4/domains',
            headers=self._headers(),
            timeout=30
        )
        try:
            return r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}

    def list_domain_names(self):
        data = self.domains()
        return [d.get('name') for d in (data.get('domains') or [])]

    def create_mailbox(self, domain=None):
        if self.backend == 'mob2':
            return self._create_mob2()
        body = {}
        if domain:
            body['domain'] = domain
        r = self.session.post(
            f'{self.base_io}/api/v3/email/new',
            headers=self._headers(),
            json=body,
            timeout=30
        )
        try:
            data = r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}
        self.mailbox = data.get('email')
        self.token = data.get('token')
        print(f"[+] mailbox: {self.mailbox}")
        print(f"[+] token (key): {self.token}")
        return data

    def _create_mob2(self):
        r = self.session.post(
            f'{self.base_mob2}/mailbox',
            headers={
                'accept': 'application/json',
                'user-agent': 'TempMail/1022 CFNetwork/1568.100.1 Darwin/24.0.0',
            },
            timeout=30
        )
        try:
            data = r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}
        self.token = data.get('token')
        self.mailbox = data.get('mailbox')
        print(f"[+] mailbox: {self.mailbox}")
        print(f"[+] token saved")
        return data

    def login(self, token, email=None):
        self.token = token
        if email:
            self.mailbox = email
        print(f"[+] logged in | mailbox={self.mailbox} | token={str(token)[:12]}...")
        return {'token': self.token, 'email': self.mailbox}

    def get_messages(self):
        if not self.mailbox and not self.token:
            return {'error': 'no mailbox — call create_mailbox() or login() first'}
        if self.backend == 'mob2':
            r = self.session.get(
                f'{self.base_mob2}/messages',
                headers={
                    'accept': 'application/json',
                    'user-agent': 'TempMail/1022 CFNetwork/1568.100.1 Darwin/24.0.0',
                    'authorization': self.token or '',
                },
                timeout=30
            )
        else:
            if not self.mailbox:
                return {'error': 'email required for tempmail_io backend'}
            r = self.session.get(
                f'{self.base_io}/api/v3/email/{self.mailbox}/messages',
                headers=self._headers(),
                timeout=30
            )
        try:
            data = r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}
        if isinstance(data, list):
            return {'mailbox': self.mailbox, 'messages': data}
        return data

    def get_message(self, message_id):
        if self.backend == 'mob2':
            r = self.session.get(
                f'{self.base_mob2}/messages/{message_id}',
                headers={
                    'accept': 'application/json',
                    'user-agent': 'TempMail/1022 CFNetwork/1568.100.1 Darwin/24.0.0',
                    'authorization': self.token or '',
                },
                timeout=30
            )
        else:
            r = self.session.get(
                f'{self.base_io}/api/v3/message/{message_id}',
                headers=self._headers(),
                timeout=30
            )
        try:
            return r.json()
        except Exception:
            return {'error': r.text[:300], 'status_code': r.status_code}

    def wait_for_message(self, timeout=120, interval=5, subject_contains=None):
        deadline = time.time() + timeout
        seen = set()
        while time.time() < deadline:
            data = self.get_messages()
            msgs = data.get('messages') if isinstance(data, dict) else (data if isinstance(data, list) else [])
            msgs = msgs or []
            for m in msgs:
                mid = m.get('_id') or m.get('id') or m.get('message_id')
                if mid is None or mid in seen:
                    continue
                seen.add(mid)
                subj = m.get('subject') or ''
                if subject_contains and subject_contains.lower() not in subj.lower():
                    continue
                print(f"[+] new mail: {subj} from {m.get('from')}")
                return self.get_message(mid)
            left = int(deadline - time.time())
            print(f"[*] waiting... ({left}s left) mailbox={self.mailbox}")
            time.sleep(interval)
        return None

    def run(self):
        # 1) fetch domains
        print("===== DOMAINS =====")
        names = self.list_domain_names()
        print("domains:", names)

        # 2) create mailbox on first domain
        domain = names[0] if names else None
        print(f"\n===== CREATE on domain={domain} =====")
        created = self.create_mailbox(domain=domain)
        print("create:", created)

        # 3) list inbox
        print("\n===== INBOX =====")
        inbox = self.get_messages()
        print("inbox:", inbox)

        # 4) login again using token key
        print("\n===== LOGIN WITH KEY =====")
        key = self.token
        email = self.mailbox
        bot2 = TempMail()
        bot2.login(token=key, email=email)
        print("inbox after login:", bot2.get_messages())

        return {
            'domains': names,
            'email': email,
            'token': key,
            'inbox': inbox,
        }


if __name__ == "__main__":
    bot = TempMail()
    bot.run()
