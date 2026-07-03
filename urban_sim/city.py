import numpy as np


FACILITY_TYPES = [
    "home",
    "work",
    "school",
    "station",
    "commerce",
    "hospital",
    "park",
    "admin",
]


def make_city(cfg):
    w = int(cfg.get("city_width", 24))
    h = int(cfg.get("city_height", 18))

    facilities = {
        "home": [(3, 3), (5, 5), (4, 12), (7, 14), (20, 4), (18, 14)],
        "work": [(15, 5), (17, 7), (19, 8), (14, 12)],
        "school": [(8, 9), (11, 14)],
        "station": [(9, 4), (12, 9), (16, 13)],
        "commerce": [(12, 5), (13, 10), (18, 11), (6, 8)],
        "hospital": [(21, 12), (10, 2)],
        "park": [(5, 15), (20, 15), (3, 9)],
        "admin": [(12, 15)],
    }

    if cfg.get("policy_add_station", False):
        facilities["station"].append((6, 12))
    if cfg.get("policy_add_park", False):
        facilities["park"].append((14, 3))
    if cfg.get("policy_mixed_use", False):
        facilities["work"].extend([(5, 6), (19, 5)])
        facilities["commerce"].extend([(4, 4), (18, 4)])

    return {"width": w, "height": h, "facilities": facilities}


def nearest(point, locations):
    p = np.array(point, dtype=float)
    arr = np.array(locations, dtype=float)
    d = np.abs(arr - p).sum(axis=1)
    return tuple(arr[int(np.argmin(d))].astype(int))


def manhattan_step(pos, target, speed=1):
    x, y = int(pos[0]), int(pos[1])
    tx, ty = int(target[0]), int(target[1])

    for _ in range(int(max(1, speed))):
        if x != tx:
            x += 1 if tx > x else -1
        elif y != ty:
            y += 1 if ty > y else -1
    return (x, y)


def clamp_pos(pos, city):
    x, y = pos
    return (
        int(np.clip(x, 0, city["width"] - 1)),
        int(np.clip(y, 0, city["height"] - 1)),
    )
