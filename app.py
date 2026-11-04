import base64
import json
import os
import streamlit as st
from google import genai

# Configuración de página
st.set_page_config(page_title="Playeras Tricolor", page_icon="img/logo.png", layout="wide")


# Función para cargar la fuente en Base64 de forma segura
def incluir_fuente_local(ruta_font):
  if os.path.exists(ruta_font):
    with open(ruta_font, "rb") as f:
      encoded = base64.b64encode(f.read()).decode()
    return f"data:font/ttf;charset=utf-8;base64,{encoded}"
  return ""


font_base64 = incluir_fuente_local("fonts/Triforce.ttf")

if font_base64:
  st.markdown(
      f"""
    <style>
    @font-face {{
        font-family: 'TriforcePersonalizada';
        src: url('{font_base64}') format('truetype');
    }}

    /* Aplicar la fuente personalizada en títulos principales */
    h1, h2, .stMarkdown h1, .stMarkdown h2 {{
        font-family: 'TriforcePersonalizada', sans-serif !important;
        letter-spacing: 1px;
    }}
    </style>
    """,
      unsafe_allow_html=True,
  )

# Inicialización segura de Gemini
GEMINI_KEY = ""
try:
  if "GEMINI_API_KEY" in os.environ:
    GEMINI_KEY = os.environ["GEMINI_API_KEY"]
  elif hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
  pass

client = None
if GEMINI_KEY:
  try:
    client = genai.Client(api_key=GEMINI_KEY)
  except Exception:
    pass

# Control de accesos (Visitas)
if "contador_accesos" not in st.session_state:
  st.session_state.contador_accesos = 1
else:
  st.session_state.contador_accesos += 1

if "carrito" not in st.session_state:
  st.session_state.carrito = []

# Estados de Autenticación
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "user_role" not in st.session_state:
  st.session_state.user_role = None
if "user_email" not in st.session_state:
  st.session_state.user_email = ""


