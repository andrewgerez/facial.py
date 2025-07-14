import customtkinter as ctk
import threading
from tkinter import simpledialog, messagebox
from facial_recognition import init_db, register_face_with_id, recognize_once

ctk.set_appearance_mode("dark")  # Modo dark
ctk.set_default_color_theme("blue")  # Tema azul moderno

class FacialApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Reconhecimento Facial")
        self.geometry("400x300")
        self.resizable(False, False)

        # Container centralizado
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.loading_label = None

        # Título
        self.title_label = ctk.CTkLabel(self, text="Facial AI", font=ctk.CTkFont(size=30, weight="bold"))
        self.title_label.grid(row=1, column=1, pady=(10, 40), sticky="n")

        # Botões
        self.register_btn = ctk.CTkButton(self, text="Cadastrar novo rosto", width=220, height=40, command=self.handle_register)
        self.register_btn.grid(row=2, column=1, pady=10)

        self.recognize_btn = ctk.CTkButton(self, text="Iniciar reconhecimento", width=220, height=40, command=self.handle_recognition)
        self.recognize_btn.grid(row=3, column=1, pady=10)

        self.exit_btn = ctk.CTkButton(self, text="Sair", width=220, height=40, fg_color="#D32F2F", hover_color="#B71C1C", command=self.quit)
        self.exit_btn.grid(row=4, column=1, pady=30)

    def show_loading(self, message="Carregando câmera..."):
        if not self.loading_label:
            self.loading_label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=14))
            self.loading_label.grid(row=5, column=1, pady=10)
        self.update_idletasks()

    def hide_loading(self):
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None
            self.update_idletasks()

    def disable_buttons(self):
        self.register_btn.configure(state="disabled")
        self.recognize_btn.configure(state="disabled")

    def enable_buttons(self):
        self.register_btn.configure(state="normal")
        self.recognize_btn.configure(state="normal")

    def handle_register(self):
        user_id = simpledialog.askstring("Cadastro", "Digite o ID para esse rosto:", parent=self)
        if not user_id:
            return

        def process():
            self.disable_buttons()
            self.show_loading()

            ok = register_face_with_id(user_id)

            self.hide_loading()
            self.enable_buttons()

            if ok:
                messagebox.showinfo("Sucesso", f"Rosto salvo com ID: {user_id}", parent=self)
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar rosto.", parent=self)

        threading.Thread(target=process, daemon=True).start()

    def handle_recognition(self):
        def process():
            self.disable_buttons()
            self.show_loading("Reconhecendo...")

            result = recognize_once()

            self.hide_loading()
            self.enable_buttons()

            if result:
                messagebox.showinfo("Reconhecido", f"Rosto reconhecido: {result}", parent=self)
            else:
                messagebox.showinfo("Cancelado", "Reconhecimento não concluído.", parent=self)

        threading.Thread(target=process, daemon=True).start()


def main():
    init_db()
    app = FacialApp()
    app.mainloop()


if __name__ == "__main__":
    main()
