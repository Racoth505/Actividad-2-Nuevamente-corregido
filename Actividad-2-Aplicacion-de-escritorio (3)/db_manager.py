# db_manager.py
import sqlite3
import os
import hashlib

DB_FILE = "calificaciones.db"

# --- Database Connection and Password Hashing ---
def get_db_connection():
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Access results by column name
    conn.execute("PRAGMA foreign_keys = ON") # Enable foreign key constraints
    return conn

def hash_password(password):
    """Generates a secure SHA256 hash for the password."""
    return hashlib.sha256(password.encode()).hexdigest()

# --- Database Initialization ---
def initialize_database():
    """
    Creates all necessary tables if the database file doesn't exist.
    This function should be called once when the application starts.
    """
    if os.path.exists(DB_FILE):
        return # Database already exists

    print(f"Initializing new database: {DB_FILE}")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Usuarios Table (Admin, Professor, Student)
    cursor.execute("""
    CREATE TABLE Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'profesor', 'alumno')),
        nombre_completo TEXT,
        apellidos TEXT,
        telefono TEXT,
        direccion TEXT,
        ruta_foto TEXT DEFAULT 'assets/default_user.png'
    );
    """)

    # 2. Materias Table (Subjects/Courses - UPDATED)
    cursor.execute("""
    CREATE TABLE Materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        id_profesor_principal INTEGER, -- Optional main professor
        horas_semanales INTEGER,
        salon TEXT,
        fecha_inicio TEXT,           -- Format YYYY-MM-DD
        fecha_fin TEXT,              -- Format YYYY-MM-DD
        FOREIGN KEY (id_profesor_principal) REFERENCES Usuarios(id) ON DELETE SET NULL
    );
    """)

    # 3. Actividades Table (Assignments/Grades - UPDATED)
    cursor.execute("""
    CREATE TABLE Actividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_alumno INTEGER NOT NULL,
        id_materia INTEGER NOT NULL,
        tipo_actividad TEXT,         -- e.g., Tarea, Examen
        descripcion TEXT NOT NULL,   -- Description of the activity (e.g., "Tarea 1")
        calificacion REAL NOT NULL DEFAULT 0.0,
        peso REAL NOT NULL DEFAULT 1.0, -- Weight (percentage as decimal, e.g., 0.3 for 30%)
        fecha_inicio TEXT,           -- Format YYYY-MM-DD
        hora_inicio TEXT,            -- Format HH:MM
        fecha_fin TEXT,              -- Format YYYY-MM-DD
        hora_fin TEXT,               -- Format HH:MM
        FOREIGN KEY (id_alumno) REFERENCES Usuarios(id) ON DELETE CASCADE,
        FOREIGN KEY (id_materia) REFERENCES Materias(id) ON DELETE CASCADE
    );
    """)

    # 4. Asignaciones Table (Professor teaches Subject)
    cursor.execute("""
    CREATE TABLE Asignaciones (
        id_profesor INTEGER NOT NULL,
        id_materia INTEGER NOT NULL,
        FOREIGN KEY (id_profesor) REFERENCES Usuarios(id) ON DELETE CASCADE,
        FOREIGN KEY (id_materia) REFERENCES Materias(id) ON DELETE CASCADE,
        PRIMARY KEY (id_profesor, id_materia)
    );
    """)

    # 5. Inscripciones Table (Student enrolls in Subject)
    cursor.execute("""
    CREATE TABLE Inscripciones (
        id_alumno INTEGER NOT NULL,
        id_materia INTEGER NOT NULL,
        FOREIGN KEY (id_alumno) REFERENCES Usuarios(id) ON DELETE CASCADE,
        FOREIGN KEY (id_materia) REFERENCES Materias(id) ON DELETE CASCADE,
        PRIMARY KEY (id_alumno, id_materia)
    );
    """)

    # --- Default Admin User ---
    admin_pass_hash = hash_password("admin123")
    cursor.execute(
        "INSERT INTO Usuarios (username, password, role, nombre_completo) VALUES (?, ?, ?, ?)",
        ('admin', admin_pass_hash, 'admin', 'Administrador')
    )

    conn.commit()
    conn.close()
    print("Base de datos 'calificaciones.db' inicializada correctamente.")

