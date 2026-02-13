"""Sudoku UI mockup built with tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class SudokuMockupApp:
    GRID_SIZE = 9
    MIN_CELL_SIZE = 42
    MAX_CELL_SIZE = 88
    BOARD_PADDING = 14

    BG_COLOR = "#F6F7FB"
    BOARD_BG = "#FFFFFF"
    SELECT_COLOR = "#DCEBFF"
    BLOCK_LINE_COLOR = "#3B4252"
    CELL_LINE_COLOR = "#C5CAD6"
    FIXED_TEXT_COLOR = "#1F2A44"
    USER_TEXT_COLOR = "#111111"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sudoku (Tkinter)")
        self.root.geometry("900x700")
        self.root.minsize(800, 620)
        self.root.configure(bg=self.BG_COLOR)

        self.selected: tuple[int, int] | None = None
        self.status_var = tk.StringVar(value="モックアップ準備完了")
        self.time_var = tk.StringVar(value="00:00")
        self.mistake_var = tk.StringVar(value="0")
        self.filled_var = tk.StringVar(value="0 / 81")

        self.canvas: tk.Canvas
        self.cell_size = 58

        self._build_style()
        self._build_layout()
        self._draw_board()

    def _build_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Toolbar.TFrame", background=self.BG_COLOR)
        style.configure("Main.TFrame", background=self.BG_COLOR)
        style.configure("Panel.TLabelframe", background=self.BG_COLOR)
        style.configure("Panel.TLabelframe.Label", background=self.BG_COLOR, font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        wrapper = ttk.Frame(self.root, padding=12, style="Main.TFrame")
        wrapper.pack(fill="both", expand=True)

        self._build_toolbar(wrapper)

        content = ttk.Frame(wrapper, style="Main.TFrame")
        content.pack(fill="both", expand=True, pady=(10, 8))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.rowconfigure(0, weight=1)

        board_frame = ttk.Frame(content, style="Main.TFrame")
        board_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        board_frame.rowconfigure(0, weight=1)
        board_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            board_frame,
            bg=self.BOARD_BG,
            highlightthickness=0,
            relief="flat",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self._build_info_panel(content)
        self._build_statusbar(wrapper)

    def _build_toolbar(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent, style="Toolbar.TFrame")
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="新規ゲーム", command=lambda: self._set_status("新規ゲーム（モック）")).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="リセット", command=lambda: self._set_status("リセット（モック）")).pack(side="left", padx=6)
        ttk.Button(toolbar, text="チェック", command=lambda: self._set_status("チェック（モック）")).pack(side="left", padx=6)
        ttk.Button(toolbar, text="ヒント", command=lambda: self._set_status("ヒント（モック）")).pack(side="left", padx=6)

        ttk.Label(toolbar, text="難易度:").pack(side="left", padx=(16, 6))
        self.difficulty = tk.StringVar(value="Normal")
        ttk.Combobox(
            toolbar,
            textvariable=self.difficulty,
            values=["Easy", "Normal", "Hard"],
            width=10,
            state="readonly",
        ).pack(side="left")

        self.memo_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(toolbar, text="メモモード", variable=self.memo_mode).pack(side="left", padx=(16, 0))

    def _build_info_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.LabelFrame(parent, text="ゲーム情報", padding=10, style="Panel.TLabelframe")
        panel.grid(row=0, column=1, sticky="ns")

        ttk.Label(panel, text="経過時間", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(panel, textvariable=self.time_var).pack(anchor="w", pady=(0, 8))

        ttk.Label(panel, text="ミス回数", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(panel, textvariable=self.mistake_var).pack(anchor="w", pady=(0, 8))

        ttk.Label(panel, text="入力済み", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(panel, textvariable=self.filled_var).pack(anchor="w", pady=(0, 12))

        ttk.Separator(panel).pack(fill="x", pady=6)
        ttk.Label(panel, text="操作ガイド", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 4))
        guide = (
            "・クリックでセル選択\n"
            "・1〜9 で入力（予定）\n"
            "・Backspace で削除（予定）\n"
            "・M でメモモード切替（予定）"
        )
        ttk.Label(panel, text=guide, justify="left").pack(anchor="w")

    def _build_statusbar(self, parent: ttk.Frame) -> None:
        status = ttk.Frame(parent, style="Toolbar.TFrame")
        status.pack(fill="x", pady=(6, 0))
        ttk.Label(status, textvariable=self.status_var).pack(side="left")

    def _on_canvas_resize(self, event: tk.Event) -> None:
        board_side = min(event.width, event.height)
        usable = max(1, board_side - self.BOARD_PADDING * 2)
        new_size = max(self.MIN_CELL_SIZE, min(self.MAX_CELL_SIZE, usable // self.GRID_SIZE))
        if new_size != self.cell_size:
            self.cell_size = new_size
            self._draw_board()

    def _draw_board(self) -> None:
        self.canvas.delete("all")

        board_len = self.GRID_SIZE * self.cell_size
        canvas_size = board_len + self.BOARD_PADDING * 2
        self.canvas.configure(scrollregion=(0, 0, canvas_size, canvas_size))

        if self.selected:
            row, col = self.selected
            x1, y1, x2, y2 = self._cell_rect(row, col)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.SELECT_COLOR, outline="")

        for i in range(self.GRID_SIZE + 1):
            x = self.BOARD_PADDING + i * self.cell_size
            y = self.BOARD_PADDING + i * self.cell_size
            width = 3 if i % 3 == 0 else 1

            self.canvas.create_line(
                x,
                self.BOARD_PADDING,
                x,
                self.BOARD_PADDING + board_len,
                fill=self.BLOCK_LINE_COLOR if i % 3 == 0 else self.CELL_LINE_COLOR,
                width=width,
            )
            self.canvas.create_line(
                self.BOARD_PADDING,
                y,
                self.BOARD_PADDING + board_len,
                y,
                fill=self.BLOCK_LINE_COLOR if i % 3 == 0 else self.CELL_LINE_COLOR,
                width=width,
            )

        fixed_numbers = {
            (0, 0): 5,
            (0, 1): 3,
            (0, 4): 7,
            (1, 0): 6,
            (1, 3): 1,
            (2, 1): 9,
            (4, 4): 5,
            (6, 7): 8,
            (8, 8): 9,
        }
        mock_user_numbers = {(3, 3): 8, (4, 1): 2, (7, 5): 4}

        value_font_size = max(14, int(self.cell_size * 0.34))
        for (row, col), value in fixed_numbers.items():
            cx, cy = self._cell_center(row, col)
            self.canvas.create_text(cx, cy, text=str(value), font=("Segoe UI", value_font_size, "bold"), fill=self.FIXED_TEXT_COLOR)

        for (row, col), value in mock_user_numbers.items():
            cx, cy = self._cell_center(row, col)
            self.canvas.create_text(cx, cy, text=str(value), font=("Segoe UI", value_font_size), fill=self.USER_TEXT_COLOR)

    def _on_canvas_click(self, event: tk.Event) -> None:
        col = (event.x - self.BOARD_PADDING) // self.cell_size
        row = (event.y - self.BOARD_PADDING) // self.cell_size

        if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
            self.selected = (int(row), int(col))
            self._set_status(f"セル R{row + 1}C{col + 1} を選択中")
            self._draw_board()

    def _cell_rect(self, row: int, col: int) -> tuple[int, int, int, int]:
        x1 = self.BOARD_PADDING + col * self.cell_size
        y1 = self.BOARD_PADDING + row * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        return x1, y1, x2, y2

    def _cell_center(self, row: int, col: int) -> tuple[int, int]:
        x1, y1, x2, y2 = self._cell_rect(row, col)
        return (x1 + x2) // 2, (y1 + y2) // 2

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)


def main() -> None:
    root = tk.Tk()
    SudokuMockupApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
