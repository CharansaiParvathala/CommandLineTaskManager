# charts.py
import plotly.express as px
import pandas as pd
from ui import console

def plot_task_distribution(tasks):
    if not tasks:
        console.print("[yellow]No tasks to visualize.[/yellow]")
        return
    df = pd.DataFrame(tasks)
    fig = px.pie(df, names='status', title='Task Status Distribution')
    fig.show()

def plot_priority_bar(tasks):
    if not tasks:
        console.print("[yellow]No tasks to visualize.[/yellow]")
        return
    df = pd.DataFrame(tasks)
    fig = px.bar(df, x='priority', title='Tasks by Priority')
    fig.show()

def plot_gantt_chart(tasks):
    if not tasks:
        console.print("[yellow]No tasks to visualize.[/yellow]")
        return
    df = pd.DataFrame([
        dict(Task=t['title'], Start=t['created_at'], Finish=t['due_date'], Resource=t['status'])
        for t in tasks if t['due_date']
    ])
    if not df.empty:
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource", title="Task Timeline")
        fig.show()
    else:
        console.print("[yellow]No tasks with due dates to visualize.[/yellow]")