# --- User Management Functions ---

def validate_login(username, password):
    """Validates user credentials against the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    pass_hash = hash_password(password)
    cursor.execute(
        "SELECT * FROM Usuarios WHERE username = ? AND password = ?",
        (username, pass_hash)
    )
    user = cursor.fetchone()
    conn.close()
    if user: return dict(user)
    return None

def create_user(username, password, role, nombre_completo, apellidos, telefono, direccion, ruta_foto=None):
    """Creates a new user (Professor or Student). Returns the new user's ID or None."""
    pass_hash = hash_password(password)
    if not ruta_foto:
        ruta_foto = "assets/default_prof.png" if role == "profesor" else "assets/default_student.png"

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO Usuarios (username, password, role, nombre_completo, apellidos, telefono, direccion, ruta_foto)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (username, pass_hash, role, nombre_completo, apellidos, telefono, direccion, ruta_foto)
        )
        conn.commit()
        new_user_id = cursor.lastrowid
        conn.close()
        return new_user_id
    except sqlite3.IntegrityError: # Username likely exists
        conn.close()
        return None
    except Exception as e:
        print(f"Error in create_user: {e}")
        conn.close()
        return None

def get_user_by_id(user_id):
    """Fetches user data by their primary ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user: return dict(user)
    return None

def get_users_by_role(role):
    """Gets all users belonging to a specific role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE role = ? ORDER BY nombre_completo", (role,))
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

def get_all_users_except_admin():
    """Gets all users except the 'admin' role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, nombre_completo FROM Usuarios WHERE role != 'admin' ORDER BY role, nombre_completo")
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

def delete_user(user_id):
    """Deletes a user by ID. Cascades deletes related records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Usuarios WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        conn.close()
        return False

