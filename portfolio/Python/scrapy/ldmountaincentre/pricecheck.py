from decimal import Decimal

VALID_PERC = Decimal(0.4)

def valid_price(belowtradeprices_price, price):
    p1 = Decimal(belowtradeprices_price)
    p2 = Decimal(price)

    return p1 - p1 * VALID_PERC <= p2 <= p1 + p2 * VALID_PERC
