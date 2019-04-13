def build_https_absolute_uri(url: str) -> str:
    if url is None:
        raise ValueError("Provide a not empty string.")

    return url.replace("http://", "https://")