def update_user_password(user_id, new_password):
    """Updates a user's password (typically by Admin)."""
    pass_hash = hash_password(new_password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Usuarios SET password = ? WHERE id = ?", (pass_hash, user_id))
    conn.commit()
    conn.close()

def update_user_password_by_id_and_old_pass(user_id, old_password, new_password):
    """Updates a user's password only if the old password matches."""
    conn = get_db_connection()
    cursor = conn.cursor()
    old_pass_hash = hash_password(old_password)
    cursor.execute("SELECT id FROM Usuarios WHERE id = ? AND password = ?", (user_id, old_pass_hash))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False # Old password incorrect
    new_pass_hash = hash_password(new_password)
    cursor.execute("UPDATE Usuarios SET password = ? WHERE id = ?", (new_pass_hash, user_id))
    conn.commit()
    conn.close()
    return True

def update_user_photo(user_id, new_photo_path):
    """Updates the user's profile photo path."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Usuarios SET ruta_foto = ? WHERE id = ?", (new_photo_path, user_id))
    conn.commit()
    conn.close()

def update_user_profile_details(user_id, nombre_completo, apellidos, telefono, direccion):
    """Actualiza los detalles editables del perfil de un usuario."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Usuarios
            SET nombre_completo = ?,
                apellidos = ?,
                telefono = ?,
                direccion = ?
            WHERE id = ?
        """, (nombre_completo, apellidos, telefono, direccion, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error en update_user_profile_details: {e}")
        conn.rollback()
        conn.close()
        return False

# --- Subject Management Functions ---

def add_subject_with_details(nombre, id_profesor, horas, salon, inicio, fin):
    """Añade una nueva materia con todos sus detalles."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Materias (nombre, id_profesor_principal, horas_semanales, salon, fecha_inicio, fecha_fin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, id_profesor, horas, salon, inicio, fin))
        conn.commit()
        new_subject_id = cursor.lastrowid # Get the ID of the newly inserted subject

        # Opcional: Asegurarse que el profesor principal también esté en Asignaciones
        if id_profesor:
             try:
                 cursor.execute("INSERT OR IGNORE INTO Asignaciones (id_profesor, id_materia) VALUES (?, ?)", (id_profesor, new_subject_id))
                 conn.commit()
             except Exception as assign_e:
                 print(f"Nota: No se pudo auto-asignar profesor principal a materia: {assign_e}")

        conn.close()
        return True # Indicate success
    except sqlite3.IntegrityError: # Likely duplicate name
        conn.close()
        return False
    except Exception as e:
        print(f"Error en add_subject_with_details: {e}")
        conn.rollback()
        conn.close()
        return False

def get_subjects():
    """Gets a list of all subjects (id, nombre)."""
    # Simplified version for the "Add Subject" view's potential list (if needed)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM Materias ORDER BY nombre")
    materias = cursor.fetchall()
    conn.close()
    return [dict(materia) for materia in materias]

def get_subject_details(subject_id):
    """Gets all details for a specific subject by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Materias WHERE id = ?", (subject_id,))
    subject = cursor.fetchone()
    conn.close()
    if subject: return dict(subject)
    return None

def update_subject_details(subject_id, nombre, id_profesor, horas, salon, inicio, fin):
    """Updates details for a specific subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Materias
            SET nombre = ?, id_profesor_principal = ?, horas_semanales = ?,
                salon = ?, fecha_inicio = ?, fecha_fin = ?
            WHERE id = ?
        """, (nombre, id_profesor, horas, salon, inicio, fin, subject_id))
        conn.commit()
        # Ensure the main professor is also assigned in Asignaciones
        if id_profesor:
             try:
                 cursor.execute("INSERT OR IGNORE INTO Asignaciones (id_profesor, id_materia) VALUES (?, ?)", (id_profesor, subject_id))
                 conn.commit()
             except Exception as assign_e: print(f"Note: Failed to auto-assign main prof: {assign_e}")
        conn.close()
        return True
    except Exception as e:
        print(f"Error in update_subject_details: {e}")
        conn.rollback(); conn.close(); return False

def delete_subject(subject_id):
    """Deletes a subject by ID. Cascades deletes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Materias WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting subject: {e}")
        conn.close()
        return False

# --- Assignment and Enrollment Functions ---
def assign_subject_to_prof(id_profesor, id_materia):
    """Assigns a subject to a professor (in Asignaciones table)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Asignaciones (id_profesor, id_materia) VALUES (?, ?)", (id_profesor, id_materia))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError: # Already assigned
        conn.close()
        return False

def enroll_student(id_alumno, id_materia):
    """Enrolls a student in a subject (in Inscripciones table)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Inscripciones (id_alumno, id_materia) VALUES (?, ?)", (id_alumno, id_materia))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError: # Already enrolled
        conn.close()
        return False

# --- Activity and Grade Management Functions ---

def add_activity_definition(id_materia, tipo_actividad, descripcion, peso, fecha_inicio, hora_inicio, fecha_fin, hora_fin):
    """
    Defines a new activity type for a subject.
    Creates a grade entry (default 0.0) for this activity for ALL enrolled students.
    """
    students = get_students_by_subject(id_materia)
    if not students:
        print("No students enrolled in this subject to add activity for.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    success_count = 0
    try:
        for student in students:
            student_id = student['id']
            # Check if this specific activity already exists for this student
            cursor.execute("SELECT id FROM Actividades WHERE id_alumno=? AND id_materia=? AND descripcion=?", (student_id, id_materia, descripcion))
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(
                    """INSERT INTO Actividades (id_alumno, id_materia, tipo_actividad, descripcion, calificacion, peso, fecha_inicio, hora_inicio, fecha_fin, hora_fin)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (student_id, id_materia, tipo_actividad, descripcion, 0.0, peso, fecha_inicio, hora_inicio, fecha_fin, hora_fin)
                )
                if cursor.rowcount > 0:
                    success_count += 1
        conn.commit()
        conn.close()
        return success_count > 0 or (success_count == 0 and students)
    except Exception as e:
        print(f"Error in add_activity_definition: {e}")
        conn.rollback(); conn.close(); return False

def update_activity(id_actividad, descripcion, calificacion, peso):
    """Updates an existing individual grade entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Actividades SET descripcion = ?, calificacion = ?, peso = ? WHERE id = ?",
            (descripcion, calificacion, peso, id_actividad)
        )
        conn.commit(); conn.close(); return True
    except Exception as e: print(f"Error in update_activity: {e}"); conn.close(); return False

def delete_activity(id_actividad):
    """Deletes a specific grade entry by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Actividades WHERE id = ?", (id_actividad,))
        conn.commit(); conn.close(); return True
    except Exception as e: print(f"Error in delete_activity: {e}"); conn.close(); return False

def get_activity_definition(id_materia, descripcion):
    """Gets the definition details for an activity within a subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tipo_actividad, peso, fecha_inicio, hora_inicio, fecha_fin, hora_fin
        FROM Actividades
        WHERE id_materia = ? AND descripcion = ?
        LIMIT 1
    """, (id_materia, descripcion))
    definition = cursor.fetchone()
    conn.close()
    if definition: return dict(definition)
    return None

def update_activity_definition(id_materia, old_descripcion, new_tipo, new_descripcion, new_peso, new_fecha_inicio, new_hora_inicio, new_fecha_fin, new_hora_fin):
    """Updates the definition details for ALL instances of an activity in a subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Actividades
            SET tipo_actividad = ?, descripcion = ?, peso = ?,
                fecha_inicio = ?, hora_inicio = ?, fecha_fin = ?, hora_fin = ?
            WHERE id_materia = ? AND descripcion = ?
        """, (new_tipo, new_descripcion, new_peso, new_fecha_inicio, new_hora_inicio, new_fecha_fin, new_hora_fin, id_materia, old_descripcion))
        conn.commit()
        updated_rows = cursor.rowcount
        conn.close()
        return updated_rows > 0
    except Exception as e:
        print(f"Error in update_activity_definition: {e}")
        conn.rollback(); conn.close(); return False

def delete_activity_definition(id_materia, descripcion):
    """Deletes ALL grade entries for a specific activity definition within a subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM Actividades WHERE id_materia = ? AND descripcion = ?",
            (id_materia, descripcion)
        )
        conn.commit()
        deleted_rows = cursor.rowcount
        conn.close()
        return deleted_rows > 0
    except Exception as e:
        print(f"Error in delete_activity_definition: {e}")
        conn.rollback(); conn.close(); return False

def get_distinct_activities_for_subject(id_materia):
    """Gets unique activity descriptions and their weights for a subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT descripcion, peso
        FROM Actividades
        WHERE id_materia = ? AND descripcion IS NOT NULL AND descripcion != ''
        GROUP BY descripcion
        ORDER BY MIN(id) -- Order by approx creation time
    """, (id_materia,))
    activities = cursor.fetchall()
    conn.close()
    return [(act['descripcion'], act['peso']) for act in activities]

