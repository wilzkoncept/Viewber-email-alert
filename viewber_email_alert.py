import ssl
import certifi
import time
import requests
from imapclient import IMAPClient
import pyzmail

# Email server settings
HOST = 'imap.gmail.com'
USERNAME = 'wilzkoncept@gmail.com'
PASSWORD = 'tgyr pvol yujo oonv'  # Gmail app password
FROM_EMAIL = 'viewings@viewber.co.uk'
CHECK_INTERVAL = 60  # in seconds

# VoiceMonkey Announcement API settings
VOICEMONKEY_API_URL = "https://api-v2.voicemonkey.io/announcement"
MONKEY_TOKEN = "4da5355d44138ef99c63a6fa3d4e7ee4_4484f041541be1073a3e4bc3a84e1a6a"
DEVICE_NAME = "viewber"
ANNOUNCEMENT_TEXT = "You have a new email from Viewber"

def send_voice_monkey_alert():
    params = {
        "token": MONKEY_TOKEN,
        "device": DEVICE_NAME,
        "announcement": ANNOUNCEMENT_TEXT
    }
    response = requests.get(VOICEMONKEY_API_URL, params=params)
    if response.status_code == 200:
        print("🔊 Alexa announcement triggered.")
    else:
        print(f"❌ Error triggering announcement: {response.status_code} - {response.text}")

def check_emails():
    cafile_path = certifi.where()
    print(f"✅ Using CA file: {cafile_path}")
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=cafile_path)

    with IMAPClient(HOST, ssl=True, ssl_context=context) as server:
        server.login(USERNAME, PASSWORD)
        server.select_folder('INBOX')

        # Filter only unseen emails from Viewber
        messages = server.search(['UNSEEN', 'FROM', FROM_EMAIL])
        for msgid in messages:
            raw_message = server.fetch([msgid], ['BODY[]', 'FLAGS'])
            message = pyzmail.PyzMessage.factory(raw_message[msgid][b'BODY[]'])
            subject = message.get_subject().lower()

            if 'confirmed' in subject or 'cancelled' in subject:
                print(f"⏩ Skipping email with subject: {subject}")
                server.add_flags(msgid, [b'\\Seen'])  # Mark as read anyway
                continue

            print(f"🔔 New relevant email with subject: {subject}")
            send_voice_monkey_alert()
            server.add_flags(msgid, [b'\\Seen'])  # Mark as read to avoid re-alert

def main():
    print("📬 Starting Viewber email alert service...")
    while True:
        try:
            check_emails()
        except Exception as e:
            print(f"⚠️ Error checking emails: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
