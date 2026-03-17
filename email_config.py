# email_config.py

EMAIL_ACCOUNTS = [
    {
        "label": "Gmail",
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "email": "---@gmail.com" ,
        "password": "#app pass",
         #"email": "---@gmail.com", (othermail)#"password": "#app pass",   (other APass)
    },
    {
        "label": "Zohomail",
        "imap_server": "imap.zoho.in",
        "imap_port": 993,
        "email": "---@zohomail.in",
        "password": "#app pass",
    },
]

# maximum emails to fetch per account (reduce during development)
MAX_FETCH_PER_ACCOUNT = 50


