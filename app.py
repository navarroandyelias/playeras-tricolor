import base64
import json
import os
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Playeras Tricolor", page_icon="img/logo.png", layout="wide"
)


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
    h1, h2, .stMarkdown h1, .stMarkdown h2 {{
        font-family: 'TriforcePersonalizada', sans-serif !important;
        letter-spacing: 1px;
    }}
    </style>
    """,
      unsafe_allow_html=True,
  )

# Control de accesos (Visitas)
if "contador_accesos" not in st.session_state:
  st.session_state.contador_accesos = 1
else:
  st.session_state.contador_accesos += 1

if "carrito" not in st.session_state:
  st.session_state.carrito = []

if "direccion_envio" not in st.session_state:
  st.session_state.direccion_envio = ""

if "pedidos" not in st.session_state:
  st.session_state.pedidos = []  # Historial de compras / productos vendidos

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


def guardar_datos(datos):
  os.makedirs("data", exist_ok=True)
  with open("data/base_datos.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, indent=4, ensure_ascii=False)


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
          guardar_datos(db)
          st.sidebar.success(
              "¡Cuenta creada con éxito! Ya puedes iniciar sesión."
          )
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
menu_opciones = ["Inicio", "Catálogo (20 Productos)"]

if st.session_state.logged_in and st.session_state.user_role == "admin":
  menu_opciones.append("Seguimiento y Entregas (Admin)")
  menu_opciones.append("Gestión de Vendedores")
else:
  menu_opciones.append("Carrito y Seguimiento")

opcion = st.sidebar.radio("Menú de Navegación", menu_opciones)

# --- ESTILOS CSS AISLADOS ---
st.markdown(
    """
    <style>
    .logo-exclusivo img {
        width: 130px !important;
        height: auto !important;
        object-fit: contain !important;
        border-radius: 0px !important;
    }
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
      "Explora nuestro catálogo exclusivo con tallas, filtros avanzados y la"
      " mejor calidad tricolor."
  )
  if not st.session_state.logged_in:
    st.info(
        "💡 **Nota:** Puedes navegar y agregar productos al carrito libremente."
        " Se te pedirá iniciar sesión al momento de realizar tu compra."
    )

elif opcion == "Catálogo (20 Productos)":
  st.header("Catálogo de Playeras")

  st.markdown("### 🔍 Filtros de Búsqueda")
  col_f1, col_f2 = st.columns(2)
  with col_f1:
    filtro_estilo = st.selectbox("Estilo", ["Todos", "Formal", "Informal"])
  with col_f2:
    filtro_genero = st.selectbox("Género", ["Todos", "Hombre", "Mujer"])

  productos = db.get("productos", [])

  productos_filtrados = []
  for p in productos:
    estilo_prod = p.get("estilo", "Informal")
    genero_prod = p.get("genero", "Hombre")

    match_estilo = (
        filtro_estilo == "Todos" or estilo_prod.lower() == filtro_estilo.lower()
    )
    match_genero = (
        filtro_genero == "Todos" or genero_prod.lower() == genero_prod.lower()
    )

    if match_estilo and match_genero:
      productos_filtrados.append(p)

  if not productos_filtrados:
    st.warning("No se encontraron productos con los filtros seleccionados.")
  else:
    for i in range(0, len(productos_filtrados), 3):
      fila_productos = productos_filtrados[i : i + 3]
      cols = st.columns(3)

      for j, prod in enumerate(fila_productos):
        with cols[j]:
          with st.container(border=True):
            st.subheader(prod.get("nombre", "Sin nombre"))
            img_path = prod.get("imagen", "")

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

            # Selector de tallas (Chica, Mediana, Grande)
            talla_seleccionada = st.selectbox(
                "Talla", ["Chica", "Mediana", "Grande"], key=f"talla_{prod.get('id', i+j)}"
            )

            if st.session_state.user_role != "admin":
              if st.button("Agregar al carrito", key=f"add_{prod.get('id', i+j)}"):
                item_carrito = prod.copy()
                item_carrito["talla"] = talla_seleccionada
                st.session_state.carrito.append(item_carrito)
                st.success(f"¡{prod.get('nombre')} ({talla_seleccionada}) agregado!")
            else:
              st.info("Vista de Administrador (Catálogo)")

