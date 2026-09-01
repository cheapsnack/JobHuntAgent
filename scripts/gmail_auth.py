"""
Gmail OAuth helper - authorise once, then create DRAFT emails with an
attachment. This kit never sends mail. You review and send from Gmail
Drafts yourself.

    python scripts/gmail_auth.py                          # run the consent flow
    python scripts/gmail_auth.py --test-draft you@x.com   # create a test draft
    python scripts/gmail_auth.py --draft to@x.com "Subject" body.txt resume.pdf

Needs config/gmail_client_secret.json (see docs/01_SETUP_API_KEYS.md).
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""
import base64
import sys
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRET = ROOT / "config" / "gmail_client_secret.json"
TOKEN = ROOT / "config" / "gmail_token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not SECRET.exists():
                sys.exit("config/gmail_client_secret.json missing - see docs/01_SETUP_API_KEYS.md")
            creds = InstalledAppFlow.from_client_secrets_file(str(SECRET), SCOPES).run_local_server(port=0)
        TOKEN.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def make_draft(svc, to, subject, body, attachment=None, bcc=None):
    msg = EmailMessage()
    msg["To"] = to
    msg["Subject"] = subject
    if bcc:
        msg["Bcc"] = bcc
    msg.set_content(body)
    if attachment:
        p = Path(attachment)
        msg.add_attachment(p.read_bytes(), maintype="application",
                           subtype="pdf", filename=p.name)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    d = svc.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return d["id"]


def main():
    args = sys.argv[1:]
    svc = service()
    print("authorised. token cached at config/gmail_token.json")

    if args and args[0] == "--test-draft" and len(args) == 2:
        did = make_draft(svc, args[1], "Job Hunt Agent test draft",
                         "This is a test draft created by gmail_auth.py.")
        print(f"draft created: {did} - check your Gmail Drafts")
    elif args and args[0] == "--draft" and len(args) >= 4:
        to, subject, body_file = args[1], args[2], args[3]
        attachment = args[4] if len(args) > 4 else None
        did = make_draft(svc, to, subject, Path(body_file).read_text(), attachment)
        print(f"draft created: {did}")


if __name__ == "__main__":
    main()