def get_grades_for_subject(id_materia):
    """Gets all grades for all students in a specific subject, organized for the table view."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, id_alumno, descripcion, calificacion
        FROM Actividades WHERE id_materia = ?
    """, (id_materia,))
    grades = cursor.fetchall()
    conn.close()
    # {student_id: {activity_desc: {'calificacion': x, 'id': y}}}
    grades_dict = {}
    for grade in grades:
        s_id = grade['id_alumno']; desc = grade['descripcion']
        if s_id not in grades_dict: grades_dict[s_id] = {}
        grades_dict[s_id][desc] = {'calificacion': grade['calificacion'], 'id': grade['id']}
    return grades_dict

def add_or_update_grade(id_alumno, id_materia, descripcion, peso, calificacion, activity_id=None):
    """Adds or updates a specific grade entry for a student/subject/activity."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if an entry for this student/subject/description already exists
        cursor.execute(
            "SELECT id FROM Actividades WHERE id_alumno = ? AND id_materia = ? AND descripcion = ?",
            (id_alumno, id_materia, descripcion)
        )
        existing = cursor.fetchone()

        if existing:
            # Update the existing grade and potentially the weight if definition changed
            cursor.execute(
                "UPDATE Actividades SET calificacion = ?, peso = ? WHERE id = ?",
                (calificacion, peso, existing['id'])
            )
        else:
            # If it doesn't exist, create it (should ideally exist from definition)
            print(f"Warning: Creating grade entry on the fly for {descripcion}")
            # Insert with known data, try to get definition data if possible
            definition = get_activity_definition(id_materia, descripcion)
            tipo = definition.get('tipo_actividad', 'Desconocido') if definition else 'Desconocido'
            f_inicio = definition.get('fecha_inicio') if definition else None
            h_inicio = definition.get('hora_inicio') if definition else None
            f_fin = definition.get('fecha_fin') if definition else None
            h_fin = definition.get('hora_fin') if definition else None
            cursor.execute(
                """INSERT INTO Actividades (id_alumno, id_materia, descripcion, calificacion, peso, tipo_actividad, fecha_inicio, hora_inicio, fecha_fin, hora_fin)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (id_alumno, id_materia, descripcion, calificacion, peso, tipo, f_inicio, h_inicio, f_fin, h_fin)
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in add_or_update_grade: {e}")
        conn.rollback(); conn.close(); return False

