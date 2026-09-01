"""
Telegram bot helper.

    python scripts/telegram_setup.py chat_id   # find your chat id, save to profile.json
    python scripts/telegram_setup.py test       # send yourself a test message
    python scripts/telegram_setup.py digest     # send a list of PENDING_REVIEW jobs

Needs config/profile.json -> messaging.bot_token (see docs/01_SETUP_API_KEYS.md).
An always-on listener with Approve/Pass buttons is not included - the hosted
dashboard (docs step 5) covers that use case.
"""
import json
import sqlite3
import sys
from pathlib import Path
from urllib import request, parse, error

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "config" / "profile.json"
DB = ROOT / "data" / "jobs.db"


def cfg():
    p = json.loads(PROFILE.read_text())
    token = (p.get("messaging") or {}).get("bot_token", "").strip()
    if not token:
        sys.exit("set messaging.bot_token in config/profile.json first")
    return p, token


def api(token, method, **params):
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = parse.urlencode(params).encode()
    try:
        with request.urlopen(request.Request(url, data=data), timeout=20) as r:
            return json.loads(r.read().decode())
    except error.HTTPError as e:
        sys.exit(f"{method} -> {e.code}: {e.read().decode()[:200]}")


def save_chat_id(profile, chat_id):
    profile.setdefault("messaging", {})["chat_id"] = str(chat_id)
    PROFILE.write_text(json.dumps(profile, indent=2))


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    action = sys.argv[1]
    profile, token = cfg()

    if action == "chat_id":
        res = api(token, "getUpdates")
        ids = {u["message"]["chat"]["id"]
               for u in res.get("result", []) if u.get("message")}
        if not ids:
            sys.exit("No messages found. Send your bot any message in Telegram, then retry.")
        chat_id = ids.pop()
        save_chat_id(profile, chat_id)
        print(f"chat_id {chat_id} saved to config/profile.json")
        return

    chat_id = (profile.get("messaging") or {}).get("chat_id")
    if not chat_id:
        sys.exit("run 'chat_id' first")

    if action == "test":
        api(token, "sendMessage", chat_id=chat_id, text="Job Hunt Agent: Telegram is connected.")
        print("sent")
    elif action == "digest":
        if not DB.exists():
            sys.exit("no data/jobs.db - run 'python scripts/track.py init'")
        c = sqlite3.connect(str(DB))
        rows = c.execute("SELECT id, company, role_title, location FROM jobs "
                         "WHERE status='PENDING_REVIEW' ORDER BY id DESC LIMIT 25").fetchall()
        if not rows:
            api(token, "sendMessage", chat_id=chat_id, text="No jobs pending review.")
            print("sent (empty)")
            return
        lines = [f"{r[0]}. {r[1]} - {r[2]}  [{r[3] or '?'}]" for r in rows]
        api(token, "sendMessage", chat_id=chat_id,
            text="Pending review:\n" + "\n".join(lines))
        print(f"sent ({len(rows)} jobs)")
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
