# app_styles.py
from tkinter import ttk

def configure_styles():
    """Configura los estilos de ttk para la aplicación."""
    style = ttk.Style()

    # --- Colores ---
    COLOR_BACKGROUND = "#f0f2f5"; COLOR_GREEN_DARK = "#28a745"; COLOR_GREEN_HOVER = "#218838"; COLOR_RED = "#f44336"; COLOR_RED_HOVER = "#da190b"; COLOR_WHITE = "#ffffff"; COLOR_CARD_MAROON = "#800000"; COLOR_CARD_YELLOW = "#ffc107"; COLOR_CARD_BLUE = "#007bff"; COLOR_DARK_TEXT = "#333333"

    # --- Estilos Base ---
    style.configure("Main.TFrame", background=COLOR_BACKGROUND)
    style.configure("TButton", font=("Helvetica", 10), padding=10)
    style.configure("TLabel", background=COLOR_BACKGROUND, font=("Helvetica", 11))
    style.configure("TEntry", font=("Helvetica", 11), padding=5) # Añadir padding a Entry
    style.configure("TCombobox", font=("Helvetica", 11))
    style.configure("TLabelframe", background=COLOR_BACKGROUND, padding=10)
    style.configure("TLabelframe.Label", background=COLOR_BACKGROUND, font=("Helvetica", 10, "bold"))

    # --- Botones Específicos ---
    style.configure("Accent.TButton", background="#4CAF50", foreground=COLOR_WHITE); style.map("Accent.TButton", background=[("active", "#45a049")])
    style.configure("Danger.TButton", background=COLOR_RED, foreground=COLOR_WHITE); style.map("Danger.TButton", background=[("active", COLOR_RED_HOVER)])
    style.configure("Green.TButton", background=COLOR_GREEN_DARK, foreground=COLOR_WHITE, font=("Helvetica", 12, "bold"), padding=10); style.map("Green.TButton", background=[("active", COLOR_GREEN_HOVER)])

    # --- Sidebar ---
    # Padding ajustado para ícono y texto
    style.configure("Sidebar.TButton", font=("Helvetica", 11), foreground=COLOR_WHITE, background=COLOR_GREEN_DARK, anchor="w", padding=(10, 8))
    style.map("Sidebar.TButton", background=[("active", COLOR_GREEN_HOVER), ("selected", COLOR_GREEN_HOVER)]) # Estilo para botón seleccionado

    # --- Tarjetas Alumno (LabelFrame coloreado) ---
    style.configure("CardBody.TFrame", background=COLOR_WHITE); style.configure("CardBody.TLabel", background=COLOR_WHITE, font=("Helvetica", 10)); style.configure("CardAvg.TLabel", background=COLOR_WHITE, font=("Helvetica", 10, "bold")); style.configure("CardDetail.TLabel", background=COLOR_WHITE, font=("Helvetica", 9))
    style.configure("MaroonCard.TLabelframe", background=COLOR_WHITE, bordercolor=COLOR_DARK_TEXT, borderwidth=1, relief="solid"); style.configure("MaroonCard.TLabelframe.Label", background=COLOR_CARD_MAROON, foreground=COLOR_WHITE, font=("Helvetica", 11, "bold"), padding=(10, 5), anchor="center")
    style.configure("YellowCard.TLabelframe", background=COLOR_WHITE, bordercolor=COLOR_DARK_TEXT, borderwidth=1, relief="solid"); style.configure("YellowCard.TLabelframe.Label", background=COLOR_CARD_YELLOW, foreground=COLOR_DARK_TEXT, font=("Helvetica", 11, "bold"), padding=(10, 5), anchor="center")
    style.configure("BlueCard.TLabelframe", background=COLOR_WHITE, bordercolor=COLOR_DARK_TEXT, borderwidth=1, relief="solid"); style.configure("BlueCard.TLabelframe.Label", background=COLOR_CARD_BLUE, foreground=COLOR_WHITE, font=("Helvetica", 11, "bold"), padding=(10, 5), anchor="center")

    # --- NUEVO: Botón pequeño para "editar" foto (placeholder) ---
    style.configure("EditPhoto.TButton", padding=1, relief="flat", background=COLOR_BACKGROUND)
    style.map("EditPhoto.TButton", background=[("active", "#cccccc")])


    return style