# student_subjects_view.py
import tkinter as tk
from tkinter import ttk
import db_manager # Para obtener datos de materias y calificaciones

class MateriaWidget(ttk.Frame):
    """
    Widget que muestra una materia con ancho fijo y se expande verticalmente si hay detalles.
    """
    def __init__(self, parent, materia_info, bg_color):
        super().__init__(parent, style="CardBody.TFrame", padding=0)

        self.materia_info = materia_info
        self.bg_color = bg_color
        self.is_expanded = False
        self.card_width = 300  # ancho fijo

        # Elegir estilo según color
        style_name = "BlueCard.TLabelframe"
        if bg_color == "#0A4174": style_name = "BlueCard.TLabelframe"
        elif bg_color == "#F0C000": style_name = "YellowCard.TLabelframe"
        elif bg_color == "#681a1a": style_name = "MaroonCard.TLabelframe"

        # Contenedor principal
        self.container = ttk.LabelFrame(self, width=self.card_width, style=style_name, labelwidget=tk.Label())
        
        # --- CORRECCIÓN 2: Comentar pack_propagate y cambiar el pack ---
        # self.container.pack_propagate(False)  # <-- ESTO DEBE ESTAR COMENTADO
        self.container.pack(fill='x', expand=True, padx=5, pady=5) # <-- USAR FILL Y EXPAND

        # --- Header ---
        self.header_frame = ttk.Frame(self.container, style="CardBody.TFrame")
        self.header_frame.pack(fill='x', expand=True, padx=1, pady=1)

        # Título
        self.lbl_title_widget = tk.Label(
            self.container, # No importa que el parent sea 'self.container'
            text=self.materia_info.get('nombre', 'Materia Desconocida'),
            font=("Helvetica", 11, "bold"),
            background=self.bg_color,
            foreground="white" if bg_color != "#F0C000" else "#333333",
            anchor="center",
            padx=10, pady=5
        )
        self.container.configure(labelwidget=self.lbl_title_widget) # Se asigna como título

        # Promedio
        promedio_text = self.materia_info.get('promedio', 'N/A')
        promedio_val = f"{promedio_text:.1f}" if isinstance(promedio_text, (int, float)) else "N/A"
        self.promedio_label = ttk.Label(
            self.header_frame,
            text=f"Promedio: {promedio_val}",
            style="CardAvg.TLabel",
            anchor="w"
        )
        self.promedio_label.pack(fill='x', padx=10, pady=(5, 10))

        # Detalles (oculto al inicio)
        self.details_frame = ttk.Frame(self.header_frame, style="CardBody.TFrame")
        # No se empaqueta aún

        # Hacer header clickeable
        for widget in [self.header_frame, self.promedio_label, self.container]:
            widget.bind("<Button-1>", self.toggle_expand)
        self.lbl_title_widget.bind("<Button-1>", self.toggle_expand)

    def toggle_expand(self, event=None):
        if self.is_expanded:
            self.details_frame.pack_forget()
            self.is_expanded = False
        else:
            # Limpiar detalles previos
            for child in self.details_frame.winfo_children():
                child.destroy()

            calificaciones = self.materia_info.get('calificaciones_detalle', {})

            # --- INICIO DE LA CORRECCIÓN 1 ---
            if not calificaciones:
                # Si no hay calificaciones, mostrar el mensaje
                max_width = self.card_width - 40 # 300 (ancho) - 40 (padding)
                ttk.Label(
                    self.details_frame, 
                    text="No hay calificaciones detalladas.", 
                    style="CardDetail.TLabel",
                    wraplength=max_width,
                    justify="center"
                ).pack(pady=5, padx=10)
            else:
                # Si SÍ hay, agregar detalles
                for nombre_act, calif_dict in calificaciones.items():
                    calif_val = calif_dict.get('calificacion', 'N/A')
                    calif_str = f"{calif_val:.1f}" if isinstance(calif_val, (int, float)) else str(calif_val)

                    detail_line = ttk.Frame(self.details_frame, style="CardBody.TFrame")
                    max_text_width = self.card_width - 80

                    ttk.Label(detail_line, text=f"{nombre_act}:", style="CardDetail.TLabel",
                              anchor="w", wraplength=max_text_width).pack(side=tk.LEFT, fill='x', expand=True)
                    ttk.Label(detail_line, text=calif_str, style="CardDetail.TLabel", anchor="e").pack(side=tk.RIGHT)

                    detail_line.pack(fill='x', padx=10, pady=1)

            # Estas líneas ahora se ejecutan en AMBOS casos,
            # mostrando el frame de detalles (con el mensaje o con la lista)
            self.details_frame.pack(fill='x', pady=(0, 10))
            self.is_expanded = True
            # --- FIN DE LA CORRECCIÓN 1 ---




