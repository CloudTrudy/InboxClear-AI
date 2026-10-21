
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail permission to apply labels and archive messages.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")


def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_recent_emails(limit=10):
    service = get_gmail_service()

    label_response = service.users().labels().list(
        userId="me"
    ).execute()

    demo_label_id = next(
        (
            label["id"]
            for label in label_response.get("labels", [])
            if label.get("name") == "InboxClear AI Demo"
        ),
        None,
    )

    if demo_label_id is None:
        raise ValueError(
            "Gmail label 'InboxClear AI Demo' was not found. "
            "Please check the label name in Gmail."
        )

    results = service.users().messages().list(
        userId="me",
        maxResults=limit,
        labelIds=[demo_label_id],
    ).execute()

    emails = []

    for item in results.get("messages", []):
        message = service.users().messages().get(
            userId="me",
            id=item["id"],
            format="full",
        ).execute()

        headers = message.get("payload", {}).get("headers", [])
        header_map = {
            h["name"].lower(): h["value"]
            for h in headers
        }

        emails.append({
            "id": message["id"],
            "sender": header_map.get("from", "Unknown sender"),
            "subject": header_map.get("subject", "(No subject)"),
            "body": message.get("snippet", ""),
        })

    return emails


def get_or_create_label(service, label_name):
    """Find a Gmail label or create it if needed."""
    response = service.users().labels().list(
        userId="me"
    ).execute()

    for label in response.get("labels", []):
        if label.get("name") == label_name:
            return label["id"]

    created = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        },
    ).execute()

    return created["id"]


def apply_inboxclear_label(message_id, category):
    """
    IMPORTANT: label and keep in inbox.
    JUNK: label and archive out of inbox.
    REVIEW or other categories: do not modify.
    """
    if category not in {"IMPORTANT", "JUNK"}:
        raise ValueError(
            "Only IMPORTANT and JUNK can be processed automatically."
        )

    service = get_gmail_service()
    label_name = f"InboxClear/{category}"
    label_id = get_or_create_label(service, label_name)

    changes = {"addLabelIds": [label_id]}

    if category == "JUNK":
        changes["removeLabelIds"] = ["INBOX"]

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body=changes,
    ).execute()

    return label_name
