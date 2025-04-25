from PIL import Image
def load_obstacles_map(path, col_res):
    if path == "":
        return [[0] * col_res for _ in range(col_res)]

    img = Image.open(path).convert("L")
    img_rescaled = img.resize((col_res[0], col_res[1]), Image.LANCZOS)

    pixels = list(img_rescaled.getdata())
    obstacles_map = [
        [1 if p > 128 else 0 for p in pixels[row_start: row_start + col_res[0]]]
        for row_start in range(0, col_res[0] * col_res[1], col_res[0])
    ]
    return obstacles_map

def generate_safe_map(margin_units, map_size, obstacles_map):
    obstacles_w, obstacles_h = len(obstacles_map[0]), len(obstacles_map)

    margin_x = max(int(margin_units * (obstacles_w / map_size)), 1)
    margin_y = max(int(margin_units * (obstacles_h / map_size)), 1)

    safe_map = [[1] * obstacles_w for _ in range(obstacles_h)]

    for y in range(obstacles_h):
        for x in range(obstacles_w):
            if obstacles_map[y][x] == 1:
                x0 = max(0, x - margin_x)
                x1 = min(obstacles_w, x + margin_x + 1)
                y0 = max(0, y - margin_y)
                y1 = min(obstacles_h, y + margin_y + 1)

                for yy in range(y0, y1):
                    for xx in range(x0, x1):
                        safe_map[yy][xx] = 0
    return safe_map