# Cargar base de datos
def cargar_datos():
  if os.path.exists("data/base_datos.json"):
    try:
      with open("data/base_datos.json", "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception as e:
      st.error(f"Error al leer base_datos.json: {e}")
  return {"productos": [], "clientes": [], "proveedores": []}


db = cargar_datos()

# --- PANEL DE LOGIN / REGISTRO VISIBLE EN LA BARRA LATERAL ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔐 Control de Acceso")

if not st.session_state.logged_in:
  modo_auth = st.sidebar.radio(
      "Seleccione una opción", ["Iniciar Sesión", "Registrarse"]
  )

  if modo_auth == "Iniciar Sesión":
    correo_ing = st.sidebar.text_input("Correo electrónico")
    pass_ing = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Ingresar"):
      if correo_ing == "admin@tricolor.com" and pass_ing == "admin123":
        st.session_state.logged_in = True
        st.session_state.user_role = "admin"
        st.session_state.user_email = correo_ing
        st.sidebar.success("¡Bienvenido, Administrador!")
        st.rerun()
      else:
        cliente_encontrado = next(
            (c for c in db.get("clientes", []) if c.get("correo") == correo_ing),
            None,
        )
        if cliente_encontrado:
          st.session_state.logged_in = True
          st.session_state.user_role = "cliente"
          st.session_state.user_email = correo_ing
          st.sidebar.success(f"¡Bienvenido, {cliente_encontrado['nombre']}!")
          st.rerun()
        else:
          st.sidebar.error("Correo o contraseña incorrectos.")

  else:
    reg_nombre = st.sidebar.text_input("Nombre completo")
    reg_correo = st.sidebar.text_input("Correo para registro")
    reg_tel = st.sidebar.text_input("Teléfono")
    reg_pass = st.sidebar.text_input("Contraseña nueva", type="password")

    if st.sidebar.button("Crear cuenta"):
      if reg_nombre and reg_correo and reg_pass:
        nuevo_cli = {
            "id": len(db.get("clientes", [])) + 1,
            "nombre": reg_nombre,
            "correo": reg_correo,
            "verificado": True,
            "telefono": reg_tel,
        }
        db.setdefault("clientes", []).append(nuevo_cli)
        try:
          with open("data/base_datos.json", "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
          st.sidebar.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
        except Exception as e:
          st.sidebar.error(f"Error al guardar el usuario: {e}")
      else:
        st.sidebar.error("Por favor completa los campos requeridos.")
else:
  st.sidebar.success(
      f"Sesión activa:\n**{st.session_state.user_email}**\n*(Rol:"
      f" {st.session_state.user_role.upper()})*"
  )
  if st.sidebar.button("Cerrar Sesión"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_email = ""
    st.rerun()

st.sidebar.markdown("---")

# --- MENÚ DE NAVEGACIÓN DINÁMICO ---
menu_opciones = ["Inicio", "Catálogo (20 Productos)", "Carrito y Pagos"]
if st.session_state.logged_in and st.session_state.user_role == "admin":
  menu_opciones.append("Gestión (Clientes y Proveedores)")
menu_opciones.append("Ayuda / IA")

opcion = st.sidebar.radio("Menú de Navegación", menu_opciones)

# --- ESTILOS CSS AISLADOS (SOLO PARA LOGO Y BARRA LATERAL) ---
st.markdown(
    """
    <style>
    /* Estilo exclusivo y aislado para el LOGO principal */
    .logo-exclusivo img {
        width: 130px !important;
        height: auto !important;
        object-fit: contain !important;
        border-radius: 0px !important;
    }

    /* Barra lateral azul y blanca */
    [data-testid="stSidebar"] {
        background-color: #0b2545;
        border-right: 2px solid #134074;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-size: 17px !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
        font-size: 17px !important;
        color: #eeeeee !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] button {
        background-color: #134074 !important;
        color: #ffffff !important;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Encabezado visual principal
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
  if os.path.exists("img/logo.png"):
    with open("img/logo.png", "rb") as img_file:
      logo_base64 = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <div class="logo-exclusivo">
            <img src="data:image/png;base64,{logo_base64}">
        </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    st.markdown("### 👕")

with col_titulo:
  st.markdown(
      "<h1 style='color: #E61C24; margin-bottom: 0;'>PLAYERAS TRICOLOR</h1>",
      unsafe_allow_html=True,
  )
  st.caption(
      f"Visitas registradas en el sistema: {st.session_state.contador_accesos}"
  )

st.markdown("---")

# --- VISTAS DE LA APLICACIÓN ---

if opcion == "Inicio":
  st.header("Bienvenido a Playeras Tricolor")
  st.write(
      "Explora nuestro catálogo exclusivo con filtros avanzados y la mejor calidad"
      " tricolor."
  )
  if not st.session_state.logged_in:
    st.info(
        "💡 **Nota:** Puedes navegar y agregar productos al carrito libremente."
        " Se te pedirá iniciar sesión al momento de realizar tu compra."
    )

elif opcion == "Catálogo (20 Productos)":
  st.header("Catálogo de Playeras")

  # --- FILTROS DE BÚSQUEDA ---
  st.markdown("### 🔍 Filtros de Búsqueda")
  col_f1, col_f2 = st.columns(2)
  with col_f1:
    filtro_estilo = st.selectbox(
        "Estilo", ["Todos", "Formal", "Informal"]
    )
  with col_f2:
    filtro_genero = st.selectbox("Género", ["Todos", "Hombre", "Mujer"])

  productos = db.get("productos", [])

  # Aplicar filtros
  productos_filtrados = []
  for p in productos:
    estilo_prod = p.get("estilo", "Informal")
    genero_prod = p.get("genero", "Hombre")

    match_estilo = (
        filtro_estilo == "Todos" or estilo_prod.lower() == filtro_estilo.lower()
    )
    match_genero = (
        filtro_genero == "Todos" or genero_prod.lower() == genero_prod.lower()
    )  # Corregido para filtrar género correctamente

    if match_estilo and match_genero:
      productos_filtrados.append(p)

  if not productos_filtrados:
    st.warning("No se encontraron productos con los filtros seleccionados.")
  else:
    # ORDENAR EN FILAS ESTRICTAS DE 3 COLUMNAS
    for i in range(0, len(productos_filtrados), 3):
      fila_productos = productos_filtrados[i : i + 3]
      cols = st.columns(3)

      for j, prod in enumerate(fila_productos):
        with cols[j]:
          with st.container(border=True):
            st.subheader(prod.get("nombre", "Sin nombre"))
            img_path = prod.get("imagen", "")

            # Renderizado de imágenes con Base64
            if img_path and os.path.exists(img_path):
              with open(img_path, "rb") as p_img:
                p_base64 = base64.b64encode(p_img.read()).decode()
              st.markdown(
                  f'<img src="data:image/jpeg;base64,{p_base64}" style="width:'
                  " 100%; height: 210px; object-fit: cover; border-radius: 8px;"
                  ' margin-bottom: 10px;">',
                  unsafe_allow_html=True,
              )
            else:
              st.warning("Imagen no disponible")

            st.write(f"**Precio:** ${prod.get('precio', 0)} MXN")
            st.write(
                f"**Stock:** {prod.get('stock', 0)} | **Estilo:**"
                f" {prod.get('estilo', 'Informal')} | **Género:**"
                f" {prod.get('genero', 'Hombre')}"
            )

            if st.button("Agregar al carrito", key=f"add_{prod.get('id', i+j)}"):
              st.session_state.carrito.append(prod)
              st.success(f"¡{prod.get('nombre')} agregado al carrito!")

elif opcion == "Carrito y Pagos":
  st.header("Carrito de Compras y Pasarela de Pagos")
  if not st.session_state.carrito:
    st.warning("Tu carrito está vacío. Agrega productos desde el catálogo.")
  else:
    total = 0
    for item in st.session_state.carrito:
      st.write(f"- {item.get('nombre')} : ${item.get('precio')} MXN")
      total += item.get("precio", 0)
    st.markdown(f"### Total a pagar: **${total} MXN**")
    st.markdown("---")

    if not st.session_state.logged_in:
      st.warning(
          "⚠️ **Debes iniciar sesión o registrar una cuenta en la barra lateral"
          " izquierda** para poder confirmar tu compra."
      )
    else:
      st.subheader("Pasarela de Pago Segura")
      st.write(
          f"Comprando como: **{st.session_state.user_email}**"
          f" ({st.session_state.user_role.upper()})"
      )

      tarjeta = st.text_input("Número de Tarjeta (16 dígitos):", max_chars=16)
      es_humano = st.checkbox("Verificación anti-bots (No soy un robot)")

      if st.button("Procesar Pago y Confirmar Compra"):
        if len(tarjeta) == 16 and es_humano:
          st.balloons()
          st.success("¡Compra exitosa! Estatus de envío: En proceso.")
          st.session_state.carrito = []
        else:
          st.error(
              "Por favor verifica que la tarjeta tenga exactamente 16 dígitos y"
              " marca la casilla anti-bots."
          )

elif opcion == "Gestión (Clientes y Proveedores)":
  st.header("Panel de Administración y Gestión")
  tab_cli, tab_prov, tab_prod = st.tabs(
      [
          "👥 Clientes Registrados",
          "📦 Proveedores y Garantías",
          "➕ Agregar Producto",
      ]
  )

  with tab_cli:
    st.subheader("Base de Datos de Clientes")
    clientes = db.get("clientes", [])
    if clientes:
      for cli in clientes:
        st.write(
            f"- **ID:** {cli.get('id')} | **Nombre:** {cli.get('nombre')} |"
            f" **Correo:** {cli.get('correo')} | **Tel:**"
            f" {cli.get('telefono')}"
        )
    else:
      st.info("No hay clientes registrados.")

  with tab_prov:
    st.subheader("Proveedores Activos")
    proveedores = db.get("proveedores", [])
    if proveedores:
      for prov in proveedores:
        st.write(
            f"- **{prov.get('nombre')}** | Contacto: {prov.get('contacto')} |"
            f" Garantía: `{prov.get('garantia')}`"
        )
    else:
      st.info("No hay proveedores registrados.")

  with tab_prod:
    st.subheader("Registrar Nuevo Producto al Catálogo")
    with st.form("form_nuevo_producto"):
      nuevo_nombre = st.text_input("Nombre de la Playera")
      nuevo_precio = st.number_input(
          "Precio (MXN)", min_value=1.0, value=250.0
      )
      nuevo_stock = st.number_input("Stock disponible", min_value=0, value=10)
      nuevo_estilo = st.selectbox("Estilo", ["Formal", "Informal"])
      nuevo_genero = st.selectbox("Género", ["Hombre", "Mujer"])
      nueva_imagen = st.text_input(
          "Ruta de imagen (Ej: img/producto_1.jpeg)", value="img/producto_1.jpeg"
      )

      submitted = st.form_submit_button("Guardar Producto")
      if submitted:
        if nuevo_nombre:
          nuevo_id = (
              max([p.get("id", 0) for p in db.get("productos", [])], default=0)
              + 1
          )
          prod_data = {
              "id": nuevo_id,
              "nombre": nuevo_nombre,
              "precio": float(nuevo_precio),
              "stock": int(nuevo_stock),
              "ventas": 0,
              "estilo": nuevo_estilo,
              "genero": nuevo_genero,
              "imagen": nueva_imagen,
          }
          db.setdefault("productos", []).append(prod_data)
          try:
            with open("data/base_datos.json", "w", encoding="utf-8") as f:
              json.dump(db, f, indent=4, ensure_ascii=False)
            st.success(f"¡Producto '{nuevo_nombre}' agregado con éxito!")
          except Exception as e:
            st.error(f"Error al guardar en la base de datos: {e}")
        else:
          st.error("El nombre del producto es obligatorio.")

elif opcion == "Ayuda / IA":
  st.header("Asistente Virtual")
  if client:
    pregunta = st.text_input("Pregúntale algo al asistente sobre las playeras:")
    if pregunta:
      try:
        respuesta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "Eres el asistente de la tienda 'Playeras Tricolor':"
                f" {pregunta}"
            ),
        )
        st.write(respuesta.text)
      except Exception as e:
        st.error(f"Error al conectar con Gemini: {e}")
  else:
    st.warning(
        "El asistente de IA no está disponible (falta configurar la API Key)."
    )