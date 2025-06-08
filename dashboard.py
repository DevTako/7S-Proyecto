import flet as ft
import asyncio
import mysql.connector
import threading
from datetime import datetime, date 

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'port': 3306,
    'database': 'qr_auth_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def record_logout(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%H:%M:%S")
        
        # CORRECTO: Usar 'usuario' para la tabla 'registros_acceso'
        cursor.execute("""
            UPDATE registros_acceso
            SET hora_salida = %s
            WHERE usuario = %s AND fecha = %s AND hora_salida IS NULL
            ORDER BY hora_entrada DESC
            LIMIT 1
        """, (hora_actual, username, fecha_actual))
        conn.commit()
        print(f"Hora de salida registrada para {username}.")
    except Exception as e:
        print(f"Error al registrar hora de salida: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def safe_async(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=lambda: asyncio.run(func(*args, **kwargs))).start()
    return wrapper

async def show_dashboard(page: ft.Page, username: str, record_logout_func):
    page.controls.clear()
    page.title = f"Dashboard - {username}"
    page.bgcolor = "#1e1e2f"
    page.window_width = 900
    page.window_height = 600
    page.window_resizable = True

    selected_option = "lista_ingresos"
    content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    async def update_content():
        content.controls.clear()
        option = selected_option
        
        page.update() 

        if option == "lista_ingresos":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                # CORRECTO: Usar 'usuario' para la tabla 'registros_acceso'
                cursor.execute("""
                    SELECT usuario, fecha, hora_entrada, hora_salida
                    FROM registros_acceso
                    ORDER BY fecha DESC, hora_entrada DESC
                """)
                rows = cursor.fetchall()

                if rows:
                    data_table = ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Usuario", color="white", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Fecha", color="white", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Hora de Entrada", color="white", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Hora de Salida", color="white", weight=ft.FontWeight.BOLD)),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(row[0], color="white")),
                                    # CORREGIDO para isinstance() error
                                    ft.DataCell(ft.Text(row[1].strftime("%d/%m/%Y") if isinstance(row[1], date) else (str(row[1]) if row[1] is not None else "-"), color="white")),
                                    ft.DataCell(ft.Text(row[2], color="white")),
                                    ft.DataCell(ft.Text(row[3] if row[3] else "-", color="white")),
                                ]
                            ) for row in rows
                        ],
                        heading_row_color={"even": "#2d2d45", "odd": "#2d2d45"},
                        data_row_color={"even": "#2b2b3c", "odd": "#1e1e2f"},
                        border=ft.border.all(1, "grey"),
                        column_spacing=20,
                        show_checkbox_column=False,
                        width=700,
                        vertical_lines=ft.BorderSide(0.5, "grey"),
                        horizontal_lines=ft.BorderSide(0.5, "grey"),
                        # ELIMINADO: min_row_height
                    )
                    content.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text("📋 Lista de Ingresos", size=24, color="#9fffb3", weight=ft.FontWeight.BOLD),
                                ft.Divider(color="grey", thickness=2),
                                ft.Container(height=10),
                                data_table
                            ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            alignment=ft.alignment.center,
                            expand=True
                        )
                    )
                else:
                    content.controls.append(
                        ft.Column([
                            ft.Text("📋 Lista de Ingresos", size=24, color="#9fffb3", weight=ft.FontWeight.BOLD),
                            ft.Divider(color="grey", thickness=2),
                            ft.Container(height=10),
                            ft.Text("No hay registros de acceso disponibles.", color="white", size=16, text_align=ft.TextAlign.CENTER)
                        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
                    )

            except Exception as e:
                content.controls.append(
                    ft.Text(f"Error al cargar registros: {e}", color=ft.Colors.RED, size=16, text_align=ft.TextAlign.CENTER)
                )
                print(f"DEBUG: Error cargando registros: {e}")
            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if 'conn' in locals() and conn:
                    conn.close()

        elif option == "ajustes_usuario":
            new_password = ft.TextField(
                password=True,
                can_reveal_password=True,
                width=300,
                label="Nueva Contraseña",
                label_style=ft.TextStyle(color="white"),
                text_style=ft.TextStyle(color="white"),
                border_color="#4CAF50"
            )
            confirm_user = ft.TextField(
                width=300,
                label="Confirma tu Usuario",
                label_style=ft.TextStyle(color="white"),
                text_style=ft.TextStyle(color="white"),
                border_color="#4CAF50"
            )
            message = ft.Text("", color=ft.Colors.RED)

            async def guardar_cambios(e):
                message.value = ""
                page.update()

                if confirm_user.value.strip() != username:
                    message.value = "Usuario incorrecto. Por favor, confirma tu propio usuario."
                    message.color = ft.Colors.RED
                elif not new_password.value:
                    message.value = "Por favor, ingresa la nueva contraseña."
                    message.color = ft.Colors.RED
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        # CORRECTO: Usar 'username' para la tabla 'users'
                        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password.value, username))
                        conn.commit()
                        message.value = "Contraseña actualizada correctamente. Cerrando sesión..."
                        message.color = ft.Colors.GREEN_400
                        page.update()
                        await asyncio.sleep(2)
                        
                        record_logout_func(username) 
                        
                        from main import main
                        page.controls.clear()
                        await main(page)
                        return
                    except Exception as ex:
                        message.value = f"Error al actualizar la contraseña: {ex}"
                        message.color = ft.Colors.RED
                    finally:
                        if 'cursor' in locals() and cursor:
                            cursor.close()
                        if 'conn' in locals() and conn:
                            conn.close()
                page.update()

            content.controls.append(
                ft.Column([
                    ft.Text("🔒 Cambiar Contraseña", size=24, color="#9fffb3", weight=ft.FontWeight.BOLD),
                    ft.Divider(color="grey", thickness=2),
                    ft.Container(height=20),
                    new_password,
                    confirm_user,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Guardar cambios",
                        on_click=guardar_cambios,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                            padding=ft.padding.all(15),
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    message
                ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
            )

        elif option == "soporte":
            content.controls.append(
                ft.Column([
                    ft.Text("🛠 Soporte Técnico", size=24, color="#9fffb3", weight=ft.FontWeight.BOLD),
                    ft.Divider(color="grey", thickness=2),
                    ft.Container(height=20),
                    ft.Text("Si necesitas ayuda o tienes alguna pregunta, no dudes en contactarnos:",
                            color="white", size=16, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    ft.Text("📧 Correo Electrónico: soporte@seguridad.com", color="#8ab4f8", size=16, selectable=True),
                    ft.Text("📞 Teléfono: +58 412-1234567", color="#8ab4f8", size=16, selectable=True),
                    ft.Container(height=10),
                    ft.Text("Horario de Atención: Lunes a Viernes, 9:00 AM - 5:00 PM (Hora de Venezuela)",
                            color="white", size=14, text_align=ft.TextAlign.CENTER),
                ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
            )

        page.update()

    def on_nav_change(e):
        nonlocal selected_option
        selected_option = e.control.data
        for tile in nav_column_content.controls[1:]:
            tile.selected = (tile.data == selected_option)
            tile.selected_tile_color = "#3a3a50" if tile.selected else None
            tile.bgcolor = "#3a3a50" if tile.selected else None
        
        asyncio.run(update_content())

    async def logout(e):
        print(f"Usuario {username} cerrando sesión.")
        record_logout_func(username)
        
        from main import main
        page.controls.clear()
        await main(page)

    app_bar = ft.AppBar(
        title=ft.Text(f"Bienvenido, {username}", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor="#111122",
        actions=[
            ft.IconButton(
                ft.Icons.LOGOUT,
                on_click=logout,
                tooltip="Cerrar sesión",
                icon_color=ft.Colors.WHITE,
                selected_icon=ft.Icons.LOGOUT_ROUNDED
            )
        ]
    )

    nav_column_content = ft.Column([
        ft.Container(
            content=ft.Text("Menú Principal", size=20, weight=ft.FontWeight.BOLD, color="#9fffb3"),
            padding=ft.padding.only(bottom=10, top=10, left=10)
        ),
        ft.ListTile(
            title=ft.Text("Lista de Ingresos", color=ft.Colors.WHITE),
            leading=ft.Icon(ft.Icons.LIST_ALT, color=ft.Colors.WHITE),
            data="lista_ingresos",
            on_click=on_nav_change,
            selected=True,
            selected_tile_color="#3a3a50",
            bgcolor="#3a3a50"
        ),
        ft.ListTile(
            title=ft.Text("Ajustes de Usuario", color=ft.Colors.WHITE),
            leading=ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.WHITE),
            data="ajustes_usuario",
            on_click=on_nav_change
        ),
        ft.ListTile(
            title=ft.Text("Soporte", color=ft.Colors.WHITE),
            leading=ft.Icon(ft.Icons.LIVE_HELP, color=ft.Colors.WHITE),
            data="soporte",
            on_click=on_nav_change
        )
    ], spacing=5, expand=True)

    nav = ft.Container(
        content=nav_column_content,
        width=220,
        padding=0,
        bgcolor="#2c2c3c"
    )

    layout = ft.Row([
        nav,
        ft.VerticalDivider(width=1, color="grey"),
        ft.Container(content, expand=True, padding=20)
    ], expand=True)

    page.add(app_bar, layout)
    
    await update_content()
    page.update()