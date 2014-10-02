IGNORE = []


def accept_product(name):
    for ig in IGNORE:
        if ig in name.lower():
            return False

    return True