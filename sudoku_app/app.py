"""Sudoku game built with tkinter."""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

Grid = list[list[int]]
NotesGrid = list[list[set[int]]]


@dataclass
class GameState:
    """Runtime state for the current Sudoku game."""

    puzzle: Grid
    solution: Grid
    user_grid: Grid
    notes: NotesGrid
    fixed_mask: list[list[bool]]
    mistakes: int = 0
    elapsed_seconds: int = 0
    difficulty: str = "normal"
    started_at: float = field(default_factory=time.time)
    hints_used: int = 0


PUZZLES: dict[str, list[dict[str, Grid]]] = {
    "easy": [
        {
            "puzzle": [
                [5, 0, 4, 6, 0, 8, 9, 1, 2],
                [6, 7, 0, 1, 9, 5, 0, 4, 8],
                [1, 9, 8, 3, 0, 2, 0, 6, 7],
                [8, 0, 9, 7, 6, 1, 4, 0, 3],
                [4, 2, 6, 0, 5, 0, 7, 9, 0],
                [7, 0, 3, 9, 2, 4, 8, 0, 6],
                [9, 6, 1, 5, 0, 7, 2, 8, 4],
                [2, 8, 0, 4, 1, 9, 0, 3, 5],
                [3, 4, 0, 2, 0, 6, 1, 0, 9],
            ],
            "solution": [
                [5, 3, 4, 6, 7, 8, 9, 1, 2],
                [6, 7, 2, 1, 9, 5, 3, 4, 8],
                [1, 9, 8, 3, 4, 2, 5, 6, 7],
                [8, 5, 9, 7, 6, 1, 4, 2, 3],
                [4, 2, 6, 8, 5, 3, 7, 9, 1],
                [7, 1, 3, 9, 2, 4, 8, 5, 6],
                [9, 6, 1, 5, 3, 7, 2, 8, 4],
                [2, 8, 7, 4, 1, 9, 6, 3, 5],
                [3, 4, 5, 2, 8, 6, 1, 7, 9],
            ],
        }
    ],
    "normal": [
        {
            "puzzle": [
                [0, 0, 0, 2, 6, 0, 7, 0, 1],
                [6, 8, 0, 0, 7, 0, 0, 9, 0],
                [1, 9, 0, 0, 0, 4, 5, 0, 0],
                [8, 2, 0, 1, 0, 0, 0, 4, 0],
                [0, 0, 4, 6, 0, 2, 9, 0, 0],
                [0, 5, 0, 0, 0, 3, 0, 2, 8],
                [0, 0, 9, 3, 0, 0, 0, 7, 4],
                [0, 4, 0, 0, 5, 0, 0, 3, 6],
                [7, 0, 3, 0, 1, 8, 0, 0, 0],
            ],
            "solution": [
                [4, 3, 5, 2, 6, 9, 7, 8, 1],
                [6, 8, 2, 5, 7, 1, 4, 9, 3],
                [1, 9, 7, 8, 3, 4, 5, 6, 2],
                [8, 2, 6, 1, 9, 5, 3, 4, 7],
                [3, 7, 4, 6, 8, 2, 9, 1, 5],
                [9, 5, 1, 7, 4, 3, 6, 2, 8],
                [5, 1, 9, 3, 2, 6, 8, 7, 4],
                [2, 4, 8, 9, 5, 7, 1, 3, 6],
                [7, 6, 3, 4, 1, 8, 2, 5, 9],
            ],
        }
    ],
    "hard": [
        {
            "puzzle": [
                [0, 0, 0, 0, 0, 0, 2, 0, 0],
                [0, 8, 0, 0, 0, 7, 0, 9, 0],
                [6, 0, 2, 0, 0, 0, 5, 0, 0],
                [0, 7, 0, 0, 6, 0, 0, 0, 0],
                [0, 0, 0, 9, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 2, 0, 0, 4, 0],
                [0, 0, 5, 0, 0, 0, 6, 0, 3],
                [0, 9, 0, 4, 0, 0, 0, 7, 0],
                [0, 0, 6, 0, 0, 0, 0, 0, 0],
            ],
            "solution": [
                [9, 5, 7, 6, 1, 3, 2, 8, 4],
                [4, 8, 3, 2, 5, 7, 1, 9, 6],
                [6, 1, 2, 8, 4, 9, 5, 3, 7],
                [1, 7, 8, 3, 6, 4, 9, 5, 2],
                [5, 2, 4, 9, 7, 1, 3, 6, 8],
                [3, 6, 9, 5, 2, 8, 7, 4, 1],
                [8, 4, 5, 7, 9, 2, 6, 1, 3],
                [2, 9, 1, 4, 3, 6, 8, 7, 5],
                [7, 3, 6, 1, 8, 5, 4, 2, 9],
            ],
        }
    ],
}


