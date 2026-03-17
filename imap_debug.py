import imaplib
imap = imaplib.IMAP4_SSL("imap.zoho.in", 993)
imap.login("chandana3118@zohomail.in", "80RDhkmM7bSC")
print("Success!")
