import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
from facial_recognition import init_db, register_face_with_id, recognize_once


def handle_register():
    user_id = simpledialog.askstring("Cadastro", "Digite o ID para esse rosto:")
    if not user_id:
        return

    def process():
        ok = register_face_with_id(user_id)
        if ok:
            messagebox.showinfo("Sucesso", f"Rosto salvo com ID: {user_id}")
        else:
            messagebox.showerror("Erro", "Falha ao cadastrar rosto.")

    threading.Thread(target=process).start()


def handle_recognition():
    def process():
        result = recognize_once()
        if result:
            messagebox.showinfo("Reconhecido", f"Rosto reconhecido: {result}")
        else:
            messagebox.showinfo("Cancelado", "Reconhecimento não concluído.")

    threading.Thread(target=process).start()


def main():
    init_db()

    root = tk.Tk()
    root.title("Reconhecimento Facial")
    root.geometry("300x200")

    tk.Label(root, text="Facial AI", font=("Arial", 16)).pack(pady=10)

    tk.Button(root, text="Cadastrar novo rosto", width=25, command=handle_register).pack(pady=5)
    tk.Button(root, text="Iniciar reconhecimento", width=25, command=handle_recognition).pack(pady=5)
    tk.Button(root, text="Sair", width=25, command=root.quit).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
