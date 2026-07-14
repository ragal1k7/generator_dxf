import ezdxf
import numpy as np


def generate_box(L, W, H, T, L_slot, target_slots=7, filename="output.dxf", spacing = 1):
    if L <= 0 or W <= 0 or H <= 0 or T <= 0:
        raise ValueError("Все размеры должны быть положительными")
    if L_slot <= 0:
        raise ValueError("Длина паза должна быть положительной")
    if 2 * T >= min(L, W, H):
        raise ValueError("Толщина слишком велика для заданных размеров")

    doc = ezdxf.new("R2000")
    doc.header["$MEASUREMENT"] = 1
    doc.units = 4
    msp = doc.modelspace()

    # ---- Helper functions ----

    def get_coords_offset(edge_len, slot_len, thickness):
        work = edge_len - 2 * thickness
        n = int(work / slot_len) if slot_len > 0 else 1
        if n < 1:
            n = 1
        if n % 2 == 0:
            n -= 1
        return (edge_len - n * slot_len) / 2

    def slot_v(Wid, L_slot, Thi, x, y):
        pts = []
        cur_x = x
        cur_t = Thi
        n = int(Wid / L_slot) + 1
        for i in range(n):
            pts.append([cur_x, y + i * L_slot])
            cur_x -= cur_t
            cur_t = -cur_t
            pts.append([cur_x, y + i * L_slot])
        return pts

    def slot_h(Len, L_slot, Thi, x, y):
        pts = []
        cur_y = y
        cur_t = Thi
        n = int(Len / L_slot) + 1
        for i in range(1, n):
            pts.append([x + (i - 1) * L_slot, cur_y])
            pts.append([x + i * L_slot, cur_y])
            cur_y += cur_t
            cur_t = -cur_t
        return pts

    def slots_on(height, part_len, l_slot, thickness, y_off, shift_x, shift_y):
        x = (part_len - thickness) / 2
        rect = [[x, y_off],
                [x + thickness, y_off],
                [x + thickness, y_off + l_slot],
                [x, y_off + l_slot]]
        count = int((height - 2 * y_off) / (2 * l_slot) + 1)
        for i in range(count):
            pts = np.array(rect) + [shift_x, i * 2 * l_slot + shift_y]
            msp.add_lwpolyline(pts, close=True)

    # ---- Lid ----
    points_lid = [[T, 0], [T, W - T], [L - T, W - T], [L - T, 0]]
    msp.add_lwpolyline(points_lid, close=True)

    # ---- Bottom ----
    x_off = get_coords_offset(L, L_slot, T)
    y_off = get_coords_offset(W, L_slot, T)

    bottom1 = slot_v(W - 2 * y_off, L_slot, T, T, y_off)
    bottom2 = slot_h(L - 2 * x_off, L_slot, T, x_off, W - T)
    bottom3 = slot_v(W - 2 * y_off, L_slot, -T, L - T, y_off)
    bottom4 = slot_h(L - 2 * x_off, L_slot, -T, x_off, T)

    points_bottom = (bottom1 + [[T, W - T]] + bottom2 +
                     [[L - T, W - T]] + bottom3[::-1] +
                     [[L - T, T]] + bottom4[::-1] + [[T, T]])
    points_bottom = np.array(points_bottom) + [L + spacing, 0]
    msp.add_lwpolyline(points_bottom, close=True)

    slots_on(W, L, L_slot, T, y_off, L + spacing, 0)

    # ---- Back wall ----
    x_off = get_coords_offset(L, L_slot, T)
    y_off = get_coords_offset(H, L_slot, T)

    back1 = slot_v(H - 2 * y_off - 2 * T - L_slot, L_slot, -T, 0, y_off)
    back3 = slot_v(H - 2 * y_off - 2 * T - L_slot, L_slot, T, L, y_off)
    back4 = slot_h(L - 2 * x_off, L_slot, T, x_off, 0)

    back = back1 + [[0, H], [L, H]] + back3[::-1] + [[L, 0]] + back4[::-1] + [[0, 0]]
    back = np.array(back) + [0, W + spacing]
    msp.add_lwpolyline(back, close=True)

    slots_on(H - 2 * T, L, L_slot, T, y_off + T, 0, W + spacing)

    # ---- Front wall ----
    x_off = get_coords_offset(L, L_slot, T)
    y_off = get_coords_offset(H, L_slot, T)

    front1 = slot_v(H - 2 * y_off - 2 * T - L_slot, L_slot, -T, 0, y_off)
    front2 = [[T, H - T], [T, H - 2 * T], [L - T, H - 2 * T], [L - T, H - T]]
    front3 = slot_v(H - 2 * y_off - 2 * T - L_slot, L_slot, T, L, y_off)
    front4 = slot_h(L - 2 * x_off, L_slot, T, x_off, 0)

    front = front1 + [[0, H - T]] + front2 + [[L, H - T]] + front3[::-1] + [[L, 0]] + front4[::-1] + [[0, 0]]
    front = np.array(front) + [L + spacing, W + spacing]
    msp.add_lwpolyline(front, close=True)

    slots_on(H - 2 * T, L, L_slot, T, y_off + T, L + spacing, W + spacing)

    # ---- Divider ----
    y_off += T
    x_off = get_coords_offset(W, L_slot, T)
    H_divider = H - 2 * T

    divider1 = slot_v(H_divider - 2 * y_off, L_slot, -T, W - T, y_off)

    R = W / 8

    divider2 = slot_h(W - 2 * x_off, L_slot, T, x_off, 0)

    divider3 = slot_v(H_divider - 2 * y_off, L_slot, T, T, y_off)

    divider = [[W - 3 * R, H_divider], [W - T, H_divider]] + divider1[::-1] + [[W - T, T], [W - x_off, T]] + divider2[::-1] + [[x_off, T], [T, T]] + divider3 + [[T, H_divider], [3 * R, H_divider]]

    divider = np.array(divider) + [2 * (W + spacing), W + H + 2 * spacing]

    msp.add_lwpolyline(
        divider,
        close = 0
    )

    msp.add_arc(
        center=(2 * (W + spacing) + W / 2, W + H + 2 * spacing + H_divider),
        radius=R,
        start_angle=180,
        end_angle=0,
    )

    # ---- Side walls ----
    x_off = get_coords_offset(W, L_slot, T)
    y_off = get_coords_offset(H, L_slot, T)

    side1 = slot_v(H - 2 * y_off - 2 * T - L_slot, L_slot, T, T, y_off)
    side2 = slot_h(W - 2 * x_off, L_slot, T, x_off, H - T)
    side3 = slot_v(H - 2 * y_off - 2 * T - L_slot, L_slot, -T, W - T, y_off)
    side4 = slot_h(W - 2 * x_off, L_slot, -T, x_off, T)

    side = (side1 + [[T, H], [x_off, H]] + side2 +
            [[W - x_off, H], [W - T, H]] + side3[::-1] +
            [[W - T, 0], [W - x_off, 0]] + side4[::-1] +
            [[x_off, 0], [T, 0]])
    side_l = np.array(side) + [0, W + H + 2 * spacing]
    msp.add_lwpolyline(side_l, close=True)

    side_r = np.array(side) + [W + spacing, W + H + 2 * spacing]
    msp.add_lwpolyline(side_r, close=True)

    # ---- Limiters ----
    x_off = get_coords_offset(W, L_slot, T)
    y_off = get_coords_offset(2 * T, L_slot, T)

    lim1 = slot_h(W - 2 * x_off, L_slot, -T, x_off, 3 * T)
    lim = lim1 + [[W - x_off, 2 * T], [W - T, 2 * T], [W - T, 0], [T, 0], [T, 2 *T], [x_off, 2 * T]]
    lim_l = np.array(lim) + [0, W + 2 * H + 3 * spacing]
    lim_r = np.array(lim) + [W + spacing, W + 2 * H + 3 * spacing]
    msp.add_lwpolyline(lim_l, close=True)
    msp.add_lwpolyline(lim_r, close=True)

    doc.saveas(filename)
    print(f"Чертёж сохранён: {filename}")
    return filename