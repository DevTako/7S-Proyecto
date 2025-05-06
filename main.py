import flet as ft
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from PIL import Image
import io
import asyncio
import base64  # Importación añadida para la codificación base64

async def main(page: ft.Page):
    page.window_width = 800
    page.window_height = 520
    page.padding = 0
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    
    # Controles de UI
    username_field = ft.TextField(
        width=280,
        height=40,
        hint_text='Usuario',
        border='underline',
        color='black',
        prefix_icon=ft.icons.PERSON,
    )
    
    password_field = ft.TextField(
        width=280,
        height=40,
        hint_text='Contraseña',
        border='underline',
        color='black',
        prefix_icon=ft.icons.LOCK,
        password=True,
    )
    
    # Vista previa de la cámara
    camera_view = ft.Image(
        src="",
        width=300,
        height=300,
        visible=False,
        fit=ft.ImageFit.CONTAIN
    )
    
    qr_result = ft.Text(
        "",
        size=16,
        weight="bold",
        visible=False
    )
    
    # Diálogo del escáner QR
    qr_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Escanear código QR"),
        content=ft.Column([
            camera_view,
            qr_result,
            ft.ElevatedButton(
                "Cancelar",
                on_click=lambda e: close_qr_scanner(e)
            )
        ], tight=True),
        on_dismiss=lambda e: print("Escaneo cancelado"),
    )
    
    # Variable para controlar el escaneo
    scanning = False
    
    async def close_qr_scanner(e):
        nonlocal scanning
        scanning = False
        qr_dialog.open = False
        page.update()
    
    async def open_qr_scanner(e):
        nonlocal scanning
        
        # Verificar disponibilidad de cámara
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise Exception("No se pudo acceder a la cámara")
            cap.release()
        except Exception as e:
            page.snackbar = ft.SnackBar(ft.Text(f"Error de cámara: {str(e)}"))
            page.snackbar.open = True
            page.update()
            return

        scanning = True
        page.dialog = qr_dialog
        qr_dialog.open = True
        camera_view.visible = True
        qr_result.value = "Apunte el código QR a la cámara"
        qr_result.visible = True
        page.update()
        
        # Iniciar captura de cámara
        cap = cv2.VideoCapture(0)
        
        while scanning and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convertir frame para mostrar en Flet
            _, buffer = cv2.imencode('.jpg', frame)
            img_bytes = io.BytesIO(buffer)
            camera_view.src_base64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
            
            # Intentar decodificar QR
            decoded_objects = pyzbar.decode(frame)
            if decoded_objects:
                for obj in decoded_objects:
                    qr_data = obj.data.decode("utf-8")
                    qr_result.value = f"Código detectado: {qr_data}"
                    qr_result.visible = True
                    
                    # Validar el código QR (aquí deberías implementar tu lógica)
                    if qr_data == "CODIGO_VALIDO":  # Reemplaza con tu validación
                        await asyncio.sleep(1)  # Mostrar feedback
                        scanning = False
                        qr_dialog.open = False
                        page.snackbar = ft.SnackBar(ft.Text("Autenticación por QR exitosa!"))
                        page.snackbar.open = True
                        # Aquí iría la navegación a la pantalla principal
                        # page.go("/home")
                    break
                    
            page.update()
            await asyncio.sleep(0.1)  # Controlar la tasa de refresco
            
        cap.release()
        camera_view.visible = False
        qr_result.visible = False
        page.update()
    
    async def login_with_credentials(e):
        if username_field.value and password_field.value:
            page.snackbar = ft.SnackBar(ft.Text("Inicio de sesión exitoso!"))
            page.snackbar.open = True
            # Aquí iría la navegación a la pantalla principal
            # page.go("/home")
        else:
            page.snackbar = ft.SnackBar(ft.Text("Usuario y contraseña requeridos"))
            page.snackbar.open = True
        page.update()
    
    # Construcción de la interfaz
    login_column = ft.Column(
        controls=[
            ft.Container(
                ft.Image(src='logo.png', width=70),
                padding=ft.padding.only(150, 20)
            ),
            ft.Text(
                'Iniciar Sesión',
                width=360,
                size=30,
                weight='w900',
                text_align='center'
            ),
            ft.Container(username_field, padding=ft.padding.only(20, 10)),
            ft.Container(password_field, padding=ft.padding.only(20, 10)),
            ft.Container(
                ft.Checkbox(label='Recordar contraseña', check_color='black'),
                padding=ft.padding.only(40),
            ),
            ft.Container(
                ft.ElevatedButton(
                    content=ft.Text('INICIAR', color='white', weight='w500'),
                    width=280,
                    bgcolor='black',
                    on_click=login_with_credentials
                ),
                padding=ft.padding.only(25, 10)
            ),
            ft.Container(
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.icons.QR_CODE_SCANNER),  # Icono corregido
                        ft.Text("Escanear código QR", weight='w500')
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    width=280,
                    bgcolor='black',
                    on_click=open_qr_scanner
                ),
                padding=ft.padding.only(25, 10)
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    )
    
    body = ft.Container(
        ft.Row([
            ft.Container(
                login_column,
                gradient=ft.LinearGradient(['red', 'orange']),
                width=380,
                height=460,
                border_radius=20
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        ),
        padding=10,
    )
    
    page.add(body)

# Ejecutar la app
ft.app(target=main)