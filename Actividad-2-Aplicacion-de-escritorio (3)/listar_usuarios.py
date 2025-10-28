# listar_usuarios.py
import sqlite3
# import os # Ya no es necesario
import db_manager # <--- AÑADIDO: Importamos nuestro módulo corregido

# DB = "calificaciones.db" # <--- ELIMINADO
# if not os.path.exists(DB): # <--- ELIMINADO
#     print("No se encontró", DB); raise SystemExit

print(f"Buscando base de datos en: {db_manager.DB_FILE}")

try:
    # --- CORREGIDO: Usamos la función de db_manager ---
    conn = db_manager.get_db_connection()
except sqlite3.OperationalError as e:
    print(f"Error al conectar a la base de datos (asegúrate que exista): {e}")
    raise SystemExit

conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, username, role, nombre_completo FROM Usuarios ORDER BY username")
rows = cur.fetchall()
print("Usuarios encontrados:", len(rows))
for r in rows:
    print(f"{r['id']:3}  {r['username']:15}  {r['role']:9}  {r['nombre_completo'] or ''}")
conn.close()