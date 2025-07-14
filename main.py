
from modules.ui import CollegeApp
import ttkbootstrap as ttk

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = CollegeApp(root)
    root.mainloop()
