import cv2
import tkinter as tk
from tkinter import Label, Button, Frame
from PIL import Image, ImageTk
import mediapipe as mp
import random

# Inicializar MediaPipe para detección de manos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Inicializar la captura de video
cap = cv2.VideoCapture(0)

# Crear la ventana principal
root = tk.Tk()
root.title("Interfaz de Cámara")
root.geometry("850x550")

# Crear un Label para la cámara (izquierda)
video_label = Label(root, bg="gray", width=320, height=320)
video_label.grid(row=0, column=0, padx=10, pady=10)

# Crear un botón al lado derecho (por ahora no hace nada)
start_button = Button(root, text="Iniciar Juego", font=("Arial", 14), command=lambda: start_countdown(3))
start_button.grid(row=0, column=1, padx=10, pady=10)

# Crear un panel en la parte inferior
panel2 = Frame(root, width=200, height=100, bg="lightblue")
panel2.grid(row=1, column=1, padx=10, pady=10)


panel1 = Frame(root, width=200, height=100, bg="blue")
panel1.grid(row=1, column=0, padx=10, pady=10)
txt_eleccion_usuario = Label(panel1, text="Tu: ", font=("Arial", 16), bg="blue", fg="white")
txt_eleccion_usuario.pack() 

panel3 = Frame(root, width=200, height=100, bg="lightgreen")
panel3.grid(row=1, column=2, padx=10, pady=10)
txt_eleccion_maquina = Label(panel3, text="Máquina: ", font=("Arial", 16), bg="lightgreen", fg="black")
txt_eleccion_maquina.pack()

panel4 = Frame(root, width=600, height=100, bg="gray")  # Resultado
panel4.grid(row=2, column=1, columnspan=1, padx=10, pady=10)

resultado_label = Label(panel4, text="", font=("Arial", 20), bg="gray", fg="white")
resultado_label.pack()

countdown_label = Label(panel2, text="", font=("Arial", 24), bg="lightgray")
countdown_label.pack()

choice_label = Label(root, text="Esperando...", font=("Arial", 20), bg="white")
choice_label.grid(row=0, column=2, padx=10, pady=10)

# Función para actualizar la cámara en Tkinter
def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)  # Voltear para que sea espejo
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir BGR a RGB

        # Procesar la imagen con MediaPipe
        results = hands.process(frame_rgb)
        eleccion_usuario = "?"

        # Dibujar detección de manos y evaluar el gesto
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                       mp_draw.DrawingSpec(color=(225, 234, 0), thickness=7, circle_radius=5),
                                       mp_draw.DrawingSpec(color=(225, 100, 0), thickness=7))

                # Obtener coordenadas de los dedos
                corazon = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
                junta_corazon = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y
                indice = hand_landmarks.landmark[8].y
                junta_indice = hand_landmarks.landmark[5].y
                anular = hand_landmarks.landmark[16].y
                junta_anular = hand_landmarks.landmark[13].y
                menique = hand_landmarks.landmark[20].y
                junta_menique = hand_landmarks.landmark[17].y
                pulgar = hand_landmarks.landmark[4].y

                # Evaluar gestos
                if pulgar < corazon and pulgar < indice and pulgar < menique and pulgar < anular:
                    eleccion_usuario = "Piedra"
                elif menique > junta_menique and anular > junta_anular and indice< junta_indice and corazon<junta_corazon:
                   eleccion_usuario = "Tijera"
                elif menique < junta_menique and anular < junta_anular and corazon < junta_corazon and indice < junta_indice:
                    eleccion_usuario ="Papel"
                else:
                    eleccion_usuario ="no identificado"


        txt_eleccion_usuario.config(text=f"Tu elección: {eleccion_usuario}")
        
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        # Convertir la imagen con dibujos a formato Tkinter
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        # Mostrar la imagen en el Label
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    # Volver a llamar a la función después de 10ms
    root.after(10, update_frame)

def start_countdown(count):
    if count > 0:
        countdown_label.config(text=str(count))  # Actualizar la etiqueta con el número
        root.after(1000, start_countdown, count - 1)  # Llamar a la función después de 1 segundo
    else:
        countdown_label.config(text="¡YA!") 
        select_random_choice() 


ultima_eleccion_maquina = None 


def select_random_choice():
    global choice_image, ultima_eleccion_maquina  

    opciones = ["Piedra", "Papel", "Tijera"]

    # Evitar la misma elección consecutiva
    nueva_eleccion = random.choice(opciones)
    while nueva_eleccion == ultima_eleccion_maquina:
        nueva_eleccion = random.choice(opciones)

    ultima_eleccion_maquina = nueva_eleccion  # Guardar la nueva elección
    txt_eleccion_maquina.config(text=f"Máquina: {nueva_eleccion}")

    imagenes = {
        "Piedra": "piedra.png",
        "Papel": "papel.png",
        "Tijera": "tijera.png"
    }

    ruta_imagen = imagenes.get(nueva_eleccion)
    if ruta_imagen:
        imagen_pil = Image.open(ruta_imagen).convert("RGBA")  # Asegurar canal alfa
        
        # Convertir fondo blanco a transparente
        datos = imagen_pil.getdata()
        nueva_imagen = [(255, 255, 255, 0) if (r > 200 and g > 200 and b > 200) else (r, g, b, a) for (r, g, b, a) in datos]

        imagen_pil.putdata(nueva_imagen)

        # Redimensionar imagen y convertir a formato Tkinter
        imagen_pil = imagen_pil.resize((320, 320), Image.Resampling.LANCZOS)
        choice_image = ImageTk.PhotoImage(imagen_pil)

        choice_label.config(image=choice_image, text="")
        choice_label.image = choice_image  # Fijar imagen en memoria

    determinar_ganador(nueva_eleccion)


def determinar_ganador(eleccion_maquina):
    eleccion_usuario = txt_eleccion_usuario.cget("text").split(": ")[1]
    
    if eleccion_usuario == eleccion_maquina:
        resultado = "¡Empate!"
    elif (eleccion_usuario == "Piedra" and eleccion_maquina == "Tijera") or \
         (eleccion_usuario == "Papel" and eleccion_maquina == "Piedra") or \
         (eleccion_usuario == "Tijera" and eleccion_maquina == "Papel"):
        resultado = "¡Ganaste!"
    else:
        resultado = "¡Perdiste!"
    
    resultado_label.config(text=resultado)
# Iniciar la actualización de la cámara
update_frame()

# Ejecutar la interfaz
root.mainloop()

# Liberar la cámara cuando se cierra la ventana
cap.release()
cv2.destroyAllWindows()