class SudokuApp:
    GRID_SIZE = 9
    MIN_CELL_SIZE = 42
    MAX_CELL_SIZE = 88
    BOARD_PADDING = 14

    BG_COLOR = "#F6F7FB"
    BOARD_BG = "#FFFFFF"
    SELECT_COLOR = "#DCEBFF"
    SAME_VALUE_COLOR = "#FFF4CC"
    CONFLICT_COLOR = "#FFD6D6"
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
        self.cell_size = 58
        self.conflicts: set[tuple[int, int]] = set()

        self.status_var = tk.StringVar(value="準備完了")
        self.time_var = tk.StringVar(value="00:00")
        self.mistake_var = tk.StringVar(value="0")
        self.filled_var = tk.StringVar(value="0 / 81")
        self.difficulty_var = tk.StringVar(value="Normal")
        self.memo_mode = tk.BooleanVar(value=False)

        self.state = self._new_state("normal")
        self._build_style()
        self._build_layout()
        self._bind_events()
        self._refresh_all()
        self._tick_timer()

    def _new_state(self, difficulty: str) -> GameState:
        selected = random.choice(PUZZLES[difficulty])
        puzzle = [row[:] for row in selected["puzzle"]]
        solution = [row[:] for row in selected["solution"]]
        fixed_mask = [[value != 0 for value in row] for row in puzzle]
        return GameState(
            puzzle=puzzle,
            solution=solution,
            user_grid=[row[:] for row in puzzle],
            notes=[[set() for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)],
            fixed_mask=fixed_mask,
            difficulty=difficulty,
        )

    def _build_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background=self.BG_COLOR)
        style.configure("Panel.TLabelframe", background=self.BG_COLOR)
        style.configure("Panel.TLabelframe.Label", background=self.BG_COLOR, font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        wrapper = ttk.Frame(self.root, padding=12, style="App.TFrame")
        wrapper.pack(fill="both", expand=True)

        self._build_toolbar(wrapper)

        content = ttk.Frame(wrapper, style="App.TFrame")
        content.pack(fill="both", expand=True, pady=(10, 8))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.rowconfigure(0, weight=1)

        board_frame = ttk.Frame(content, style="App.TFrame")
        board_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        board_frame.rowconfigure(0, weight=1)
        board_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(board_frame, bg=self.BOARD_BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self._build_info_panel(content)
        self._build_statusbar(wrapper)

    def _build_toolbar(self, parent: ttk.Frame) -> None:
        toolbar = ttk.Frame(parent, style="App.TFrame")
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="新規ゲーム", command=self.new_game).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="リセット", command=self.reset_game).pack(side="left", padx=6)
        ttk.Button(toolbar, text="チェック", command=self.check_board).pack(side="left", padx=6)
        ttk.Button(toolbar, text="ヒント", command=self.give_hint).pack(side="left", padx=6)

        ttk.Label(toolbar, text="難易度:").pack(side="left", padx=(16, 6))
        self.difficulty_combo = ttk.Combobox(
            toolbar,
            textvariable=self.difficulty_var,
            values=["Easy", "Normal", "Hard"],
            width=10,
            state="readonly",
        )
        self.difficulty_combo.pack(side="left")

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
        ttk.Label(
            panel,
            justify="left",
            text=(
                "・クリックでセル選択\n"
                "・1〜9 で入力\n"
                "・Backspace/Delete で削除\n"
                "・矢印キーで移動\n"
                "・M でメモモード切替\n"
                "・Ctrl+S 保存 / Ctrl+O 読込"
            ),
        ).pack(anchor="w")

    def _build_statusbar(self, parent: ttk.Frame) -> None:
        bar = ttk.Frame(parent, style="App.TFrame")
        bar.pack(fill="x", pady=(6, 0))
        ttk.Label(bar, textvariable=self.status_var).pack(side="left")

    def _bind_events(self) -> None:
        self.root.bind("<Key>", self._on_key_press)
        self.root.bind("<Control-n>", lambda _e: self.new_game())
        self.root.bind("<Control-s>", lambda _e: self.save_game())
        self.root.bind("<Control-o>", lambda _e: self.load_game())
        self.difficulty_combo.bind("<<ComboboxSelected>>", lambda _e: self.new_game())

    def _tick_timer(self) -> None:
        if self.state:
            self.state.elapsed_seconds = int(time.time() - self.state.started_at)
            self.time_var.set(self._format_time(self.state.elapsed_seconds))
        self.root.after(1000, self._tick_timer)

    def _format_time(self, sec: int) -> str:
        return f"{sec // 60:02d}:{sec % 60:02d}"

    def _refresh_all(self) -> None:
        self.conflicts = self._collect_conflicts()
        self.mistake_var.set(str(self.state.mistakes))
        filled = sum(1 for row in self.state.user_grid for value in row if value != 0)
        self.filled_var.set(f"{filled} / 81")
        self.time_var.set(self._format_time(self.state.elapsed_seconds))
        self._draw_board()

    def _on_canvas_resize(self, event: tk.Event) -> None:
        board_side = min(event.width, event.height)
        usable = max(1, board_side - self.BOARD_PADDING * 2)
        self.cell_size = max(self.MIN_CELL_SIZE, min(self.MAX_CELL_SIZE, usable // self.GRID_SIZE))
        self._draw_board()

    def _on_canvas_click(self, event: tk.Event) -> None:
        col = (event.x - self.BOARD_PADDING) // self.cell_size
        row = (event.y - self.BOARD_PADDING) // self.cell_size
        if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
            self.selected = (int(row), int(col))
            self._set_status(f"セル R{row + 1}C{col + 1} を選択中")
            self._draw_board()

    def _on_key_press(self, event: tk.Event) -> None:
        if event.keysym.lower() == "m":
            self.memo_mode.set(not self.memo_mode.get())
            self._set_status("メモモード ON" if self.memo_mode.get() else "メモモード OFF")
            return

        if self.selected is None:
            return

        row, col = self.selected
        if event.keysym in {"Up", "Down", "Left", "Right"}:
            self._move_selection(event.keysym)
            return

        if event.char in "123456789":
            self._apply_number(row, col, int(event.char))
        elif event.keysym in {"BackSpace", "Delete"}:
            self._clear_cell(row, col)

    def _move_selection(self, direction: str) -> None:
        if self.selected is None:
            return
        row, col = self.selected
        if direction == "Up":
            row = max(0, row - 1)
        elif direction == "Down":
            row = min(8, row + 1)
        elif direction == "Left":
            col = max(0, col - 1)
        elif direction == "Right":
            col = min(8, col + 1)
        self.selected = (row, col)
        self._set_status(f"セル R{row + 1}C{col + 1} を選択中")
        self._draw_board()

    def _apply_number(self, row: int, col: int, value: int) -> None:
        if self.state.fixed_mask[row][col]:
            self._set_status("固定セルは編集できません")
            return

        if self.memo_mode.get():
            notes = self.state.notes[row][col]
            if value in notes:
                notes.remove(value)
            else:
                notes.add(value)
            self._set_status(f"メモ {'追加' if value in notes else '削除'}: {value}")
        else:
            self.state.user_grid[row][col] = value
            self.state.notes[row][col].clear()
            if value != self.state.solution[row][col]:
                self.state.mistakes += 1
                self._set_status("不正解の可能性があります")
            else:
                self._set_status(f"入力: R{row + 1}C{col + 1} = {value}")

        self._refresh_all()
        self._check_completed()

    def _clear_cell(self, row: int, col: int) -> None:
        if self.state.fixed_mask[row][col]:
            self._set_status("固定セルは編集できません")
            return
        self.state.user_grid[row][col] = 0
        self.state.notes[row][col].clear()
        self._set_status(f"セル R{row + 1}C{col + 1} をクリア")
        self._refresh_all()

    def _collect_conflicts(self) -> set[tuple[int, int]]:
        conflicts: set[tuple[int, int]] = set()
        grid = self.state.user_grid
        for row in range(9):
            for col in range(9):
                value = grid[row][col]
                if value == 0:
                    continue
                peers = [(row, c) for c in range(9) if c != col]
                peers += [(r, col) for r in range(9) if r != row]
                br, bc = (row // 3) * 3, (col // 3) * 3
                peers += [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if (r, c) != (row, col)
                ]
                if any(grid[r][c] == value for r, c in peers):
                    conflicts.add((row, col))
        return conflicts

    def _check_completed(self) -> None:
        grid = self.state.user_grid
        if any(value == 0 for row in grid for value in row):
            return
        if self.conflicts:
            return
        if grid != self.state.solution:
            return
        messagebox.showinfo("クリア", f"おめでとうございます！\n時間: {self.time_var.get()}\nミス: {self.state.mistakes}")
        self._set_status("ゲームクリア")

    def _draw_board(self) -> None:
        self.canvas.delete("all")
        board_len = self.GRID_SIZE * self.cell_size

        selected_value = None
        if self.selected:
            sr, sc = self.selected
            selected_value = self.state.user_grid[sr][sc]

        for row in range(9):
            for col in range(9):
                x1, y1, x2, y2 = self._cell_rect(row, col)
                fill = self.BOARD_BG
                value = self.state.user_grid[row][col]

                if selected_value and value == selected_value:
                    fill = self.SAME_VALUE_COLOR
                if (row, col) in self.conflicts:
                    fill = self.CONFLICT_COLOR
                if self.selected == (row, col):
                    fill = self.SELECT_COLOR

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

                if value:
                    font = ("Segoe UI", max(14, int(self.cell_size * 0.34)), "bold" if self.state.fixed_mask[row][col] else "normal")
                    color = self.FIXED_TEXT_COLOR if self.state.fixed_mask[row][col] else self.USER_TEXT_COLOR
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(value), font=font, fill=color)
                elif self.state.notes[row][col]:
                    self._draw_notes(row, col)

        for i in range(self.GRID_SIZE + 1):
            w = 3 if i % 3 == 0 else 1
            color = self.BLOCK_LINE_COLOR if i % 3 == 0 else self.CELL_LINE_COLOR
            x = self.BOARD_PADDING + i * self.cell_size
            y = self.BOARD_PADDING + i * self.cell_size
            self.canvas.create_line(x, self.BOARD_PADDING, x, self.BOARD_PADDING + board_len, width=w, fill=color)
            self.canvas.create_line(self.BOARD_PADDING, y, self.BOARD_PADDING + board_len, y, width=w, fill=color)

    def _draw_notes(self, row: int, col: int) -> None:
        notes = self.state.notes[row][col]
        note_font = ("Segoe UI", max(8, int(self.cell_size * 0.14)))
        for n in range(1, 10):
            if n not in notes:
                continue
            sub_r = (n - 1) // 3
            sub_c = (n - 1) % 3
            x1, y1, _, _ = self._cell_rect(row, col)
            nx = x1 + int((sub_c + 0.5) * self.cell_size / 3)
            ny = y1 + int((sub_r + 0.5) * self.cell_size / 3)
            self.canvas.create_text(nx, ny, text=str(n), font=note_font, fill="#555")

    def _cell_rect(self, row: int, col: int) -> tuple[int, int, int, int]:
        x1 = self.BOARD_PADDING + col * self.cell_size
        y1 = self.BOARD_PADDING + row * self.cell_size
        return x1, y1, x1 + self.cell_size, y1 + self.cell_size

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def new_game(self) -> None:
        mapping = {"Easy": "easy", "Normal": "normal", "Hard": "hard"}
        difficulty = mapping.get(self.difficulty_var.get(), "normal")
        self.state = self._new_state(difficulty)
        self.selected = None
        self.conflicts.clear()
        self._set_status(f"新規ゲーム開始: {self.difficulty_var.get()}")
        self._refresh_all()

    def reset_game(self) -> None:
        self.state.user_grid = [row[:] for row in self.state.puzzle]
        self.state.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.state.mistakes = 0
        self.state.started_at = time.time()
        self.state.elapsed_seconds = 0
        self._set_status("盤面をリセットしました")
        self._refresh_all()

    def check_board(self) -> None:
        self.conflicts = self._collect_conflicts()
        if self.conflicts:
            self._set_status("衝突があります")
        else:
            self._set_status("衝突はありません")
        self._draw_board()

    def give_hint(self) -> None:
        empties = [(r, c) for r in range(9) for c in range(9) if self.state.user_grid[r][c] == 0]
        if not empties:
            self._set_status("ヒント対象の空セルがありません")
            return
        row, col = random.choice(empties)
        self.state.user_grid[row][col] = self.state.solution[row][col]
        self.state.notes[row][col].clear()
        self.state.hints_used += 1
        self._set_status(f"ヒント使用: R{row + 1}C{col + 1}（合計 {self.state.hints_used} 回）")
        self._refresh_all()
        self._check_completed()

    def save_game(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".sudoku.json",
            filetypes=[("Sudoku Save", "*.sudoku.json"), ("JSON", "*.json")],
        )
        if not path:
            return
        payload = {
            "puzzle": self.state.puzzle,
            "solution": self.state.solution,
            "user_grid": self.state.user_grid,
            "notes": [[sorted(list(cell)) for cell in row] for row in self.state.notes],
            "mistakes": self.state.mistakes,
            "elapsed_seconds": self.state.elapsed_seconds,
            "difficulty": self.state.difficulty,
        }
        try:
            Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            self._set_status("保存しました")
        except OSError as error:
            messagebox.showerror("保存失敗", f"保存に失敗しました:\n{error}")

    def load_game(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Sudoku Save", "*.sudoku.json"), ("JSON", "*.json")])
        if not path:
            return
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            self._validate_payload(payload)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror("読込失敗", f"不正データのため読込できません:\n{error}")
            return

        difficulty = payload["difficulty"]
        self.state = GameState(
            puzzle=payload["puzzle"],
            solution=payload["solution"],
            user_grid=payload["user_grid"],
            notes=[[set(cell) for cell in row] for row in payload["notes"]],
            fixed_mask=[[value != 0 for value in row] for row in payload["puzzle"]],
            mistakes=payload["mistakes"],
            elapsed_seconds=payload["elapsed_seconds"],
            difficulty=difficulty,
            started_at=time.time() - payload["elapsed_seconds"],
        )
        self.difficulty_var.set(difficulty.capitalize())
        self._set_status("セーブデータを読み込みました")
        self._refresh_all()

    def _validate_payload(self, payload: dict) -> None:
        required = {"puzzle", "solution", "user_grid", "notes", "mistakes", "elapsed_seconds", "difficulty"}
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"必須キー不足: {', '.join(sorted(missing))}")

        for key in ("puzzle", "solution", "user_grid"):
            self._validate_grid(payload[key], key)
        if len(payload["notes"]) != 9 or any(len(row) != 9 for row in payload["notes"]):
            raise ValueError("notesのサイズが不正です")
        for row in payload["notes"]:
            for cell in row:
                if any(n not in range(1, 10) for n in cell):
                    raise ValueError("notesの値が不正です")
        if payload["difficulty"] not in {"easy", "normal", "hard"}:
            raise ValueError("difficultyが不正です")

    def _validate_grid(self, grid: list[list[int]], name: str) -> None:
        if len(grid) != 9 or any(len(row) != 9 for row in grid):
            raise ValueError(f"{name}のサイズが不正です")
        for row in grid:
            for value in row:
                if not isinstance(value, int) or value not in range(10):
                    raise ValueError(f"{name}に不正値があります")


def main() -> None:
    root = tk.Tk()
    app = SudokuApp(root)

    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=False)
    file_menu.add_command(label="保存", command=app.save_game, accelerator="Ctrl+S")
    file_menu.add_command(label="読込", command=app.load_game, accelerator="Ctrl+O")
    menubar.add_cascade(label="ファイル", menu=file_menu)
    root.config(menu=menubar)

    root.mainloop()


if __name__ == "__main__":
    main()
