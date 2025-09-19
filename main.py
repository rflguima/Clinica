import tkinter as tk
from gui.main_window import ClinicaApp

def main():
    root = tk.Tk()
    app = ClinicaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()