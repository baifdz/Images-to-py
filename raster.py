import cv2
import numpy as np
import os

def generate_turtle_drawing_code_from_image(image_path, output_filename="draw.py"):
    try:
        # 1. Cargar la imagen
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen: {image_path}")

        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Aplicar desenfoque Gaussiano para reducir el ruido y ayudar a la detección de bordes
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 2. Detección de bordes (Canny)
        # Los umbrales (50, 150) pueden necesitar ajustarse para diferentes imágenes
        edges = cv2.Canny(blurred, 50, 150)

        # 3. Encontrar contornos
        # cv2.RETR_LIST recupera todos los contornos sin establecer ninguna relación jerárquica
        # cv2.CHAIN_APPROX_SIMPLE comprime los segmentos horizontales, verticales y diagonales
        # y deja solo sus puntos finales.
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Abrir el archivo de salida para escribir el código Python
        with open(output_filename, "w") as f_out:
            f_out.write("import turtle\n")
            f_out.write("\n")
            f_out.write("def draw_image_from_contours():\n")
            f_out.write("    screen = turtle.Screen()\n")
            f_out.write("    screen.title('Imagen Vectorizada con Turtle')\n")
            f_out.write("    turtle.speed(0) # La velocidad mas rapida\n")
            f_out.write("    turtle.penup()\n")
            f_out.write("    turtle.hideturtle()\n")
            f_out.write("    turtle.pencolor('black')\n")
            f_out.write("\n")
            
            # Escala y desplazamiento para centrar y ajustar el tamaño
            # Los contornos se obtienen en coordenadas de píxeles, necesitamos escalarlos
            # para que se ajusten a la ventana de turtle (que suele ser -300 a 300)
            
            # Calcular el centroide de todos los contornos para centrar
            all_points = np.concatenate(contours) if contours else np.array([])
            if all_points.size == 0:
                print("No se encontraron contornos para dibujar.")
                return

            min_x = all_points[:, 0, 0].min()
            max_x = all_points[:, 0, 0].max()
            min_y = all_points[:, 0, 1].min()
            max_y = all_points[:, 0, 1].max()
            
            img_width = max_x - min_x
            img_height = max_y - min_y

            # Ajustar el factor de escala para que la imagen quepa en la ventana de turtle
            # Asumimos una ventana de turtle de ~600x600 unidades.
            # Puedes ajustar 500 para hacerlo más grande o pequeño en la ventana de turtle
            scale_factor = 500 / max(img_width, img_height, 1) 
            
            # Calcular el desplazamiento para centrar la imagen
            offset_x = - (min_x + max_x) / 2 * scale_factor
            offset_y = - (min_y + max_y) / 2 * scale_factor

            for i, contour in enumerate(contours):
                if len(contour) < 2: # Necesitamos al menos dos puntos para una línea
                    continue
                
                # Mover al primer punto del contorno
                x, y = contour[0][0]
                f_out.write(f"    turtle.penup()\n")
                f_out.write(f"    turtle.goto({x * scale_factor + offset_x}, {-(y * scale_factor + offset_y)})\n") # Y se invierte en turtle
                f_out.write(f"    turtle.pendown()\n")

                # Dibujar el resto del contorno
                for point in contour:
                    x, y = point[0]
                    f_out.write(f"    turtle.goto({x * scale_factor + offset_x}, {-(y * scale_factor + offset_y)})\n")
                
                # Opcional: Cerrar el contorno si es una forma cerrada
                # f_out.write(f"    turtle.goto({contour[0][0][0] * scale_factor + offset_x}, {-(contour[0][0][1] * scale_factor + offset_y)})\n")

            f_out.write("\n")
            f_out.write("    turtle.done()\n")
            f_out.write("\n")
            f_out.write("if __name__ == '__main__':\n")
            f_out.write("    draw_image_from_contours()\n")

        print(f"Archivo '{output_filename}' generado exitosamente. Ejecútalo para ver el dibujo.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

# --- Asegurarse de tener la imagen (como en ejemplos anteriores) ---
image_filename_for_vectorization = "rosaf.png"

if not os.path.exists(image_filename_for_vectorization):
    print(f"Creando una imagen de rosa simple para el ejemplo, ya que '{image_filename_for_vectorization}' no existe.")
    from PIL import Image, ImageDraw
    img_placeholder = Image.new('RGB', (300, 300), color = 'white')
    d = ImageDraw.Draw(img_placeholder)
    # Dibujo simplificado para que los contornos sean más claros
    d.ellipse((50, 50, 250, 250), fill=(255, 0, 0), outline=(0, 0, 0), width=5)
    d.polygon([(150, 250), (140, 300), (160, 300)], fill=(0, 128, 0))
    d.line([(150, 200), (100, 150)], fill=(0,0,0), width=3) # Un detalle más para contorno
    d.line([(150, 200), (200, 150)], fill=(0,0,0), width=3) # Un detalle más para contorno
    img_placeholder.save(image_filename_for_vectorization)
    print(f"Se ha guardado '{image_filename_for_vectorization}' (placeholder).")

# Generar el archivo Python para dibujar la imagen
generate_turtle_drawing_code_from_image(image_filename_for_vectorization)