def create_student_subjects_view(parent_frame, user_data):
    """Crea la vista de materias con scroll y tarjetas."""

    student_id = user_data['id'] # ID numérico del alumno
    
    # Contenedor principal que se ajustará al parent_frame
    container = ttk.Frame(parent_frame, style="Main.TFrame")
    container.pack(fill=tk.BOTH, expand=True)
    container.rowconfigure(1, weight=1)
    container.columnconfigure(0, weight=1)

    ttk.Label(container, text="Materias Inscritas", font=("Helvetica", 16, "bold"), style="TLabel").grid(row=0, column=0, pady=10, sticky='nw', padx=10)

    # --- Canvas y Scrollbar ---
    canvas = tk.Canvas(container, bg='#f0f2f5', highlightthickness=0) # Usar color de fondo
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=1, column=0, sticky='nsew')
    scrollbar.grid(row=1, column=1, sticky='ns')

    # Frame interior del canvas
    materias_frame = ttk.Frame(canvas, style="Main.TFrame", padding=(10,0)) # Padding superior
    canvas_window = canvas.create_window((0, 0), window=materias_frame, anchor='nw')

    # --- Cargar y procesar datos ---
    materias_inscritas = db_manager.get_subjects_by_student(student_id)
    
    materia_widgets_list = []

    # --- Funciones para el scroll con la rueda del ratón ---
    def _on_mousewheel(event):
        # Maneja el scroll multiplataforma
        if event.delta: # Windows/macOS
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else: # Linux
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    def _bind_mousewheel(widget):
        # Enlaza el evento de scroll a un widget y todos sus hijos
        widget.bind("<MouseWheel>", _on_mousewheel)
        widget.bind("<Button-4>", _on_mousewheel)
        widget.bind("<Button-5>", _on_mousewheel)
        for child in widget.winfo_children():
            _bind_mousewheel(child)
    
    # Enlazar el scroll al canvas principal
    canvas.bind("<MouseWheel>", _on_mousewheel)
    canvas.bind("<Button-4>", _on_mousewheel)
    canvas.bind("<Button-5>", _on_mousewheel)
    
    # Enlazar el scroll al frame que contiene las materias
    materias_frame.bind("<MouseWheel>", _on_mousewheel)
    materias_frame.bind("<Button-4>", _on_mousewheel)
    materias_frame.bind("<Button-5>", _on_mousewheel)


    if not materias_inscritas:
        ttk.Label(materias_frame, text="No tienes materias asignadas.", style="TLabel").pack(pady=20)
    else:
        # Colores actualizados
        colores = ["#0A4174", "#F0C000", "#681a1a"] # Azul, Amarillo, Guinda
        
        for i, materia in enumerate(materias_inscritas):
            materia_id = materia['id']
            # Obtener detalles de calificaciones
            actividades = db_manager.get_activities_by_student_subject(student_id, materia_id)
            calificaciones_detalle = {act['descripcion']: {'calificacion': act['calificacion'], 'id': act['id']} for act in actividades}

            # Calcular promedio
            promedio = db_manager.get_weighted_average(student_id, materia_id)

            materia_info_completa = {
                'id': materia_id,
                'nombre': materia['nombre'],
                'promedio': promedio,
                'calificaciones_detalle': calificaciones_detalle
            }

            color = colores[i % len(colores)]
            materia_widget = MateriaWidget(materias_frame, materia_info_completa, color)
            
            # Enlazar scroll a la tarjeta
            _bind_mousewheel(materia_widget) 
            
            materia_widgets_list.append(materia_widget)

    # --- Lógica de Layout Responsivo ---
    def layout_materias(event=None):
        canvas_width = canvas.winfo_width()
        if canvas_width <= 1: return # Evitar cálculo si no es visible

        # Este valor DEBE coincidir con self.card_width en la clase MateriaWidget
        card_width = 300 
        padding = 10
        num_columns = max(1, canvas_width // (card_width + padding*2)) # Columnas que caben

        # Limitar columnas si se desea
        # num_columns = min(num_columns, 4)

        for i, widget in enumerate(materia_widgets_list):
            row = i // num_columns
            col = i % num_columns
            
            # Corregido a 'new' para anclar arriba
            widget.grid(row=row, column=col, padx=padding, pady=padding, sticky='new')

        # Configurar peso de columnas para centrado/expansión
        for c in range(num_columns):
            materias_frame.columnconfigure(c, weight=1)

        # Actualizar scrollregion
        materias_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Ajustar ancho del frame interior al canvas para que el scroll funcione bien
        canvas.itemconfig(canvas_window, width=canvas_width)

    # Binds para responsividad y scroll
    materias_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    # Corregido el Typo
    canvas.bind('<Configure>', layout_materias)

    # Layout inicial
    layout_materias()

    return container # Devolver el contenedor principal