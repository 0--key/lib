replacement = {"'": '%27', '.': '%2E', '+': '%2B', '`': '%60',
               '#': '%23', ' ': '%20', '%': '%25'}


def purify_url(raw_url):
    """Replases prohibited symbols out from raw url"""
    clear_url = str(raw_url)
    for k in replacement:
        clear_url = clear_url.replace(k, replacement[k])
    return clear_url
