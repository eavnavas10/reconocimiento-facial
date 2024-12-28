# Importamos librerias
from tkinter import *
from tkinter import Tk, messagebox
import os
import cv2
import dlib
from scipy.spatial import distance
from matplotlib import pyplot
from mtcnn.mtcnn import MTCNN
import numpy as np

# Cargar los detectores de rostro y de ojos
face_detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Función para calcular la relación de aspecto del ojo (EAR)
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Umbral para detección de parpadeo
EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3

#------------------------ Crearemos una funcion que se encargara de registrar el usuario -----------------------
def registrar_usuario():
    usuario_info = usuario.get()
    contra_info = contra.get()

    archivo = open(usuario_info, "w")
    archivo.write(usuario_info + "\n")
    archivo.write(contra_info)
    archivo.close()

    #Limpiaremos los text variable
    usuario_entrada.delete(0, END)
    contra_entrada.delete(0, END)

    #Mensaje al usuario que su registro ha sido exitoso
    Label(pantalla1, text = "Registro convencional exitoso", fg = "green", font = ("Calibri",11)).pack()   

#------------------------------ Funcion para almacenar el registro facial --------------------------------------    
def registro_facial():
    
    # Iniciar la captura el rostro
    cap = cv2.VideoCapture(0)
    while(True):
        ret,frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray)
        
        # Mostrar el número de rostros detectados en el frame
        num_faces = len(faces)
        cv2.putText(frame, f"Rostros detectados: {num_faces}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Reiniciar el contador de parpadeos si hay más de un rostro
        if num_faces > 1:
            cv2.putText(frame, "Demasiados rostros en pantalla", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        elif num_faces < 1:
            cv2.putText(frame, "No hay rostros por examinar", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)    
        elif num_faces == 1:
            capture_frame = frame.copy()
        
        #Muestra ventana
        cv2.imshow('Registro Facial',frame)
        
        #Rompe el video
        if cv2.waitKey(1) & 0xFF == ord("q") and num_faces == 1:
            break
        
    usuario_img = usuario.get()
    cv2.imwrite(usuario_img+".jpg",frame)
    cap.release()
    cv2.destroyAllWindows()

    usuario_entrada.delete(0, END)
    contra_entrada.delete(0, END)
    root = Tk()
    root.withdraw()  # Oculta la ventana principal
    messagebox.showinfo("Información", "Registro facial exitoso")
    pantalla1.destroy()

    # Detectamos el rostro y exportamos los pixeles
    def reg_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1,y1,ancho, alto = lista_resultados[i]['box']
            x2,y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i+1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg,(150,200), interpolation = cv2.INTER_CUBIC)
            cv2.imwrite(usuario_img+".jpg",cara_reg)
            pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    img = usuario_img+".jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    reg_rostro(img, caras)   
    
#------------------------- Crearemos una funcion para asignar al boton registro --------------------------------
def registro():
    global usuario
    global contra
    global usuario_entrada
    global contra_entrada
    global pantalla1
    pantalla1 = Toplevel(pantalla)
    pantalla1.configure(bg="#cbcbcb")
    pantalla1.title("Registro")
    pantalla1.geometry("350x420")
    Label(pantalla1,text="REGISTRARSE", bg="#5e5e5e", fg="white", width="350", height="3", font=("Arial", 15)).pack()  
    
    # Empezaremos a crear las entradas
    usuario = StringVar()
    contra = StringVar()
    
    Label(pantalla1, text = "", bg="#cbcbcb").pack()
    Label(pantalla1, text = "Registro facial: debe de asignar un usuario y escanear rostro", bg="#cbcbcb").pack()
    Label(pantalla1, text = "Registro tradicional: debe asignar usuario y contraseña", bg="#cbcbcb").pack()
    Label(pantalla1, text = "", bg="#cbcbcb").pack()
    Label(pantalla1, text = "* Usuario:", bg="#cbcbcb").pack()
    usuario_entrada = Entry(pantalla1, textvariable = usuario)
    usuario_entrada.pack()
    Label(pantalla1, text = "* Contraseña:", bg="#cbcbcb").pack()
    contra_entrada = Entry(pantalla1, show="*",textvariable = contra)
    contra_entrada.pack()
    Label(pantalla1, text = "", bg="#cbcbcb").pack()
    Button(pantalla1, text = "Registro Tradicional", width = 25, height = 2, bg = "#007acc", fg = "white", command = registrar_usuario).pack()

    # Vamos a crear el boton para hacer el registro facial
    Label(pantalla1, text = "", bg="#cbcbcb").pack()
    Button(pantalla1, text = "Registro Facial", width = 25, height = 2, bg = "#007acc", fg = "white", command = registro_facial).pack()

#--------------------- Funcion para verificar los datos ingresados al login ------------------------------------
def verificacion_login():
    log_usuario = verificacion_usuario.get()
    log_contra = verificacion_contra.get()

    usuario_entrada2.delete(0, END)
    contra_entrada2.delete(0, END)

    lista_archivos = os.listdir()   #Vamos a importar la lista de archivos con la libreria os
    if log_usuario in lista_archivos:   #Comparamos los archivos con el que nos interesa
        archivo2 = open(log_usuario, "r")  #Abrimos el archivo en modo lectura
        verificacion = archivo2.read().splitlines()  #leera las lineas dentro del archivo ignorando el resto
        if log_contra in verificacion:
            print("Inicio de sesion exitoso")
            messagebox.showinfo("Información", "Inicio de sesión exitoso")
        else:
            print("Contraseña incorrecta, ingrese de nuevo")
            messagebox.showinfo("Información", "Contraseña incorrecta")
    else:
        print("Usuario no encontrado")
        messagebox.showinfo("Información", "Usuario no encontrado")
    
#--------------------------------- Funcion para el Login Facial ------------------------------------------------
def login_facial():
    
    # Contador de parpadeos
    blink_counter = 0
    blink_total = 0
    
    # Iniciar la captura del rostro
    cap = cv2.VideoCapture(0)
    
    while(True):
        ret,frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray)
        
        # Mostrar el número de rostros detectados en el frame
        num_faces = len(faces)
        cv2.putText(frame, f"Rostros detectados: {num_faces}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Reiniciar el contador de parpadeos si hay más de un rostro
        if num_faces > 1:
            blink_counter = 0
            blink_total = 0
            cv2.putText(frame, "Demasiados rostros en pantalla", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        elif num_faces < 1:
            blink_counter = 0
            blink_total = 0
            cv2.putText(frame, "No hay rostros por examinar", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)    
        elif num_faces == 1:
            capture_frame = frame.copy()
            # Obtener los puntos de referencia faciales (landmarks)
            for face in faces:
                shape = predictor(gray, face)
                shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]
            
            # Extraer las coordenadas de los ojos
            left_eye = shape[36:42]
            right_eye = shape[42:48]

            # Calcular la relación de aspecto del ojo para cada ojo
            leftEAR = eye_aspect_ratio(left_eye)
            rightEAR = eye_aspect_ratio(right_eye)
            ear = (leftEAR + rightEAR) / 2.0

            # Verificar si la relación de aspecto indica un parpadeo
            if ear < EYE_AR_THRESH:
                blink_counter += 1
            else:
                if blink_counter >= EYE_AR_CONSEC_FRAMES:
                    blink_total += 1
                blink_counter = 0

            # Dibujar los ojos y la detección de parpadeos en el frame
            for (x, y) in left_eye + right_eye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                
                if blink_total >= 1:
                    cv2.putText(frame, f"Parpadeos: {blink_total}, Pulsa q para tomar captura", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                elif blink_total == 0:
                    cv2.putText(frame, f"Parpadeos: {blink_total}, Posible fotografia", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        #Muestra ventana
        cv2.imshow('Login Facial',frame)
        
        #Romper el video
        if cv2.waitKey(1) & 0xFF == ord("q") and blink_total>=1:
            break
        
    usuario_login = verificacion_usuario.get()
    cv2.imwrite(usuario_login+"LOG.jpg",capture_frame)
    cap.release()
    cv2.destroyAllWindows()

    usuario_entrada2.delete(0, END)
    contra_entrada2.delete(0, END)

    # Funcion para guardar el rostro
    def log_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1,y1,ancho, alto = lista_resultados[i]['box']
            x2,y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i+1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg,(150,200), interpolation = cv2.INTER_CUBIC) #Guardamos la imagen 150x200
            cv2.imwrite(usuario_login+"LOG.jpg",cara_reg)
            return pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    # Detectamos el rostro
    img = usuario_login+"LOG.jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    log_rostro(img, caras)

    # Funcion para comparar los rostros
    def orb_sim(img1,img2):
        orb = cv2.ORB_create()  #Creamos el objeto de comparacion
 
        kpa, descr_a = orb.detectAndCompute(img1, None)  #Creamos descriptor 1 y extraemos puntos claves
        kpb, descr_b = orb.detectAndCompute(img2, None)  #Creamos descriptor 2 y extraemos puntos claves

        comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True) #Creamos comparador de fuerza

        matches = comp.match(descr_a, descr_b)  #Aplicamos el comparador a los descriptores

        regiones_similares = [i for i in matches if i.distance < 70] #Extraemos las regiones similares en base a los puntos claves
        if len(matches) == 0:
            return 0
        return len(regiones_similares)/len(matches)  #Exportamos el porcentaje de similitud
        
    # Importamos las imagenes y llamamos la funcion de comparacion
    im_archivos = os.listdir()   #Vamos a importar la lista de archivos con la libreria os
    if usuario_login+".jpg" in im_archivos:   #Comparamos los archivos con el que nos interesa
        rostro_reg = cv2.imread(usuario_login+".jpg",0)     #Importamos el rostro del registro
        rostro_log = cv2.imread(usuario_login+"LOG.jpg",0)  #Importamos el rostro del inicio de sesion
        similitud = orb_sim(rostro_reg, rostro_log)
        if similitud >= 0.90:
            print("Bienvenido al sistema usuario: ",usuario_login)
            print("Compatibilidad con la foto del registro: ",similitud*100,"%")
            messagebox.showinfo("Información", "Inicio de sesión exitoso")
            pantalla2.destroy()
        else:
            print("Rostro incorrecto, Verifique su usuario")
            print("Compatibilidad con la foto del registro: ",similitud*100,"%")
            messagebox.showinfo("Información", "Incompatibilidad de rostros")
    else:
        print("Usuario no encontrado")
        messagebox.showinfo("Información", "Usuario no encontrado")

#------------------------Funcion que asignaremos al boton login -------------------------------------------------
def login():
    global pantalla2
    global verificacion_usuario
    global verificacion_contra
    global usuario_entrada2
    global contra_entrada2
    
    pantalla2 = Toplevel(pantalla)
    pantalla2.title("Inicio de sesión")
    pantalla2.configure(bg="#cbcbcb")
    pantalla2.geometry("400x400")
    Label(pantalla2,text="INICIAR SESIÓN", bg="#5e5e5e", fg="white", width="350", height="3", font=("Arial", 15)).pack()  
    Label(pantalla2, text = "", bg="#cbcbcb").pack()
    Label(pantalla2, text = "Inicio de sesión facial: debe de ingresar un usuario y escanear rostro", bg="#cbcbcb").pack()
    Label(pantalla2, text = "Inicio de sesión tradicional: debe asignar usuario y contraseña", bg="#cbcbcb").pack()
    Label(pantalla2, text = "", bg="#cbcbcb").pack() 
    
    verificacion_usuario = StringVar()
    verificacion_contra = StringVar()
    
    # Ingresamos los datos
    Label(pantalla2, text = "* Usuario:", bg="#cbcbcb").pack()
    usuario_entrada2 = Entry(pantalla2, textvariable = verificacion_usuario)
    usuario_entrada2.pack()
    Label(pantalla2, text="* Contraseña:", bg="#cbcbcb").pack()
    contra_entrada2 = Entry(pantalla2, show="*", textvariable = verificacion_contra)
    contra_entrada2.pack()
    Label(pantalla2, text = "", bg="#cbcbcb").pack()
    Button(pantalla2, text = "Inicio de Sesion tradicional", width = 25, height = 2, bg = "#007acc", fg = "white", command = verificacion_login).pack()

    # Vamos a crear el boton para hacer el login facial
    Label(pantalla2, text = "", bg="#cbcbcb").pack()
    Button(pantalla2, text = "Inicio de Sesion facial", width = 25, height = 2, bg = "#007acc", fg = "white", command = login_facial).pack()
        
#------------------------- Funcion de nuestra pantalla principal ------------------------------------------------
def pantalla_principal():
    global pantalla          
    pantalla = Tk()
    pantalla.geometry("400x300")  
    pantalla.title("Sistema de reconocimiento facial")   
    pantalla.configure(bg="#cbcbcb")
    pantalla.update_idletasks()  
    pantalla.eval('tk::PlaceWindow . center')  
    Label(text="MENÚ PRINCIPAL", bg="#5e5e5e", fg="white", width="350", height="3", font=("Arial", 15)).pack()
    
    # Vamos a Crear los Botones
    Label(text = "", bg="#cbcbcb").pack()  
    Button(text = "Iniciar Sesion", height = "2", width = "25", command = login, bg = "#007acc", fg = "white").pack()
    Label(text = "", bg="#cbcbcb").pack() 
    Label(text = "No tienes una cuenta? Registrate aquí", bg = "#cbcbcb", fg= "black",).pack()
    Label(text = "", bg="#cbcbcb").pack()
    Button(text = "Registrarse", height = "1", width = "15", command = registro, bg = "#007acc", fg = "white").pack()

    pantalla.mainloop()

pantalla_principal()