elif opcion == "Carrito y Seguimiento":
  st.header("🛒 Carrito de Compras, Dirección y Seguimiento")

  tab_c1, tab_c2 = st.tabs(["📦 Carrito y Pago", "🚚 Seguimiento de Pedidos"])

  with tab_c1:
    if not st.session_state.carrito:
      st.warning("Tu carrito está vacío. Agrega productos desde el catálogo.")
    else:
      total = 0
      for idx, item in enumerate(st.session_state.carrito):
        col_i1, col_i2 = st.columns([4, 1])
        with col_i1:
          st.write(
              f"- **{item.get('nombre')}** | Talla: `{item.get('talla')}` |"
              f" Precio: ${item.get('precio')} MXN"
          )
        with col_i2:
          if st.button("Quitar", key=f"quitar_c_{idx}"):
            st.session_state.carrito.pop(idx)
            st.rerun()
        total += item.get("precio", 0)

      st.markdown(f"### Total a pagar: **${total} MXN**")
      st.markdown("---")

      st.subheader("📍 Dirección de Envío")
      st.session_state.direccion_envio = st.text_area(
          "Ingresa calle, número, colonia, ciudad y código postal:",
          value=st.session_state.direccion_envio,
      )

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

        tarjeta = st.text_input(
            "Número de Tarjeta (16 dígitos):", max_chars=16, type="password"
        )
        es_humano = st.checkbox("Verificación anti-bots (No soy un robot)")

        if st.button("Procesar Pago y Confirmar Compra"):
          if not st.session_state.direccion_envio.strip():
            st.error("Por favor ingresa una dirección de envío.")
          elif len(tarjeta) == 16 and es_humano:
            nuevo_pedido = {
                "id_pedido": len(st.session_state.pedidos) + 1,
                "usuario": st.session_state.user_email,
                "productos": st.session_state.carrito.copy(),
                "total": total,
                "direccion": st.session_state.direccion_envio,
                "estatus": "En proceso",
            }
            st.session_state.pedidos.append(nuevo_pedido)
            st.balloons()
            st.success("¡Compra exitosa! Pedido registrado correctamente.")
            st.session_state.carrito = []
          else:
            st.error(
                "Por favor verifica que la tarjeta tenga 16 dígitos y marca la"
                " casilla anti-bots."
            )

  with tab_c2:
    st.subheader("📦 Estado y Seguimiento de tus Pedidos")
    if not st.session_state.pedidos:
      st.info("No tienes pedidos activos o recientes.")
    else:
      for pedido in st.session_state.pedidos:
        if pedido["usuario"] != st.session_state.user_email:
          continue

        with st.container(border=True):
          st.write(f"**Pedido ID:** #{pedido['id_pedido']}")
          st.write(f"**Dirección:** {pedido['direccion']}")
          st.write(f"**Total:** ${pedido['total']} MXN")
          st.write(f"**Estatus actual:** `{pedido['estatus']}`")

          if pedido["estatus"] == "En proceso":
            if st.button("Cancelar Compra", key=f"cancel_{pedido['id_pedido']}"):
              pedido["estatus"] = "Cancelado"
              st.success(f"El pedido #{pedido['id_pedido']} ha sido cancelado.")
              st.rerun()

elif opcion == "Seguimiento y Entregas (Admin)":
  st.header("🚚 Panel de Administración: Seguimiento y Control de Entregas")
  if not st.session_state.pedidos:
    st.info("No hay pedidos registrados en el sistema.")
  else:
    filtro_estado_admin = st.selectbox(
        "Filtrar pedidos por estatus",
        ["Todos", "En proceso", "En camino", "Entregado", "Cancelado"]
    )

    pedidos_filtrados_admin = st.session_state.pedidos
    if filtro_estado_admin != "Todos":
      pedidos_filtrados_admin = [
          p for p in st.session_state.pedidos if p["estatus"] == filtro_estado_admin
      ]

    if not pedidos_filtrados_admin:
      st.info(f"No hay pedidos con el estatus '{filtro_estado_admin}'.")
    else:
      for idx, pedido in enumerate(pedidos_filtrados_admin):
        with st.container(border=True):
          st.write(f"**Pedido ID:** #{pedido['id_pedido']} | **Cliente:** {pedido['usuario']}")
          st.write(f"**Dirección de Envío:** {pedido['direccion']}")
          st.write(f"**Total:** ${pedido['total']} MXN")
          
          st.write("**Productos:**")
          for item in pedido["productos"]:
            st.write(f"- {item.get('nombre')} (Talla: {item.get('talla')}) - ${item.get('precio')} MXN")

          estatus_actual = pedido.get("estatus", "En proceso")
          opciones_estatus = ["En proceso", "En camino", "Entregado", "Cancelado"]
          
          nuevo_estatus = st.selectbox(
              "Actualizar Estatus de Entrega",
              opciones_estatus,
              index=opciones_estatus.index(estatus_actual) if estatus_actual in opciones_estatus else 0,
              key=f"estatus_admin_{pedido['id_pedido']}"
          )

          if nuevo_estatus != estatus_actual:
            pedido["estatus"] = nuevo_estatus
            st.success(f"¡Estatus del pedido #{pedido['id_pedido']} actualizado a '{nuevo_estatus}'!")
            st.rerun()

