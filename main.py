import customtkinter as ctk
from gui.main_window import ClinicaApp

def main():
    # Apenas garantindo que a janela principal seja criada com ctk
    root = ctk.CTk() 
    app = ClinicaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()