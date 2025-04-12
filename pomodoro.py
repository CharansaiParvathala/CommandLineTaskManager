# pomodoro.py
import time
from config import POMODORO_DURATION
from ui import console

def start_pomodoro(minutes=POMODORO_DURATION):
    console.print(f"[yellow]Starting {minutes}-minute Pomodoro...[/yellow]")
    time.sleep(minutes * 60)
    console.print("[green]Pomodoro complete! Take a break.[/green]")