elif opcion == "Gestión de Vendedores":
  st.header("💼 Panel de Gestión de Vendedores")

  sub_tab_prov, sub_tab_cli, sub_tab_prod, sub_tab_reg = st.tabs([
      "📦 Proveedores",
      "👥 Clientes",
      "👕 Productos",
      "📊 Registro de Ventas",
  ])

  with sub_tab_prov:
    st.subheader("Gestión de Proveedores")
    accion_prov = st.radio(
        "Acción de Proveedores",
        ["Ver / Editar / Eliminar", "Agregar Proveedor"],
        horizontal=True,
    )
    proveedores = db.get("proveedores", [])

    if accion_prov == "Agregar Proveedor":
      with st.form("form_agregar_prov"):
        n_nombre = st.text_input("Nombre del Proveedor")
        n_contacto = st.text_input("Contacto / Teléfono / Correo")
        n_garantia = st.text_input("Condiciones de Garantía")
        if st.form_submit_button("Guardar Proveedor"):
          if n_nombre:
            nuevo_p = {
                "id": len(proveedores) + 1,
                "nombre": n_nombre,
                "contacto": n_contacto,
                "garantia": n_garantia,
            }
            db.setdefault("proveedores", []).append(nuevo_p)
            guardar_datos(db)
            st.success("¡Proveedor agregado con éxito!")
            st.rerun()
          else:
            st.error("El nombre del proveedor es obligatorio.")
    else:
      if not proveedores:
        st.info("No hay proveedores registrados.")
      else:
        for idx, prov in enumerate(proveedores):
          with st.expander(f"Proveedor: {prov.get('nombre')}"):
            with st.form(f"form_edit_prov_{idx}"):
              e_nombre = st.text_input("Nombre", value=prov.get("nombre", ""), key=f"ep_nom_{idx}")
              e_contacto = st.text_input("Contacto", value=prov.get("contacto", ""), key=f"ep_con_{idx}")
              e_garantia = st.text_input("Garantía", value=prov.get("garantia", ""), key=f"ep_gar_{idx}")

              col_p1, col_p2 = st.columns(2)
              actualizar = col_p1.form_submit_button("Guardar Cambios")
              eliminar = col_p2.form_submit_button("Eliminar Proveedor")

              if actualizar:
                prov["nombre"] = e_nombre
                prov["contacto"] = e_contacto
                prov["garantia"] = e_garantia
                guardar_datos(db)
                st.success("¡Proveedor actualizado!")
                st.rerun()

              if eliminar:
                proveedores.pop(idx)
                db["proveedores"] = proveedores
                guardar_datos(db)
                st.success("¡Proveedor eliminado!")
                st.rerun()

  with sub_tab_cli:
    st.subheader("Gestión de Clientes")
    clientes = db.get("clientes", [])
    if not clientes:
      st.info("No hay clientes registrados.")
    else:
      for idx, cli in enumerate(clientes):
        with st.expander(f"Cliente: {cli.get('nombre')} ({cli.get('correo')})"):
          with st.form(f"form_edit_cli_{idx}"):
            c_nombre = st.text_input("Nombre", value=cli.get("nombre", ""), key=f"ec_nom_{idx}")
            c_correo = st.text_input("Correo", value=cli.get("correo", ""), key=f"ec_corr_{idx}")
            c_tel = st.text_input("Teléfono", value=cli.get("telefono", ""), key=f"ec_tel_{idx}")

            col_c1, col_c2 = st.columns(2)
            act_cli = col_c1.form_submit_button("Actualizar Cliente")
            del_cli = col_c2.form_submit_button("Eliminar Cliente")

            if act_cli:
              cli["nombre"] = c_nombre
              cli["correo"] = c_correo
              cli["telefono"] = c_tel
              guardar_datos(db)
              st.success("¡Cliente actualizado!")
              st.rerun()

            if del_cli:
              clientes.pop(idx)
              db["clientes"] = clientes
              guardar_datos(db)
              st.success("¡Cliente eliminado!")
              st.rerun()

  with sub_tab_prod:
    st.subheader("Gestión de Productos y Tallas")
    accion_prod = st.radio(
        "Acción de Productos",
        ["Agregar Nuevo Producto", "Editar / Modificar / Eliminar Productos"],
        horizontal=True,
    )

    if accion_prod == "Agregar Nuevo Producto":
      with st.form("form_nuevo_prod_vendedor"):
        n_nombre = st.text_input("Nombre de la Playera")
        n_precio = st.number_input("Precio (MXN)", min_value=1.0, value=250.0)
        n_stock = st.number_input("Stock disponible", min_value=0, value=10)
        n_estilo = st.selectbox("Estilo", ["Formal", "Informal"])
        n_genero = st.selectbox("Género", ["Hombre", "Mujer"])
        
        # Subida de imagen integrada con st.file_uploader
        n_imagen_archivo = st.file_uploader("Subir imagen del producto", type=["png", "jpg", "jpeg"], key="new_prod_img")

        if st.form_submit_button("Crear Producto"):
          if n_nombre and n_imagen_archivo is not None:
            os.makedirs("img", exist_ok=True)
            ruta_imagen = os.path.join("img", n_imagen_archivo.name)
            with open(ruta_imagen, "wb") as f:
              f.write(n_imagen_archivo.getbuffer())

            nuevo_id = max([p.get("id", 0) for p in db.get("productos", [])], default=0) + 1
            prod_data = {
                "id": nuevo_id,
                "nombre": n_nombre,
                "precio": float(n_precio),
                "stock": int(n_stock),
                "estilo": n_estilo,
                "genero": n_genero,
                "imagen": ruta_imagen,
            }
            db.setdefault("productos", []).append(prod_data)
            guardar_datos(db)
            st.success(f"¡Producto '{n_nombre}' creado con éxito!")
            st.rerun()
          else:
            st.error("El nombre es obligatorio y debes subir una imagen.")
    else:
      productos = db.get("productos", [])
      if not productos:
        st.info("No hay productos registrados.")
      else:
        for idx, prod in enumerate(productos):
          with st.expander(f"Producto: {prod.get('nombre')} (${prod.get('precio')} MXN)"):
            with st.form(f"form_mod_prod_{idx}"):
              p_nombre = st.text_input("Nombre", value=prod.get("nombre", ""), key=f"mp_nom_{idx}")
              p_precio = st.number_input("Precio", value=float(prod.get("precio", 0)), key=f"mp_pre_{idx}")
              p_stock = st.number_input("Stock", value=int(prod.get("stock", 0)), key=f"mp_stk_{idx}")
              p_estilo = st.selectbox("Estilo", ["Formal", "Informal"], index=0 if prod.get("estilo")=="Formal" else 1, key=f"mp_est_{idx}")
              p_genero = st.selectbox("Género", ["Hombre", "Mujer"], index=0 if prod.get("genero")=="Hombre" else 1, key=f"mp_gen_{idx}")
              
              p_imagen_archivo = st.file_uploader("Actualizar imagen (opcional)", type=["png", "jpg", "jpeg"], key=f"mp_img_file_{idx}")

              col_pr1, col_pr2 = st.columns(2)
              guardar_prod = col_pr1.form_submit_button("Guardar Cambios")
              eliminar_prod = col_pr2.form_submit_button("Eliminar Producto")

              if guardar_prod:
                prod["nombre"] = p_nombre
                prod["precio"] = float(p_precio)
                prod["stock"] = int(p_stock)
                prod["estilo"] = p_estilo
                prod["genero"] = p_genero
                
                if p_imagen_archivo is not None:
                  os.makedirs("img", exist_ok=True)
                  ruta_imagen = os.path.join("img", p_imagen_archivo.name)
                  with open(ruta_imagen, "wb") as f:
                    f.write(p_imagen_archivo.getbuffer())
                  prod["imagen"] = ruta_imagen

                guardar_datos(db)
                st.success("¡Producto modificado exitosamente!")
                st.rerun()

              if eliminar_prod:
                productos.pop(idx)
                db["productos"] = productos
                guardar_datos(db)
                st.success("¡Producto eliminado!")
                st.rerun()

  with sub_tab_reg:
    st.subheader("📊 Registro de Productos Vendidos")
    if not st.session_state.pedidos:
      st.info("Aún no se han registrado ventas en el sistema.")
    else:
      for pedido in st.session_state.pedidos:
        with st.container(border=True):
          st.write(f"**Venta ID:** #{pedido['id_pedido']} | **Comprador:** {pedido['usuario']}")
          st.write(f"**Estatus:** `{pedido['estatus']}` | **Dirección:** {pedido['direccion']}")
          st.write("**Productos:**")
          for item in pedido["productos"]:
            st.write(f"- {item.get('nombre')} (Talla: {item.get('talla')}) - ${item.get('precio')} MXN")
          st.write(f"**Total cobrado:** **${pedido['total']} MXN**")