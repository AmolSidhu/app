from secrets import token_urlsafe

def generate_share_code():
    sample = token_urlsafe(12)
    return sample
