import cv2
import face_recognition
import sqlite3
import os
import pickle

DB_PATH = "app/faces.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces
                 (id TEXT PRIMARY KEY, encoding BLOB)''')
    conn.commit()
    conn.close()


def save_face_encoding(id, encoding):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO faces VALUES (?, ?)", (id, pickle.dumps(encoding)))
    conn.commit()
    conn.close()


def load_known_faces():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM faces")
    data = c.fetchall()
    conn.close()

    ids = []
    encodings = []

    for id, encoding_blob in data:
        ids.append(id)
        encodings.append(pickle.loads(encoding_blob))

    return ids, encodings


def register_face():
    video = cv2.VideoCapture(0)

    print("[INFO] Posicione o rosto na frente da câmera. Pressione 'q' para capturar.")
    while True:
        ret, frame = video.read()
        if not ret:
            continue

        cv2.imshow("Captura de rosto - pressione 'q'", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb_frame)

    if len(locations) != 1:
        print("[ERRO] Nenhum rosto ou múltiplos rostos detectados.")
        video.release()
        cv2.destroyAllWindows()
        return

    encoding = face_recognition.face_encodings(rgb_frame, locations)[0]
    user_id = input("Digite um ID para esse rosto: ")
    save_face_encoding(user_id, encoding)
    print(f"[OK] Rosto salvo com ID '{user_id}'.")

    video.release()
    cv2.destroyAllWindows()


def match_face(encoding, known_encodings):
    if not known_encodings:
        return None

    results = face_recognition.compare_faces(known_encodings, encoding)
    for i, match in enumerate(results):
        if match:
            return i
    return None


def recognize_loop():
    ids, encodings = load_known_faces()
    if not encodings:
        print("[!] Nenhum rosto conhecido cadastrado.")
        return

    video = cv2.VideoCapture(0)
    print("Iniciando reconhecimento...")

    while True:
        ret, frame = video.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        try:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        except Exception as e:
            print(f"[!] Erro ao codificar rosto: {e}")
            face_encodings = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            match_index = match_face(face_encoding, encodings)
            name = "Desconhecido"

            if match_index is not None:
                name = ids[match_index]
                print(f"[✓] Rosto reconhecido: {name}")

            # Draw box
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Reconhecimento Facial - Pressione ESC para sair", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    video.release()
    cv2.destroyAllWindows()


def main():
    init_db()
    while True:
        print("\n1 - Cadastrar novo rosto")
        print("2 - Iniciar reconhecimento")
        print("0 - Sair")
        choice = input("Escolha uma opção: ")

        if choice == "1":
            register_face()
        elif choice == "2":
            recognize_loop()
        elif choice == "0":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
