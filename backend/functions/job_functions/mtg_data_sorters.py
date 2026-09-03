def legalities_sorter(legalities):
    full_legalities = {}
    
    for legality, legality_status in legalities.items():
        if legality_status == 'legal':
            full_legalities[legality] = True
        elif legality_status == 'not_legal':
            full_legalities[legality] = False
        else:
            full_legalities[legality] = False
    return full_legalities

def prices_sorter(prices):
    full_prices = {}
    
    for price_type, price_value in prices.items():
        if price_value is not None:
            try:
                full_prices[price_type] = float(price_value)
            except ValueError:
                full_prices[price_type] = None
        else:
            full_prices[price_type] = False
    return full_prices

def magic_color_identifier(key_colors):
    colors = {
        'W': None,
        'U': None,
        'B': None,
        'R': None,
        'G': None,
        'C': None
    }

    if not key_colors:
        key_colors = []
    elif not isinstance(key_colors, (list, tuple)):
        key_colors = [key_colors]

    for color in colors.keys():
        if color in key_colors:
            colors[color] = True
        else:
            colors[color] = False

    return colors
