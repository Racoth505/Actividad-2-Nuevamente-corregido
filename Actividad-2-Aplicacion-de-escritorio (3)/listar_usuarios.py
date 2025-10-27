# listar_usuarios.py
import sqlite3, os
DB = "calificaciones.db"
if not os.path.exists(DB):
    print("No se encontró", DB); raise SystemExit

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, username, role, nombre_completo FROM Usuarios ORDER BY username")
rows = cur.fetchall()
print("Usuarios encontrados:", len(rows))
for r in rows:
    print(f"{r['id']:3}  {r['username']:15}  {r['role']:9}  {r['nombre_completo'] or ''}")
conn.close()