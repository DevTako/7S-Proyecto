import flet as ft
import asyncio
import mysql.connector
from datetime import datetime

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
        cursor.execute("""
            UPDATE registros_acceso
            SET hora_salida = %s
            WHERE usuario = %s AND hora_salida IS NULL
        """, (datetime.now().strftime("%H:%M:%S"), username))
        conn.commit()
    except Exception as e:
        print(f"Error al registrar hora de salida: {e}")
    finally:
        cursor.close()
        conn.close()

async def show_dashboard(page: ft.Page, username: str):
    page.controls.clear()
    page.title = f"Dashboard - {username}"
    page.bgcolor = ft.colors.BLACK
    page.window_width = 900
    page.window_height = 600

    selected_option = "lista_ingresos"
    content = ft.Column(expand=True)

    date_filter = ft.DatePicker(value=datetime.now().date())
    filter_btn = ft.ElevatedButton("Filtrar", width=120)
    filter_row = ft.Row([
        ft.Text("Filtrar por fecha:", color=ft.colors.WHITE),
        date_filter,
        filter_btn
    ], spacing=10)

    async def update_content():
        content.controls.clear()
        option = selected_option

        if option == "lista_ingresos":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                if date_filter.value:
                    selected_date = date_filter.value.strftime("%Y-%m-%d")
                    query = """
                        SELECT usuario, fecha, hora_entrada, hora_salida
                        FROM registros_acceso
                        WHERE fecha = %s
                        ORDER BY hora_entrada DESC
                    """
                    cursor.execute(query, (selected_date,))
                else:
                    cursor.execute("""
                        SELECT usuario, fecha, hora_entrada, hora_salida
                        FROM registros_acceso
                        ORDER BY fecha DESC, hora_entrada DESC
                    """)
                rows = cursor.fetchall()
                print(f"[DEBUG] Datos obtenidos ({len(rows)} filas):", rows)

                if rows:
                    data_table = ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Usuario")),
                            ft.DataColumn(ft.Text("Fecha")),
                            ft.DataColumn(ft.Text("Hora de Entrada")),
                            ft.DataColumn(ft.Text("Hora de Salida")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(row[0])),
                                    ft.DataCell(ft.Text(row[1].strftime("%d/%m/%Y") if isinstance(row[1], datetime) else str(row[1]))),
                                    ft.DataCell(ft.Text(row[2])),
                                    ft.DataCell(ft.Text(row[3] if row[3] else "-")),
                                ]
                            ) for row in rows
                        ],
                        heading_row_color=ft.colors.LIME_300,
                        data_row_color=ft.colors.WHITE24,
                        border=ft.border.Border(
                            left=ft.border.BorderSide(1, ft.colors.GREY_600),
                            top=ft.border.BorderSide(1, ft.colors.GREY_600),
                            right=ft.border.BorderSide(1, ft.colors.GREY_600),
                            bottom=ft.border.BorderSide(1, ft.colors.GREY_600),
                        ),
                        column_spacing=20,
                        show_checkbox_column=False,
                        width=700,
                        height=400,
                    )
                    content.controls.append(
                        ft.Column([
                            ft.Text("Lista de Ingresos", size=24, color=ft.colors.WHITE),
                            ft.Divider(color=ft.colors.GREY_600),
                            filter_row,
                            data_table
                        ], alignment="start")
                    )
                else:
                    content.controls.append(
                        ft.Column([
                            ft.Text("Lista de Ingresos", size=24, color=ft.colors.WHITE),
                            ft.Divider(color=ft.colors.GREY_600),
                            filter_row,
                            ft.Text("No hay registros para la fecha seleccionada.", color=ft.colors.WHITE70)
                        ], alignment="start")
                    )

            except Exception as e:
                print(f"[DEBUG] Error al cargar registros: {e}")
                content.controls.append(
                    ft.Text(f"Error al cargar registros: {e}", color=ft.colors.RED)
                )
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

        elif option == "ajustes_usuario":
            new_username = ft.TextField(width=300)
            new_password = ft.TextField(password=True, can_reveal_password=True, width=300)
            message = ft.Text("", color=ft.colors.RED)

            def guardar_cambios(e):
                if not new_username.value and not new_password.value:
                    message.value = "Ingresa nuevo usuario o contraseña"
                else:
                    message.value = "Cambios guardados (a implementar)"
                page.update()

            content.controls.append(
                ft.Column([
                    ft.Text("Ajuste de Usuario", size=24, color=ft.colors.WHITE),
                    ft.Divider(color=ft.colors.GREY_600),
                    ft.Text("Nuevo nombre de usuario:", color=ft.colors.WHITE),
                    new_username,
                    ft.Text("Nueva contraseña:", color=ft.colors.WHITE),
                    new_password,
                    ft.ElevatedButton("Guardar cambios", on_click=guardar_cambios),
                    message
                ], alignment="start")
            )
        elif option == "soporte":
            content.controls.append(
                ft.Column([
                    ft.Text("Soporte", size=24, color=ft.colors.WHITE),
                    ft.Divider(color=ft.colors.GREY_600),
                    ft.Text("Contacta a soporte@seguridad.com", color=ft.colors.WHITE70)
                ], alignment="start")
            )
        await page.update()

    def on_nav_change(e):
        nonlocal selected_option
        selected_option = e.control.data
        for tile in nav.controls:
            tile.selected = (tile.data == selected_option)
        asyncio.create_task(update_content())

    async def on_filter_click(e):
        await update_content()

    filter_btn.on_click = on_filter_click

    async def logout(e):
        record_logout(username)
        from main import main
        page.controls.clear()
        await main(page)

    app_bar = ft.AppBar(
        title=ft.Text(f"Bienvenido, {username}!", color=ft.colors.WHITE),
        bgcolor=ft.colors.BLACK,
        actions=[
            ft.IconButton(
                ft.icons.LOGOUT,
                on_click=logout,
                tooltip="Cerrar sesión"
            )
        ]
    )

    nav = ft.Column(
        [
            ft.Text("Menú", size=20, weight="bold", color=ft.colors.LIME_300),
            ft.ListTile(title=ft.Text("Lista de Ingresos", color=ft.colors.WHITE), data="lista_ingresos", on_click=on_nav_change, selected=True),
            ft.ListTile(title=ft.Text("Ajustes de Usuario", color=ft.colors.WHITE), data="ajustes_usuario", on_click=on_nav_change),
            ft.ListTile(title=ft.Text("Soporte", color=ft.colors.WHITE), data="soporte", on_click=on_nav_change)
        ],
        spacing=10
    )

    layout = ft.Row([
        ft.Container(nav, width=200, padding=10),
        ft.VerticalDivider(width=1, color=ft.colors.GREY_600),
        ft.Container(content, expand=True, padding=10)
    ])

    page.add(app_bar, layout)
    await update_content()
    await page.update()
