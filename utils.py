def format_url(url):
    if not url.startswith("http"):
        return f"https://{url}"
    return url
