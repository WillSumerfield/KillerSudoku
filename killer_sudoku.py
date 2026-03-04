import tkinter as tk
import colorsys

CELL_SIZE = 65
PADDING = 20
CANVAS_SIZE = PADDING * 2 + 9 * CELL_SIZE
CELL_RADIUS = 8
CELL_MARGIN = 2
CAGE_INSET = 8

# Known valid Sudoku solution
GRID = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

_CAGE_CELLS = [
    [(0,0),(0,1)],
    [(0,2),(0,3),(0,4)],
    [(0,5),(1,5)],
    [(0,6),(1,6)],
    [(0,7),(0,8),(1,8)],
    [(1,0),(2,0)],
    [(1,1),(1,2),(2,2)],
    [(1,3),(1,4)],
    [(1,7),(2,7)],
    [(2,1),(3,1)],
    [(2,3),(2,4),(2,5)],
    [(2,6),(3,6)],
    [(2,8),(3,8)],
    [(3,0),(4,0)],
    [(3,2),(4,2)],
    [(3,3),(3,4),(3,5)],
    [(3,7),(4,7)],
    [(4,1),(5,1)],
    [(4,3),(4,4),(4,5)],
    [(4,6),(5,6)],
    [(4,8),(5,8)],
    [(5,0),(6,0)],
    [(5,2),(6,2)],
    [(5,3),(5,4),(5,5)],
    [(5,7),(6,7)],
    [(6,1),(7,1)],
    [(6,3),(6,4),(6,5)],
    [(6,6),(7,6)],
    [(6,8),(7,8)],
    [(7,0),(8,0)],
    [(7,2),(8,2)],
    [(7,3),(7,4),(7,5)],
    [(7,7),(8,7)],
    [(8,1),(8,3)],
    [(8,4),(8,5),(8,6)],
    [(8,8),],
]

CAGES = [
    {"cells": cells, "sum": sum(GRID[r][c] for r, c in cells)}
    for cells in _CAGE_CELLS
]

cell_to_cage = {}
for i, cage in enumerate(CAGES):
    for cell in cage["cells"]:
        cell_to_cage[cell] = i


def _pastel(hue):
    r, g, b = colorsys.hls_to_rgb(hue % 1.0, 0.88, 0.55)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

CAGE_COLORS = [_pastel(i * 0.618033988) for i in range(len(CAGES))]


def round_rect(canvas, x1, y1, x2, y2, r=8, **kwargs):
    pts = [
        x1+r, y1,   x2-r, y1,
        x2,   y1,   x2,   y1+r,
        x2,   y2-r, x2,   y2,
        x2-r, y2,   x1+r, y2,
        x1,   y2,   x1,   y2-r,
        x1,   y1+r, x1,   y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


def cell_xy(r, c):
    x = PADDING + c * CELL_SIZE
    y = PADDING + r * CELL_SIZE
    return x, y


def draw_board(canvas):
    # 1. Rounded pastel cell backgrounds
    m = CELL_MARGIN
    for r in range(9):
        for c in range(9):
            x, y = cell_xy(r, c)
            color = CAGE_COLORS[cell_to_cage[(r, c)]]
            round_rect(canvas, x+m, y+m, x+CELL_SIZE-m, y+CELL_SIZE-m,
                       r=CELL_RADIUS, fill=color, outline="")

    # 2. Cage borders (dashed, inset from cell edge)
    I = CAGE_INSET
    for r in range(9):
        for c in range(9):
            x, y = cell_xy(r, c)
            cage_id = cell_to_cage[(r, c)]
            kw = dict(fill="#777", width=1.5, dash=(4, 3))
            if r == 0 or cell_to_cage.get((r-1, c), -1) != cage_id:
                canvas.create_line(x+I, y+I, x+CELL_SIZE-I, y+I, **kw)
            if c == 0 or cell_to_cage.get((r, c-1), -1) != cage_id:
                canvas.create_line(x+I, y+I, x+I, y+CELL_SIZE-I, **kw)
            if r == 8 or cell_to_cage.get((r+1, c), -1) != cage_id:
                canvas.create_line(x+I, y+CELL_SIZE-I, x+CELL_SIZE-I, y+CELL_SIZE-I, **kw)
            if c == 8 or cell_to_cage.get((r, c+1), -1) != cage_id:
                canvas.create_line(x+CELL_SIZE-I, y+I, x+CELL_SIZE-I, y+CELL_SIZE-I, **kw)

    # 3. Thin cell grid lines
    for i in range(10):
        x = PADDING + i * CELL_SIZE
        canvas.create_line(x, PADDING, x, PADDING + 9 * CELL_SIZE, fill="#ccc", width=1)
        canvas.create_line(PADDING, x, PADDING + 9 * CELL_SIZE, x, fill="#ccc", width=1)

    # 4. Thick 3x3 box borders
    for i in range(0, 10, 3):
        x = PADDING + i * CELL_SIZE
        canvas.create_line(x, PADDING, x, PADDING + 9 * CELL_SIZE, fill="#333", width=3)
        canvas.create_line(PADDING, x, PADDING + 9 * CELL_SIZE, x, fill="#333", width=3)

    # 5. Cage sum labels
    for cage in CAGES:
        top_left = min(cage["cells"])
        r, c = top_left
        x, y = cell_xy(r, c)
        canvas.create_text(x + 11, y + 11, text=str(cage["sum"]),
                           anchor="nw", font=("Arial", 8, "bold"), fill="#555")

    # 6. Cell values
    for r in range(9):
        for c in range(9):
            x, y = cell_xy(r, c)
            canvas.create_text(x + CELL_SIZE // 2, y + CELL_SIZE // 2,
                                text=str(GRID[r][c]), font=("Arial", 20, "bold"), fill="#222")


def main():
    root = tk.Tk()
    root.title("Killer Sudoku")
    root.resizable(False, False)
    canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
    canvas.pack()
    draw_board(canvas)
    root.mainloop()


if __name__ == "__main__":
    main()
