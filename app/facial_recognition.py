import cv2
import face_recognition
import sqlite3
import pickle
import os
import numpy as np

DB_PATH = "app/faces.db"

def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faces (
            id TEXT PRIMARY KEY,
            embedding BLOB
        )
    ''')
    conn.commit()
    conn.close()

def save_face_embedding(user_id, encoding):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    data = pickle.dumps(encoding)
    cursor.execute("INSERT OR REPLACE INTO faces (id, encoding) VALUES (?, ?)", (user_id, data))
    conn.commit()
    conn.close()

def load_all_embeddings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, embedding FROM faces")
    rows = cursor.fetchall()
    conn.close()

    ids = []
    encodings = []

    for row in rows:
        ids.append(row[0])
        encodings.append(pickle.loads(row[1]))

    return ids, encodings

def match_face(encoding, known_encodings, tolerance=0.6):
    if not known_encodings:
        return None
    distances = face_recognition.face_distance(known_encodings, encoding)
    best_match_index = np.argmin(distances)
    if distances[best_match_index] < tolerance:
        return best_match_index
    return None

def capture_and_register(user_id):
    cap = cv2.VideoCapture(0)
    print("Mostre seu rosto para o cadastro...")

    while True:
        ret, frame = cap.read()
        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if face_encodings:
            save_face_embedding(user_id, face_encodings[0])
            print(f"[✓] Rosto registrado com ID: {user_id}")
            break

        cv2.imshow("Cadastro", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def recognize_loop():
    ids, encodings = load_all_embeddings()

    cap = cv2.VideoCapture(0)
    print("Iniciando reconhecimento...")

    while True:
        ret, frame = cap.read()
        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            match_index = match_face(face_encoding, encodings)
            name = "Desconhecido"

            if match_index is not None:
                name = ids[match_index]
                print(f"[!] Rosto reconhecido: {name}")

            # Draw box
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            # Label
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Reconhecimento Facial", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def recognize_once():
    ids, encodings = load_known_faces()
    if not encodings:
        print("[!] Nenhum rosto conhecido cadastrado.")
        return None

    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("[ERRO] Não foi possível acessar a câmera.")
        return None

    print("Iniciando reconhecimento...")

    reconhecido = None
    while not reconhecido:
        ret, frame = video.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            match_index = match_face(face_encoding, encodings)
            if match_index is not None:
                reconhecido = ids[match_index]
                print(f"[✓] Rosto reconhecido: {reconhecido}")
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, reconhecido, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.imshow("Reconhecimento Facial", frame)
                cv2.waitKey(2000)
                break

        if not reconhecido:
            cv2.imshow("Reconhecimento Facial - ESC para sair", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    video.release()
    cv2.destroyAllWindows()
    return reconhecido

def register_face_with_id(user_id: str):
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("[ERRO] Não foi possível acessar a câmera.")
        return False

    print("[INFO] Posicione o rosto e pressione 'q' para capturar.")
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
        return False

    encoding = face_recognition.face_encodings(rgb_frame, locations)[0]
    save_face_embedding(user_id, encoding)
    print(f"[OK] Rosto salvo com ID '{user_id}'.")

    video.release()
    cv2.destroyAllWindows()
    return True

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces
                 (id TEXT PRIMARY KEY, encoding BLOB)''')
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

if __name__ == "__main__":
    create_table()

    print("\n1 - Cadastrar novo rosto")
    print("2 - Iniciar reconhecimento")
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        uid = input("Digite o ID do usuário: ")
        capture_and_register(uid)
    elif opcao == "2":
        recognize_loop()
    else:
        print("Opção inválida.")
