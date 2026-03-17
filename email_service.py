# email_service.py
import imaplib
import email
from email.header import decode_header
from datetime import datetime
from email_config import EMAIL_ACCOUNTS, MAX_FETCH_PER_ACCOUNT


def decode_mime_words(s):
    if not s:
        return ""
    decoded_parts = decode_header(s)
    result = ""
    for part, enc in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(enc or "utf-8", errors="ignore")
        else:
            result += part
    return result


def extract_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                try:
                    return part.get_payload(decode=True).decode(errors="ignore")
                except:
                    pass
    else:
        try:
            return msg.get_payload(decode=True).decode(errors="ignore")
        except:
            pass
    return ""


def detect_provider(msg):
    """
    Detect original provider from headers
    """
    headers = str(msg)
    frm = (msg.get("From") or "").lower()

    if "outlook.com" in headers or "hotmail.com" in headers or "office365" in headers:
        return "Outlook"
    if "yahoo.com" in headers or "ymail.com" in headers:
        return "Yahoo"
    if "zohomail" in headers or "zoho.com" in headers:
        return "Zoho"
    return "Gmail"


def fetch_from_gmail(account, max_count=25):
    emails = []
    mail = imaplib.IMAP4_SSL(account["imap_server"], account["imap_port"])
    mail.login(account["email"], account["password"])
    mail.select("INBOX")

    _, data = mail.search(None, "ALL")
    mail_ids = data[0].split()[-max_count:]

    for num in reversed(mail_ids):
        _, msg_data = mail.fetch(num, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject = decode_mime_words(msg.get("Subject"))
        sender = decode_mime_words(msg.get("From"))
        date_str = msg.get("Date")

        try:
            date_fmt = email.utils.parsedate_to_datetime(date_str).strftime("%Y-%m-%d %H:%M")
        except:
            date_fmt = date_str or ""

        body = extract_body(msg)
        snippet = (body[:180] + "...") if body else ""

        provider = detect_provider(msg)

        emails.append({
            "account_label": provider,  # 🔥 Original source
            "subject": subject or "(no subject)",
            "sender": sender or "(unknown sender)",
            "date": date_fmt,
            "body": body or "",
            "snippet": snippet,
        })

    mail.logout()
    return emails


def fetch_all_accounts():
    # ONLY Gmail ingestion
    return fetch_from_gmail(EMAIL_ACCOUNTS[0], MAX_FETCH_PER_ACCOUNT)
