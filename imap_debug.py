import imaplib
imap = imaplib.IMAP4_SSL("imap.zoho.in", 993)
imap.login("--@zohomail.in", "16 letters")#app pass
print("Success!")
