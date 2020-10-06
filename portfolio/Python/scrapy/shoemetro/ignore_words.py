IGNORE = ['women', 'men', 'boy', 'girl', 'kid', 'unisex',
          'black', 'white', 'orange', 'green', 'blue', 'yellow',
          'gray', 'grey', 'gold', 'bronze', 'silver', 'purple',
          'violet', 'red', 'pink', 'rose', 'burgundy', 'off white',
          'ivory', 'bone', 'brown', 'tan', 'beige', 'olive', '"',
          "'", '(', ')', '{', '}', '[', ']', '\\', '|', '*']

IGNORE = []


def accept_product(name):
    for ig in IGNORE:
        if ig in name.lower():
            return False

    return True