

def win(offsetx, offsety, x, y, color, row, data_slots):
    directionx = offsetx
    directiony = offsety
    while True:
        if (x + directionx, y + directiony) in data_slots:
            if data_slots[(x + directionx, y + directiony)] == color:
                row += 1
            else:
                break
        else:
            break
        directionx += offsetx
        directiony += offsety
    return row


def win_check(data_slots, x, y, win_length):
    if (x, y) in data_slots:
        color = data_slots[(x, y)]
    else:
        return None
    row = 1
    row = win(1, 0, x, y, color, row, data_slots)
    row = win(-1, 0, x, y, color, row, data_slots)
    if row >= win_length:
        return color
    row = 1
    row = win(0, -1, x, y, color, row, data_slots)
    if row >= win_length:
        return color
    row = 1
    row = win(1, 1, x, y, color, row, data_slots)
    row = win(-1, -1, x, y, color, row, data_slots)
    if row >= win_length:
        return color
    row = 1
    row = win(-1, 1, x, y, color, row, data_slots)
    row = win(1, -1, x, y, color, row, data_slots)
    if row >= win_length:
        return color
    return None
