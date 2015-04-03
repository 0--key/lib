# Replaces unrecognized symbols out from urls

replacement = {"'": '%27', '.': '%2E', '+': '%2B', '`': '%60',
               '#': '%23', ' ': '%20', '%': '%25'}
# append additional dictionary if it's necessary

def purify_url(raw_url):
    """Replases prohibited symbols out from raw url"""
    clear_url = str(raw_url)
    for k in replacement:
        clear_url = clear_url.replace(k, replacement[k])
    return clear_url