# --- Data Retrieval for Views ---

def get_subjects_by_professor(id_profesor):
    """Gets subjects taught by a specific professor."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.nombre FROM Materias m JOIN Asignaciones a ON m.id = a.id_materia
        WHERE a.id_profesor = ? ORDER BY m.nombre
    """, (id_profesor,))
    materias = cursor.fetchall()
    conn.close()
    return [dict(m) for m in materias]

def get_students_by_subject(id_materia):
    """Gets students enrolled in a specific subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.nombre_completo, u.username FROM Usuarios u JOIN Inscripciones i ON u.id = i.id_alumno
        WHERE i.id_materia = ? ORDER BY u.nombre_completo
    """, (id_materia,))
    alumnos = cursor.fetchall()
    conn.close()
    return [dict(a) for a in alumnos]

def get_activities_by_student_subject(id_alumno, id_materia):
    """Gets all activity grades for a specific student in a specific subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Actividades WHERE id_alumno = ? AND id_materia = ? ORDER BY id", (id_alumno, id_materia))
    actividades = cursor.fetchall()
    conn.close()
    return [dict(act) for act in actividades]

def get_weighted_average(id_alumno, id_materia):
    """Calculates the weighted average grade for a student in a subject."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(calificacion * peso) AS suma_ponderada, SUM(peso) AS suma_pesos
        FROM Actividades WHERE id_alumno = ? AND id_materia = ?
    """, (id_alumno, id_materia))
    result = cursor.fetchone()
    conn.close()
    if result and result["suma_pesos"] is not None and result["suma_pesos"] > 0:
        try:
            promedio = result["suma_ponderada"] / result["suma_pesos"]
            return max(0, min(round(promedio, 2), 100)) # Clamp between 0 and 100
        except TypeError: return 0.0
    return 0.0

def get_subjects_by_student(id_alumno):
    """Gets subjects a specific student is enrolled in."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.nombre FROM Materias m JOIN Inscripciones i ON m.id = i.id_materia
        WHERE i.id_alumno = ? ORDER BY m.nombre
    """, (id_alumno,))
    materias = cursor.fetchall()
    conn.close()
    return [dict(m) for m in materias]