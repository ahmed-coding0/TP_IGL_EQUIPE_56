def validate_email(email):
    return "@" in email

def validate_password(password):
    return len(password) > 8

def validate_age(age):
    return age > 0

def validate_phone(phone):
    return len(phone) == 10

def validate_username(username):
    return len(username) >= 3

def validate_url(url):
    return url.startswith("http")

def is_valid_credit_card(card_number):
    return len(str(card_number)) == 16
