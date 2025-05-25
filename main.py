import flet as ft
import cv2
import asyncio
import base64
import io
import numpy as np
import mysql.connector
import pyzbar.pyzbar as pyzbar
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'port': 3306,
    'database': 'qr_auth_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def validate_qr_token(qr_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username FROM users WHERE qr_token = %s", (qr_data,))
        result = cursor.fetchone()
        return bool(result), result['username'] if result else None
    except Exception as e:
        print(f"Error validando token QR: {e}")
        return False, None
    finally:
        cursor.close()
        conn.close()

def validate_credentials(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username FROM users WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        return bool(result), result['username'] if result else None
    except Exception as e:
        print(f"Error validando credenciales: {e}")
        return False, None
    finally:
        cursor.close()
        conn.close()

async def main(page: ft.Page):
    page.title = "Sistema de Acceso"
    page.bgcolor = ft.colors.BLACK
    page.window_width = 800
    page.window_height = 600
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    scanning = False

    status_text = ft.Text(
        "Seleccione método de autenticación",
        size=20,
        weight="bold",
        color=ft.colors.WHITE,
        text_align="center"
    )

    access_indicator = ft.Container(
        width=50,
        height=50,
        border_radius=25,
        bgcolor=ft.colors.GREY_300,
        visible=False
    )

    user_display = ft.Text(
        "",
        size=18,
        weight="bold",
        color=ft.colors.LIME_300,
        visible=False
    )

    username_field = ft.TextField(
        label="Usuario",
        width=300,
        bgcolor=ft.colors.BLACK,
        border_color=ft.colors.PURPLE,
        color=ft.colors.WHITE,
        prefix_icon=ft.icons.PERSON
    )

    password_field = ft.TextField(
        label="Contraseña",
        width=300,
        password=True,
        can_reveal_password=True,
        bgcolor=ft.colors.BLACK,
        border_color=ft.colors.PURPLE,
        color=ft.colors.WHITE,
        prefix_icon=ft.icons.LOCK
    )

    blank_image = base64.b64encode(io.BytesIO(cv2.imencode('.jpg', 255 * np.ones((400, 400, 3), dtype=np.uint8))[1]).getvalue()).decode("utf-8")
    camera_view = ft.Image(
        src_base64=blank_image,
        width=400,
        height=400,
        fit=ft.ImageFit.CONTAIN,
        border_radius=10
    )

    async def start_scanning(e):
        nonlocal scanning
        scanning = True
        cap = cv2.VideoCapture(0)

        while scanning and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            img_bytes = io.BytesIO(buffer)
            camera_view.src_base64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")

            decoded_objects = pyzbar.decode(frame)
            for obj in decoded_objects:
                qr_data = obj.data.decode("utf-8")
                is_valid, username = validate_qr_token(qr_data)

                if is_valid:
                    scanning = False
                    await grant_access(username)
                    break

            page.update()
            await asyncio.sleep(0.1)

        cap.release()

    async def stop_scanning(e):
        nonlocal scanning
        scanning = False

    async def login_with_credentials(e):
        if not username_field.value or not password_field.value:
            await show_message("Usuario y contraseña requeridos", ft.colors.RED_400)
            return

        is_valid, username = validate_credentials(username_field.value, password_field.value)

        if is_valid:
            await grant_access(username)
        else:
            await show_message("Credenciales incorrectas", ft.colors.RED_400)

    async def grant_access(username):
        await show_message(f"Bienvenido, {username}!", ft.colors.GREEN_400)
        from dashboard import show_dashboard
        await show_dashboard(page, username)

    async def show_message(message, color):
        page.snackbar = ft.SnackBar(ft.Text(message, color=color))
        page.snackbar.open = True
        page.update()
        await asyncio.sleep(2)
        page.snackbar.open = False
        page.update()

    page.add(
        ft.Column([
            ft.Text("Sistema de Acceso", size=24, weight="bold", color=ft.colors.LIME_300),
            ft.Divider(color=ft.colors.GREY_600),
            ft.Container(content=status_text, border=ft.border.all(1, ft.colors.PURPLE_400), padding=10),
            ft.Row([access_indicator, user_display], alignment="center", spacing=10),
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Código QR",
                        icon=ft.icons.QR_CODE,
                        content=ft.Column([
                            ft.ElevatedButton("Iniciar escaneo de QR", icon=ft.icons.CAMERA_ALT, on_click=start_scanning, width=300, bgcolor=ft.colors.BLUE_400),
                            ft.Container(content=camera_view, border=ft.border.all(1, ft.colors.PURPLE_400), padding=10, border_radius=10),
                            ft.ElevatedButton("Detener escaneo", icon=ft.icons.STOP, on_click=stop_scanning, width=300, bgcolor=ft.colors.RED_400),
                        ], spacing=20, horizontal_alignment="center")
                    ),
                    ft.Tab(
                        text="Usuario/Contraseña",
                        icon=ft.icons.PERSON,
                        content=ft.Column([
                            username_field,
                            password_field,
                            ft.ElevatedButton("Iniciar sesión", icon=ft.icons.LOGIN, on_click=login_with_credentials, width=300, bgcolor=ft.colors.GREEN_400),
                        ], spacing=20, horizontal_alignment="center")
                    )
                ]
            )
        ], spacing=30, horizontal_alignment="center")
    )

    page.update()

if __name__ == "__main__":
    ft.app(target=main)