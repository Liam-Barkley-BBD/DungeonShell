import os

ESC = "\x1B"

TERM_SIZE = os.get_terminal_size()

def move_to(x: int, y: int):
    print(f"{ESC}[{y};{x}H", end='', flush=True)

def move_to_col(col: int):
    print(f"{ESC}[{col}G", end='', flush=True)

def move_up(lines: int = 1):
    print(f"{ESC}[{lines}A", end='', flush=True)

def move_down(lines: int = 1):
    print(f"{ESC}[{lines}B", end='', flush=True)

def move_right(cols: int = 1):
    print(f"{ESC}[{cols}C", end='', flush=True)

def move_left(cols: int = 1):
    print(f"{ESC}[{cols}D", end='', flush=True)

def erase_cursor_to_line_end():
    print(f"{ESC}[0K", end='', flush=True)

def erase_line_start_to_cursor():
    print(f"{ESC}[1K", end='', flush=True)

def erase_line():
    print(f"{ESC}[2K", end='', flush=True)
