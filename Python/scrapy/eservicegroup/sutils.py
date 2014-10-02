def comas2dots(s):
    if s:
        s[0] = s[0].replace(",", ".")
    return s

def first(s):
    if isinstance(s, list) and s:
        return s[0]
    return s
