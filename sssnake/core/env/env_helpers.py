from PIL import Image
def load_obstacles_map(path, col_res):
    if path == "":
        return [[0] * col_res for _ in range(col_res)]

    img = Image.open(path).convert("L")
    img_rescaled = img.resize((col_res, col_res), Image.LANCZOS)

    pixels = list(img_rescaled.getdata())
    obstacles_map = [
        [1 if p > 128 else 0 for p in pixels[row_start: row_start + col_res]]
        for row_start in range(0, col_res**2, col_res)
    ]
    return obstacles_map

def generate_safe_map(margin_units, map_size, obstacles_map):
    obstacles_size = len(obstacles_map)

    margin = max(int(margin_units * (obstacles_size / map_size)), 1)

    safe_map = [[1] * obstacles_size for _ in range(obstacles_size)]

    for y in range(obstacles_size):
        for x in range(obstacles_size):
            if obstacles_map[y][x] == 1:
                x0 = max(0, x - margin)
                x1 = min(obstacles_size, x + margin + 1)
                y0 = max(0, y - margin)
                y1 = min(obstacles_size, y + margin + 1)

                for yy in range(y0, y1):
                    for xx in range(x0, x1):
                        safe_map[yy][xx] = 0
    return safe_map