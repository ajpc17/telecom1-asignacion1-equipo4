#!/usr/bin/env python3
"""
Genera los documentos de la Asignación Práctica N° 1 (Telecom I · Equipo 4):

  informe/Integrante2_Especialista_Redes_Equipo4.pdf
  informe/Integrante3_Seguridad_Cloud_Equipo4.pdf
  informe/Integrante4_DevOps_Automatizacion_Equipo4.pdf
  informe/Integrante5_Auditor_IA_Equipo4.pdf
  entrega/Telecom1_Asignacion1_Equipo4.pdf   (informe técnico final)
  entrega/Telecom1_Asignacion1_Equipo4.zip   (informe + script)

Uso:
  1. Completa los nombres en INTEGRANTES (abajo).
  2. Copia las capturas en la carpeta capturas/ con los nombres de CAPTURAS.
  3. Ejecuta:  pip install reportlab   y luego   python3 herramientas/generar_documentos.py
"""
import os
import zipfile
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

# =============================================================================
# DATOS DEL EQUIPO (editar aquí)
# =============================================================================
INTEGRANTES = {
    1: "Arnaldo Perdomo",
    2: "",
    3: "",
    4: "",
    5: "",
}
ROLES = {
    1: ("Arquitecto Cloud Lead", "Diseño del direccionamiento CIDR de la VNet y dimensionamiento de subredes."),
    2: ("Especialista en Redes", "Configuración de subred pública/privada y enrutamiento hacia Internet."),
    3: ("Ingeniero de Seguridad Cloud", "Diseño e implementación de reglas de firewall perimetral en los NSGs."),
    4: ("DevOps & Automatización", "Codificación y depuración del script ejecutable de despliegue y pruebas."),
    5: ("Auditor de Calidad & IA", "Auditoría de respuestas de la IA, validación de seguridad y redacción del informe."),
}
FECHA = "Ciudad Guayana, 20 de noviembre de 2026"

# Capturas esperadas en capturas/ (nombre de archivo -> pie de figura)
CAPTURAS = [
    ("01_grupo_recursos_vnet.png", "Creación del grupo de recursos y de la VNet vnet-telecom1 (10.0.0.0/16)."),
    ("02_subredes_nsg_asociados.png", "Subredes snet-publica y snet-privada con sus NSG asociados."),
    ("03_reglas_nsg_web.png", "Reglas de entrada de nsg-web (P100 HTTP/HTTPS, P110 SSH admin)."),
    ("04_reglas_nsg_db.png", "Reglas de entrada de nsg-db (P100 PostgreSQL desde 10.0.1.0/24, P4000 Deny)."),
    ("05_direcciones_vms.png", "Direcciones de las VMs: vm-web con IP pública y vm-db sin IP pública."),
    ("06_prueba_web_exterior.png", "Prueba A: el servidor web responde desde Internet (HTTP 200 / página de Nginx)."),
    ("07_prueba_bd_desde_web.png", "Prueba B: vm-web se conecta a 10.0.2.4:5432 (nc ... succeeded)."),
    ("08_prueba_bd_desde_internet.png", "Pruebas C y D: vm-db sin IP pública e IP flow verify con resultado Deny."),
    ("09_resumen_pruebas.png", "Resumen final del script: todas las pruebas correctas."),
]

# =============================================================================
# Rutas y estilos
# =============================================================================
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(BASE, "herramientas", "fuentes")
INFORME = os.path.join(BASE, "informe")
ENTREGA = os.path.join(BASE, "entrega")
PARTE1 = os.path.join(BASE, "Parte_Integrante1_Arnaldo")


def _primero(*rutas):
    """Primera ruta que exista (el repo de GitHub y la copia local tienen estructuras distintas)."""
    for r in rutas:
        if os.path.exists(r):
            return r
    return rutas[0]


DIAGRAMA = _primero(os.path.join(BASE, "diagramas", "diagrama_topologia_equipo4_recorte.png"),
                    os.path.join(PARTE1, "diagrama_topologia.png"))
SCRIPT = _primero(os.path.join(BASE, "script", "despliegue_red_azure.sh"),
                  os.path.join(PARTE1, "despliegue_red_azure.sh"))
CAPT_DIR = os.path.join(BASE, "capturas")

pdfmetrics.registerFont(TTFont("DV", os.path.join(FUENTES, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVB", os.path.join(FUENTES, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVM", os.path.join(FUENTES, "DejaVuSansMono.ttf")))
registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")

BLUE = colors.HexColor("#0F6CBD")
DARK = colors.HexColor("#1F2328")
MUTED = colors.HexColor("#57606A")
GREEN = colors.HexColor("#1A7F37")
RED = colors.HexColor("#CF222E")
LINE = colors.HexColor("#D0D7DE")
SOFT = colors.HexColor("#F6F8FA")
NAVY = colors.HexColor("#0B3D6E")
GREEN_BG = colors.HexColor("#E6F4EA")
RED_BG = colors.HexColor("#FDECEA")
BLUE_BG = colors.HexColor("#E8F1FB")
AMBER = colors.HexColor("#B7791F")
AMBER_BG = colors.HexColor("#FFF6E0")

st_kick = ParagraphStyle("kick", fontName="DV", fontSize=9, textColor=BLUE, leading=12)
st_title = ParagraphStyle("title", fontName="DVB", fontSize=18, textColor=DARK, leading=23, spaceAfter=2)
st_sub = ParagraphStyle("sub", fontName="DV", fontSize=10.5, textColor=MUTED, leading=14)
st_h1 = ParagraphStyle("h1", fontName="DVB", fontSize=14, textColor=BLUE, leading=18, spaceBefore=10, spaceAfter=6)
st_h = ParagraphStyle("h", fontName="DVB", fontSize=12.5, textColor=BLUE, leading=16, spaceBefore=10, spaceAfter=5)
st_h2 = ParagraphStyle("h2", fontName="DVB", fontSize=11, textColor=DARK, leading=14, spaceBefore=6, spaceAfter=3)
st_b = ParagraphStyle("b", fontName="DV", fontSize=11, textColor=DARK, leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
st_bul = ParagraphStyle("bul", parent=st_b, leftIndent=14, bulletIndent=2, spaceAfter=3, alignment=0)
st_cap = ParagraphStyle("cap", fontName="DV", fontSize=9, textColor=MUTED, leading=12, alignment=TA_CENTER, spaceAfter=8)
st_cell = ParagraphStyle("cell", fontName="DV", fontSize=9, textColor=DARK, leading=11.5)
st_cellh = ParagraphStyle("cellh", fontName="DVB", fontSize=9, textColor=colors.white, leading=11.5)
st_code = ParagraphStyle("code", fontName="DVM", fontSize=7.6, leading=9.6, textColor=DARK)
st_quote = ParagraphStyle("quote", fontName="DV", fontSize=10, textColor=DARK, leading=13.5, leftIndent=10,
                          borderPadding=(6, 8, 6, 8), backColor=SOFT, spaceAfter=8)

W = letter[0] - 1.6 * inch


def P(t, s=st_b):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(t, st_bul, bulletText="•") for t in items]


def tabla(rows, widths, header=True):
    data = []
    for i, r in enumerate(rows):
        s = st_cellh if (header and i == 0) else st_cell
        data.append([c if not isinstance(c, str) else Paragraph(c, s) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, SOFT]),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), BLUE))
    t.setStyle(TableStyle(style))
    return t


def codigo(texto):
    pre = Preformatted(texto, st_code)
    t = Table([[pre]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT), ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def nombre(n):
    return INTEGRANTES.get(n) or "________________"


def extracto_script(inicio, fin):
    with open(SCRIPT, encoding="utf-8") as f:
        txt = f.read()
    a = txt.index(inicio)
    b = txt.index(fin, a)
    return txt[a:b].rstrip()


def diagrama(ancho=W):
    img = Image(DIAGRAMA)
    r = img.imageHeight / img.imageWidth
    img.drawWidth, img.drawHeight = ancho, ancho * r
    return img


def construir(ruta, historia, pie, titulo):
    def footer(c, d):
        c.saveState()
        c.setFont("DV", 8)
        c.setFillColor(MUTED)
        c.drawString(0.8 * inch, 0.5 * inch, pie)
        c.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, f"Página {d.page}")
        c.restoreState()
    doc = SimpleDocTemplate(ruta, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.8 * inch, title=titulo, author="Equipo 4")
    doc.build(historia, onFirstPage=footer, onLaterPages=footer)


def encabezado(n):
    rol, _ = ROLES[n]
    banda = Table([[P("TELECOMUNICACIONES I · PROF. ING. OSCAR CEDEÑO · UNEG",
                      ParagraphStyle("k2", fontName="DV", fontSize=8.5, textColor=colors.HexColor("#BFD9F2"), leading=11)),
                    P(f"EQUIPO 4 · INTEGRANTE {n}", ParagraphStyle("k3", fontName="DVB", fontSize=8.5,
                                                               textColor=colors.white, leading=11, alignment=2))],
                   [P(f"{rol}", ParagraphStyle("t2", fontName="DVB", fontSize=19, textColor=colors.white, leading=24)), ""],
                   [P("Asignación Práctica N° 1: Cloud Networking y Arquitectura Segura en Azure",
                      ParagraphStyle("s2", fontName="DV", fontSize=10, textColor=colors.white, leading=13)),
                    P(f"Responsable: {nombre(n)}", ParagraphStyle("s3", fontName="DV", fontSize=9.5,
                                                               textColor=colors.white, leading=13, alignment=2))]],
                  colWidths=[W * 0.68, W * 0.32])
    banda.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("SPAN", (0, 1), (1, 1)),
                               ("LINEBELOW", (0, 2), (-1, 2), 4, BLUE),
                               ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                               ("TOPPADDING", (0, 0), (-1, 0), 10), ("BOTTOMPADDING", (0, 2), (-1, 2), 10),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return [banda, Spacer(1, 10)]


# =============================================================================
# Textos técnicos
# =============================================================================
R22_LARGA = [
    "Cuando un usuario en Internet solicita la página de la empresa, el navegador genera la petición HTTP "
    "sobre TLS en la <b>capa de Aplicación</b>. En la <b>capa de Transporte</b> la petición se encapsula en un "
    "segmento TCP con un puerto de origen efímero (por ejemplo, 51000) y puerto de destino 443, después de "
    "establecer la conexión con el <i>three-way handshake</i> (SYN, SYN-ACK, ACK) y negociar la sesión TLS. En la "
    "<b>capa de Internet</b> el segmento se encapsula en un datagrama IP cuyo origen es la IP pública del cliente y "
    "cuyo destino es la IP pública de vm-web (pip-web). En la <b>capa de Acceso a Red</b> el datagrama viaja dentro "
    "de tramas que se reescriben salto a salto a través de los routers del proveedor hasta el borde de Azure.",
    "Al llegar a Azure, la plataforma traduce la IP pública a la IP privada <b>10.0.1.4</b> (NAT 1:1) y "
    "<b>nsg-web</b> evalúa el flujo contra sus reglas: coincide con la regla de prioridad 100 (TCP 443 desde "
    "Internet) y se permite. La VM desencapsula capa por capa y Nginx procesa la solicitud.",
    "Para responder con datos, el servidor web abre una <b>nueva conexión TCP</b> hacia <b>10.0.2.4:5432</b>. "
    "Este es el <b>tráfico Este-Oeste</b>: circula entre servidores dentro de la VNet, a diferencia del tráfico "
    "Norte-Sur que entra o sale de Internet. El paquete se enruta mediante la ruta de sistema "
    "<i>VirtualNetwork</i> (10.0.0.0/16, siguiente salto: red virtual) sin tocar Internet; <b>nsg-db</b> lo admite "
    "por la regla de prioridad 100 porque el origen pertenece a 10.0.1.0/24. Como los NSG son <i>stateful</i>, las "
    "respuestas de la base de datos y del servidor web regresan automáticamente por el mismo flujo hasta el cliente.",
]
R23_LARGA = [
    "Asignar una IP pública a la base de datos la expone a todo Internet. Motores de escaneo masivo como Shodan, "
    "Masscan o ZMap recorren el espacio IPv4 completo en minutos e identifican servicios como PostgreSQL (5432) o "
    "MySQL (3306), que a continuación reciben ataques automatizados de <b>fuerza bruta de credenciales</b> y de "
    "explotación de vulnerabilidades conocidas. Una sola contraseña débil o un parche faltante compromete "
    "directamente el activo más crítico de la organización, los datos, protegido por una única capa de control.",
    "En la subred privada la base de datos solo tiene una dirección del rango RFC 1918 (10.0.2.4), que no es "
    "enrutable en Internet: <b>no existe un camino de red</b> para alcanzarla y no puede ser descubierta por "
    "escaneos. El único acceso posible es desde la subred web, filtrado por nsg-db. Se aplica así "
    "<b>defensa en profundidad</b>: aislamiento de red, firewall perimetral y autenticación del motor. Un atacante "
    "tendría que comprometer primero el servidor web para siquiera intentar llegar a la base de datos.",
]
R24_LARGA = [
    "Un <b>Network Security Group</b> es un filtro de paquetes distribuido que se asocia a una subred o a una "
    "interfaz de red y evalúa cada flujo según la 5-tupla: IP de origen, puerto de origen, IP de destino, puerto de "
    "destino y protocolo. Contiene reglas de entrada y de salida, cada una con acción Allow o Deny.",
    "Cada regla tiene una <b>prioridad numérica entre 100 y 4096</b>. Las reglas se evalúan de menor a mayor número "
    "y el procesamiento se detiene en la <b>primera coincidencia</b>. Por eso el orden es crítico: si en nsg-db se "
    "invirtieran las prioridades (Deny en 100 y Allow en 4000), el Deny coincidiría primero y bloquearía también al "
    "servidor web.",
    "El NSG es un firewall <b>con estado (stateful)</b>: mantiene una tabla de conexiones, de modo que si un flujo de "
    "entrada es permitido, el tráfico de retorno se autoriza automáticamente sin necesidad de una regla de salida.",
    "Azure agrega <b>reglas por defecto</b> que no se pueden eliminar: <b>AllowVnetInBound</b> (65000) permite todo "
    "el tráfico interno de la VNet, <b>AllowAzureLoadBalancerInBound</b> (65001) permite las sondas del balanceador y "
    "<b>DenyAllInBound</b> (65500) deniega todo lo demás. Su impacto es doble: todo lo que no se permite "
    "explícitamente queda bloqueado, pero el tráfico interno quedaría abierto. Por eso nsg-db incluye un "
    "<b>Deny explícito en la prioridad 4000</b>, que se evalúa antes que AllowVnetInBound y limita la base de datos "
    "exclusivamente a la subred web.",
]

R21_CORTA = (
    "Desplegar la topología en Azure reemplaza routers, switches y cableado por Redes Definidas por Software (SDN): "
    "VNet, subredes, rutas y NSG se aprovisionan en minutos mediante API o scripts. En costos, On-Premise exige un "
    "alto <b>CapEx</b> (equipos, cableado, racks, energía, climatización y renovación cada 3–5 años), mientras Azure "
    "lo convierte en <b>OpEx</b> de pago por uso, escalable según la demanda. En <b>tolerancia a fallos</b>, la red "
    "local tiene puntos únicos de falla y su redundancia es costosa; Azure ofrece redundancia de hardware nativa, "
    "Zonas de Disponibilidad, réplica en otra región y SLA garantizados, y al estar definida como código la "
    "infraestructura se reconstruye de forma idéntica y automatizada.")
R22_CORTA = (
    "El navegador genera la petición HTTPS (capa de Aplicación); en Transporte se encapsula en un segmento TCP con "
    "puerto origen efímero y destino 443, tras el <i>three-way handshake</i> y la negociación TLS; en Internet, en un "
    "datagrama IP con origen la IP del cliente y destino la IP pública de vm-web; y en Acceso a Red, en tramas "
    "reescritas salto a salto hasta Azure. Azure traduce la IP pública a 10.0.1.4 (NAT 1:1), <b>nsg-web</b> permite "
    "el flujo por la regla P100 y Nginx procesa la solicitud. Para obtener datos, vm-web abre una nueva conexión TCP "
    "a 10.0.2.4:5432 (<b>tráfico Este-Oeste</b>), enrutada por la ruta de sistema VirtualNetwork sin salir a "
    "Internet; <b>nsg-db</b> la admite por P100 al provenir de 10.0.1.0/24. Al ser NSG <i>stateful</i>, las "
    "respuestas regresan automáticamente por el mismo flujo.")
R23_CORTA = (
    "Una base de datos con IP pública queda expuesta a escáneres masivos (Shodan, Masscan) que recorren todo el "
    "espacio IPv4 en minutos, detectan los puertos 5432/3306 y lanzan fuerza bruta de credenciales y exploits; una "
    "contraseña débil o un parche faltante compromete directamente los datos. En la subred privada la BD solo tiene "
    "una dirección RFC 1918, no enrutable en Internet: no existe camino de red para alcanzarla ni puede ser "
    "descubierta. Solo la subred web llega a ella, filtrada por nsg-db. Es <b>defensa en profundidad</b>: "
    "aislamiento de red, firewall y autenticación; un atacante debería comprometer primero el servidor web.")
R24_CORTA = (
    "Un NSG es un filtro de paquetes distribuido, asociado a una subred o NIC, que evalúa cada flujo por la 5-tupla "
    "(IP y puerto de origen y destino, y protocolo). Sus reglas tienen <b>prioridad de 100 a 4096</b>: se evalúan de "
    "menor a mayor número y se detiene en la primera coincidencia, por lo que invertir prioridades rompería la "
    "política. Es <b>stateful</b>: si una conexión entrante se permite, su retorno se autoriza sin regla de salida. "
    "Azure añade reglas por defecto no eliminables: AllowVnetInBound (65000), AllowAzureLoadBalancerInBound (65001) y "
    "<b>DenyAllInBound</b> (65500), que deniega todo lo no permitido. Como AllowVnetInBound abriría la BD a toda la "
    "VNet, nsg-db incluye un Deny explícito en P4000 que se evalúa antes y la limita a la subred web.")

PROMPTS = [
    ("Esto lo tenemos para mañana Dame una serie de pasos para terminarlo que debe hacer cada quien segun loque "
     "le toca que debemos entregar et", "Se adjuntó el PDF de la asignación."),
    ("Explicame todo de pies a cabeza en consiste la actividad que debo entender to para entregar y tenerlo list", ""),
    ("Bueno si es asi empecemos con el primero entonces elejo ese", "Inicio del trabajo del Integrante 1."),
    ("Diseñame esto en figma para que se vea mejor", "Diagrama de la topología."),
    ("esta bien pero me pierdo visualmente", "Rediseño del diagrama como flujo numerado."),
    ("Bueno genera uno sin guion y coloca el grupo 4", "Versión final del diagrama."),
    ("Crea en pdf lo que sea necesario para los demas integrantes y crea el zip final agrega",
     "Script, PDFs por integrante e informe final."),
]

ERRORES = [
    ("Omisión de seguridad: NSG por NIC y IP pública por defecto",
     "En la propuesta inicial, la IA indicó crear «2 VMs pequeñas (B1s, Ubuntu)» con <font name='DVM'>az vm "
     "create</font> sin advertir que ese comando, con sus valores por defecto, <b>asigna una IP pública a cada VM y "
     "crea un NSG a nivel de NIC con SSH (22) abierto a cualquier origen</b>. Ejecutado así, vm-db habría quedado con "
     "IP pública y SSH expuesto a Internet: exactamente la falla de diseño de la pregunta 2.3, y además un segundo "
     "NSG paralelo que anula la intención de controlar la seguridad solo desde nsg-web y nsg-db.",
     "Se agregó <font name='DVM'>--public-ip-address \"\"</font> a vm-db y <font name='DVM'>--nsg \"\"</font> a "
     "ambas VMs, de modo que la seguridad la controlan únicamente los NSG asociados a las subredes. La prueba C del "
     "script verifica que vm-db no tenga IP pública."),
    ("Inconsistencia funcional en la prueba de la base de datos",
     "La IA propuso validar la base de datos con <font name='DVM'>nc -zv 10.0.2.x 5432</font> desde vm-web, pero "
     "no incluyó ningún servicio escuchando en el puerto 5432 de vm-db. La prueba habría fallado con «connection "
     "refused» aunque las reglas del NSG fueran correctas. Tampoco consideró que, desde el 31/03/2026, las VNets "
     "nuevas crean subredes privadas por defecto: vm-db, sin IP pública, no tiene salida a Internet para ejecutar "
     "<font name='DVM'>apt install postgresql</font>.",
     "Se levanta un servicio TCP en el puerto 5432 con python3 (incluido en la imagen de Ubuntu) mediante "
     "<font name='DVM'>az vm run-command</font>, sin abrir salida a Internet. La subred privada se marca "
     "explícitamente sin acceso de salida por defecto, y la prueba B usa la IP fija 10.0.2.4."),
]

VALIDACION = [
    ["Requisito", "Dónde se cumple en el script", "Estado"],
    ["3.1 VNet 10.0.0.0/16 en eastus", "Sección 2: az network vnet create", "Cumple"],
    ["3.2 Subred pública 10.0.1.0/24", "Sección 2", "Cumple"],
    ["3.2 Subred privada 10.0.2.0/24 sin IP pública", "Secciones 2 y 4 (--public-ip-address \"\")", "Cumple"],
    ["3.3 nsg-web P100: 80 y 443 desde Internet", "Sección 3: Allow-HTTP-HTTPS-Internet", "Cumple"],
    ["3.3 nsg-web P110: 22 solo administración", "Sección 3: origen ADMIN_IP/32", "Cumple"],
    ["3.3 nsg-db P100: 5432 solo desde 10.0.1.0/24", "Sección 3: Allow-PostgreSQL-From-Web", "Cumple"],
    ["3.3 nsg-db: Deny explícito del resto", "Sección 3: Deny-All-Inbound (P4000)", "Cumple"],
    ["NSG asociados a sus subredes", "Sección 3: az network vnet subnet update", "Cumple"],
    ["Sin NSG por NIC con SSH abierto", "Sección 4: --nsg \"\"", "Cumple"],
    ["3.4 Puerto web responde desde el exterior", "Prueba A (curl, código 200)", "Cumple"],
    ["3.4 BD accesible desde la subred web", "Prueba B (nc) y prueba D (Allow)", "Cumple"],
    ["3.4 BD inaccesible desde Internet", "Prueba C (sin IP pública) y prueba D (Deny)", "Cumple"],
    ["Sintaxis del script", "bash -n y ShellCheck sin advertencias; simulación completa", "Cumple"],
    ["Ejecución real en Azure", "Integrante 4, con capturas", "Pendiente"],
]


def tabla_validacion():
    rows = []
    for i, r in enumerate(VALIDACION):
        if i == 0:
            rows.append(r)
        else:
            col = GREEN if r[2] == "Cumple" else colors.HexColor("#9A6700")
            rows.append([r[0], r[1], Paragraph(f"<font color='{col.hexval()}'><b>{r[2]}</b></font>", st_cell)])
    return tabla(rows, [2.6 * inch, 3.3 * inch, W - 5.9 * inch])


def tabla_reglas(nsg):
    if nsg == "web":
        rows = [["Prio.", "Nombre", "Acción", "Protocolo / puertos", "Origen", "Justificación"],
                ["100", "Allow-HTTP-HTTPS-Internet", "Allow", "TCP 80, 443", "Internet", "Servicio web público"],
                ["110", "Allow-SSH-Admin", "Allow", "TCP 22", "IP admin /32", "Administración restringida"],
                ["65000", "AllowVnetInBound", "Allow", "Todos", "VirtualNetwork", "Por defecto de Azure"],
                ["65500", "DenyAllInBound", "Deny", "Todos", "Cualquiera", "Por defecto de Azure"]]
    else:
        rows = [["Prio.", "Nombre", "Acción", "Protocolo / puertos", "Origen", "Justificación"],
                ["100", "Allow-PostgreSQL-From-Web", "Allow", "TCP 5432", "10.0.1.0/24", "Solo la capa web consulta la BD"],
                ["4000", "Deny-All-Inbound", "Deny", "Todos", "Cualquiera", "Cierra AllowVnetInBound (65000)"],
                ["65000", "AllowVnetInBound", "Allow", "Todos", "VirtualNetwork", "Nunca se alcanza por la P4000"],
                ["65500", "DenyAllInBound", "Deny", "Todos", "Cualquiera", "Por defecto de Azure"]]
    return tabla(rows, [0.62 * inch, 1.8 * inch, 0.68 * inch, 1.05 * inch, 1.05 * inch, W - 5.2 * inch])


def tabla_direcciones():
    t = tabla([["Red", "Nombre", "CIDR", "Total IP", "IP útiles", "Uso"],
               ["VNet", "vnet-telecom1", "10.0.0.0/16", "65 536", "—", "Espacio privado (RFC 1918)"],
               ["Subred pública", "snet-publica", "10.0.1.0/24", "256", "251", "vm-web 10.0.1.4 + IP pública"],
               ["Subred privada", "snet-privada", "10.0.2.0/24", "256", "251", "vm-db 10.0.2.4, sin IP pública"]],
              [1.0 * inch, 1.1 * inch, 1.0 * inch, 0.7 * inch, 0.7 * inch, W - 4.5 * inch])
    t.setStyle(TableStyle([("BACKGROUND", (0, 1), (-1, 1), BLUE_BG), ("BACKGROUND", (0, 2), (-1, 2), GREEN_BG),
                           ("BACKGROUND", (0, 3), (-1, 3), RED_BG),
                           ("LINEBEFORE", (0, 1), (0, 1), 3, BLUE), ("LINEBEFORE", (0, 2), (0, 2), 3, GREEN),
                           ("LINEBEFORE", (0, 3), (0, 3), 3, RED)]))
    return t


def recuadro(titulo, texto, color=BLUE, fondo=BLUE_BG):
    t = Table([[P(f"<b>{titulo}</b><br/>{texto}", ParagraphStyle("rc", fontName="DV", fontSize=9.5, leading=12.5,
                                                                textColor=DARK))]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), fondo), ("LINEBEFORE", (0, 0), (0, 0), 4, color),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 7),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def tabla_pruebas():
    return tabla([["Prueba", "Qué valida", "Comando", "Resultado esperado"],
                  ["A", "El puerto web responde desde el exterior", "curl http://IP-pública", "HTTP 200"],
                  ["B", "La BD es accesible desde la subred web", "nc -zv 10.0.2.4 5432 (desde vm-web)", "succeeded"],
                  ["C", "La BD no es alcanzable desde Internet", "az vm list-ip-addresses", "vm-db sin IP pública"],
                  ["D1", "Internet → vm-db:5432", "az network watcher test-ip-flow", "Deny (Deny-All-Inbound)"],
                  ["D2", "vm-web → vm-db:5432", "test-ip-flow", "Allow (P100)"],
                  ["D3", "vm-web → vm-db:22", "test-ip-flow", "Deny (P4000)"],
                  ["D4", "Internet → vm-web:443", "test-ip-flow", "Allow (P100)"],
                  ["D5", "Internet (no admin) → vm-web:22", "test-ip-flow", "Deny (DenyAllInBound)"]],
                 [0.7 * inch, 2.0 * inch, 2.3 * inch, W - 5.0 * inch])


def tabla_matriz():
    rows = [["Rol", "Integrante", "Responsabilidad específica en la topología"]]
    for n in range(1, 6):
        rows.append([f"Integrante {n} · {ROLES[n][0]}", nombre(n), ROLES[n][1]])
    return tabla(rows, [2.05 * inch, 1.6 * inch, W - 3.65 * inch])


def tabla_prompts():
    rows = [["#", "Prompt textual", "Contexto"]]
    for i, (p, c) in enumerate(PROMPTS, 1):
        rows.append([str(i), f"«{p}»", c])
    return tabla(rows, [0.3 * inch, 4.4 * inch, W - 4.7 * inch])


def bloque_error(i, titulo, err, corr):
    return KeepTogether([
        P(f"Error {i}: {titulo}", st_h2),
        tabla([[P("<b>Error de la IA</b>", st_cell), P(err, st_cell)],
               [P("<b>Corrección del equipo</b>", st_cell), P(corr, st_cell)]],
              [1.3 * inch, W - 1.3 * inch], header=False),
        Spacer(1, 6)])


# =============================================================================
# PDFs por integrante
# =============================================================================
R21_LARGA = [
    "Montar esta red en Azure es muy distinto a hacerlo con equipos propios. En vez de comprar routers, switches y cables, todo (la VNet, las subredes, las rutas y los NSG) son recursos virtuales que se crean en minutos con un comando o un script. A eso se le llama Redes Definidas por Software (SDN). En una red local, lo mismo tomaría semanas entre comprar, instalar y cablear.",
    "En costos, la diferencia es <b>CapEx</b> contra <b>OpEx</b>. Un esquema On-Premise exige una inversión grande desde el principio (CapEx) en routers, switches, firewalls, cableado, racks, electricidad y aire acondicionado, y esos equipos hay que renovarlos cada 3 a 5 años. En Azure se paga solo por lo que se usa (OpEx): si hace falta más, se agrega, y si ya no se necesita, se elimina y se deja de pagar.",
    "En <b>tolerancia a fallos</b>, una red local depende de equipos físicos y cualquiera de ellos puede ser un punto único de falla; tener redundancia sale muy caro. Azure ya incluye redundancia de hardware, Zonas de Disponibilidad y la opción de replicar la red en otra región, además de SLA garantizados por el proveedor. Y como la red se define con código, si algo se cae se puede volver a levantar idéntica y de forma automática.",
]


def pdf_integrante1():
    h = encabezado(1)
    h.append(P("1. Topología de la red", st_h1))
    h.append(diagrama(W))
    h.append(P("Figura 1. Topología de red en Microsoft Azure: VNet segmentada en subred pública (Frontend) y "
               "privada (Backend), protegidas con NSG.", st_cap))
    h.append(P("2. Diseño del direccionamiento CIDR y dimensionamiento de subredes", st_h1))
    h.append(tabla_direcciones())
    h.append(Spacer(1, 4))
    h.append(KeepTogether([P("Cálculo", st_h2)] + bullets([
        "<b>/16</b>: 32 − 16 = 16 bits de host → 2<super>16</super> = <b>65 536 direcciones</b>.",
        "<b>/24</b>: 32 − 24 = 8 bits de host → 2<super>8</super> = <b>256 direcciones</b>.",
        "Subredes /24 que caben en la /16: 2<super>(24−16)</super> = <b>256 subredes</b>."])))
    h.append(KeepTogether([P("Direcciones reservadas por Azure en cada subred", st_h2),
                           tabla([["Dirección", "Uso"], ["x.x.x.0", "Dirección de red"],
                                  ["x.x.x.1", "Puerta de enlace predeterminada de Azure"],
                                  ["x.x.x.2 y x.x.x.3", "Mapeo del DNS de Azure"], ["x.x.x.255", "Broadcast"]],
                                 [1.6 * inch, W - 1.6 * inch])]))
    h.append(recuadro("Resultado clave",
                      "Cada /24 tiene 256 − 5 = <b>251 IP utilizables</b>, y la primera IP asignable es la <b>.4</b> "
                      "(vm-web = 10.0.1.4 y vm-db = 10.0.2.4).", GREEN, GREEN_BG))
    h.append(P("Justificación del diseño", st_h2))
    h.append(P("Usé el rango 10.0.0.0/16 porque pertenece a las direcciones privadas de la RFC 1918: son direcciones que no se enrutan en Internet, así que nadie desde afuera puede llegar a ellas directamente. Elegí un /16 para tener espacio de sobra, ya que caben hasta 256 subredes /24. Así la empresa puede crecer (por ejemplo, con una subred de gestión, otra para balanceadores o una para Azure Bastion) sin rediseñar toda la red. Cada /24 da 251 IP utilizables, más que suficiente para un par de servidores web o una base de datos. Y como la subred pública (10.0.1.0/24) y la privada (10.0.2.0/24) son bloques separados que no se pisan, cada una puede tener su propio NSG con sus propias reglas de seguridad."))
    h.append(P("3. Pregunta 2.1: On-Premise vs. Cloud Networking", st_h1))
    h += [P(t, ParagraphStyle("b9", parent=st_b, fontSize=10, leading=13.5, spaceAfter=4)) for t in R21_LARGA]
    construir(os.path.join(INFORME, "Integrante1_Arquitecto_Cloud_Equipo4.pdf"), h,
              "Telecom I · Asignación Práctica N° 1 · Equipo 4 · Integrante 1", "Integrante 1 – Arquitecto Cloud Lead")


def pdf_integrante2():
    h = encabezado(2)
    h.append(P("1. Configuración de las subredes", st_h))
    h.append(tabla([["Subred", "CIDR", "Rol", "IP pública", "Salida a Internet", "NSG"],
                    ["snet-publica", "10.0.1.0/24", "Frontend (web)", "Sí: pip-web (Standard)", "Por la IP pública de la VM", "nsg-web"],
                    ["snet-privada", "10.0.2.0/24", "Backend (BD)", "No", "No (subred privada)", "nsg-db"]],
                   [0.95 * inch, 0.9 * inch, 1.0 * inch, 1.35 * inch, 1.55 * inch, W - 5.75 * inch]))
    h.append(Spacer(1, 6))
    h.append(P("Lo que hace pública o privada a una subred en Azure no es un tipo distinto de subred, sino si sus "
               "máquinas tienen IP pública y si su NSG acepta tráfico desde Internet. Además, desde el 31 de marzo "
               "de 2026 Azure crea las subredes de VNets nuevas como <b>privadas por defecto</b> (sin acceso de "
               "salida implícito). El script marca snet-privada explícitamente como privada; vm-web obtiene su "
               "salida a Internet a través de su propia IP pública."))
    h.append(P("2. Enrutamiento", st_h))
    h.append(P("No se requieren tablas de rutas personalizadas (UDR): Azure aplica rutas de sistema a cada subred."))
    h.append(tabla([["Prefijo de destino", "Siguiente salto", "Efecto en la topología"],
                    ["10.0.0.0/16", "Red virtual (VirtualNetwork)", "Tráfico Este-Oeste vm-web → vm-db sin salir a Internet"],
                    ["0.0.0.0/0", "Internet", "Salida de vm-web por su IP pública; vm-db no tiene salida"],
                    ["10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16", "Ninguno (descartar)", "Rangos privados fuera de la VNet no se enrutan"]],
                   [2.0 * inch, 1.6 * inch, W - 3.6 * inch]))
    h.append(KeepTogether([P("3. Comandos (sección 2 del script)", st_h),
                           codigo(extracto_script("az network vnet create", "# ----"))]))
    h.append(P("4. Pregunta 2.2: Modelo TCP/IP y Tráfico Este-Oeste", st_h))
    h += [P(t) for t in R22_LARGA]
    h.append(KeepTogether([P("5. Puntos clave para la defensa", st_h)] + bullets(["Encapsulamiento: datos HTTP → segmento TCP (puertos) → datagrama IP (direcciones) → trama.",
                  "La IP pública 20.x.x.x se traduce a 10.0.1.4 (NAT 1:1) antes de llegar a la VM.",
                  "Este-Oeste = entre servidores dentro de la VNet; Norte-Sur = entre Internet y la VNet.",
                  "La ruta de sistema 10.0.0.0/16 hace que web → BD nunca pase por Internet.",
                  "vm-db no tiene IP pública ni salida a Internet: no se puede alcanzar ni puede filtrar datos hacia fuera."])))
    construir(os.path.join(INFORME, "Integrante2_Especialista_Redes_Equipo4.pdf"), h,
              "Telecom I · Asignación Práctica N° 1 · Equipo 4 · Integrante 2", "Integrante 2 – Especialista en Redes")


def pdf_integrante3():
    h = encabezado(3)
    h.append(P("1. Reglas de entrada de nsg-web (asociado a snet-publica)", st_h))
    h.append(tabla_reglas("web"))
    h.append(P("2. Reglas de entrada de nsg-db (asociado a snet-privada)", st_h))
    h.append(tabla_reglas("db"))
    h.append(P("3. Decisiones de seguridad", st_h))
    h += bullets([
        "<b>NSG a nivel de subred:</b> cada NSG se asocia a su subred, así protege a todas las VMs presentes y futuras de esa capa.",
        "<b>Sin NSG por NIC:</b> las VMs se crean con <font name='DVM'>--nsg \"\"</font>, porque <font name='DVM'>az vm create</font> crea por defecto un NSG con SSH abierto a cualquier origen.",
        "<b>SSH restringido:</b> el puerto 22 solo acepta la IP del administrador (/32); nunca 0.0.0.0/0.",
        "<b>Deny explícito en P4000:</b> sin él, AllowVnetInBound (65000) permitiría que cualquier máquina de la VNet llegue a la BD por cualquier puerto.",
        "<b>Origen por subred:</b> la regla de PostgreSQL usa 10.0.1.0/24 y no una IP fija, para que escale si se agregan más servidores web."])
    h.append(KeepTogether([P("4. Comandos (sección 3 del script)", st_h), codigo(extracto_script('az network nsg create --resource-group "$RG" --name "$NSG_WEB"', "# -----------------------------------------------------------------------------\n# 4."))]))
    h.append(P("5. Pregunta 2.3: Segmentación y Defensa en Profundidad", st_h))
    h += [P(t) for t in R23_LARGA]
    h.append(P("6. Pregunta 2.4: Anatomía y Evaluación de Reglas en un NSG", st_h))
    h += [P(t) for t in R24_LARGA]
    h.append(KeepTogether([P("7. Puntos clave para la defensa", st_h)] + bullets(["Menor número = mayor prioridad; la primera regla que coincide gana.",
                  "Stateful: la respuesta de una conexión permitida sale sin regla de salida.",
                  "Si se invierten las prioridades de nsg-db, se bloquea también al servidor web.",
                  "Abrir 5432 a 0.0.0.0/0 es la falla clásica: la BD solo debe aceptar 10.0.1.0/24.",
                  "Un NSG que no está asociado a ninguna subred ni NIC no protege nada."])))
    construir(os.path.join(INFORME, "Integrante3_Seguridad_Cloud_Equipo4.pdf"), h,
              "Telecom I · Asignación Práctica N° 1 · Equipo 4 · Integrante 3", "Integrante 3 – Ingeniero de Seguridad Cloud")


def pdf_integrante4():
    h = encabezado(4)
    h.append(P("1. Cómo ejecutar el script", st_h))
    h += bullets([
        "Entra a <b>portal.azure.com</b> con la cuenta de Azure for Students y abre <b>Cloud Shell</b> (ícono &gt;_ arriba), en modo <b>Bash</b>.",
        "Sube <font name='DVM'>despliegue_red_azure.sh</font> (botón Administrar archivos → Cargar).",
        "Ejecuta <font name='DVM'>chmod +x despliegue_red_azure.sh</font> y luego <font name='DVM'>./despliegue_red_azure.sh</font>. Tarda entre 8 y 15 minutos.",
        "En Cloud Shell la IP detectada para SSH es la de Cloud Shell. Para administrar desde tu PC usa <font name='DVM'>ADMIN_IP=tu.ip.publica ./despliegue_red_azure.sh</font>.",
        "Si Azure responde que no hay capacidad para B1s, ejecuta con <font name='DVM'>VM_SIZE=Standard_B2s</font>."])
    h.append(P("2. Estructura del script", st_h))
    h.append(tabla([["Sección", "Qué hace", "Responsable"],
                    ["0. Parámetros", "Nombres, rangos CIDR, puertos e IP del administrador", "Integrante 1"],
                    ["1. Grupo de recursos", "Crea rg-telecom1-equipo4 en eastus", "Integrante 4"],
                    ["2. VNet y subredes", "VNet 10.0.0.0/16, snet-publica y snet-privada (privada explícita)", "Integrante 2"],
                    ["3. NSG", "nsg-web y nsg-db con sus reglas y la asociación a cada subred", "Integrante 3"],
                    ["4. VMs", "vm-web con IP pública; vm-db sin IP pública; sin NSG por NIC", "Integrante 4"],
                    ["5. Servicios", "Nginx en vm-web; servicio TCP 5432 en vm-db (run-command)", "Integrante 4"],
                    ["6. Pruebas", "Pruebas A, B, C y D con resultado [OK] o [FALLO]", "Integrante 4"],
                    ["7. Evidencias", "Tablas de subredes, reglas y direcciones para las capturas", "Integrante 4"],
                    ["8. Resumen", "Conteo de pruebas y limpieza opcional (LIMPIAR=1)", "Integrante 4"]],
                   [1.5 * inch, W - 2.6 * inch, 1.1 * inch]))
    h.append(P("3. Pruebas y resultados esperados", st_h))
    h.append(tabla_pruebas())
    h.append(P("4. Capturas que debes tomar", st_h))
    h.append(P("Guárdalas en la carpeta <b>capturas/</b> con estos nombres exactos para que el informe final las "
               "inserte solo al volver a generarlo:"))
    h.append(tabla([["Archivo", "Qué debe mostrar"]] + [[f"<font name='DVM'>{a}</font>", b] for a, b in CAPTURAS],
                   [2.6 * inch, W - 2.6 * inch]))
    h.append(P("5. Problemas comunes", st_h))
    h += bullets(["<b>Prueba A falla:</b> espera 1 o 2 minutos a que Nginx termine de instalarse y vuelve a probar en el navegador con http://IP-pública.",
                  "<b>Network Watcher no disponible:</b> las pruebas D salen como [AVISO]; las pruebas A, B y C siguen siendo válidas.",
                  "<b>Errores al repetir el script:</b> borra primero el grupo con <font name='DVM'>az group delete -n rg-telecom1-equipo4 --yes</font>.",
                  "<b>Al terminar las capturas:</b> borra el grupo de recursos para no gastar el crédito de estudiante."])
    h.append(KeepTogether([P("6. Puntos clave para la defensa", st_h)] + bullets(["<font name='DVM'>run-command</font> usa el agente de Azure, no la red; por eso funciona aunque nsg-db bloquee SSH.",
                  "IP flow verify no envía tráfico: simula un paquete contra las reglas efectivas y dice qué regla coincide.",
                  "El script termina con código 0 solo si todas las pruebas pasan."])))
    construir(os.path.join(INFORME, "Integrante4_DevOps_Automatizacion_Equipo4.pdf"), h,
              "Telecom I · Asignación Práctica N° 1 · Equipo 4 · Integrante 4", "Integrante 4 – DevOps & Automatización")


def pdf_integrante5():
    h = encabezado(5)
    h.append(P("1. Herramientas de IA y modelos utilizados", st_h))
    h.append(tabla([["Herramienta", "Modelo / versión", "Uso en la asignación"],
                    ["Claude (claude.ai)", "Claude Opus 5.5", "Plan de trabajo, explicación de la topología, diagrama (Figma), "
                     "textos de la Parte I, script de despliegue y documentos del equipo"]],
                   [1.4 * inch, 1.4 * inch, W - 2.8 * inch]))
    h.append(Spacer(1, 4))
    h.append(P("Si algún integrante usó otra herramienta, debe agregarla con sus prompts antes de cerrar el informe.", st_cap))
    h.append(P("2. Registro de prompts textuales", st_h))
    h.append(tabla_prompts())
    h.append(P("3. Refutación de errores de la IA", st_h))
    for i, (t, e, c) in enumerate(ERRORES, 1):
        h.append(bloque_error(i, t, e, c))
    h.append(P("4. Validación de seguridad del script", st_h))
    h.append(tabla_validacion())
    h.append(P("5. Matriz de responsabilidades", st_h))
    h.append(tabla_matriz())
    h.append(P("6. Pasos para cerrar la entrega", st_h))
    h += bullets(["Completar los nombres en <font name='DVM'>herramientas/generar_documentos.py</font> (diccionario INTEGRANTES).",
                  "Copiar las capturas del Integrante 4 en <font name='DVM'>capturas/</font> con los nombres indicados.",
                  "Ejecutar <font name='DVM'>python3 herramientas/generar_documentos.py</font>; se regeneran el PDF final y el ZIP.",
                  "Revisar el PDF y subir <b>entrega/Telecom1_Asignacion1_Equipo4.zip</b> al Aula Virtual antes de las 12:00 PM."])
    construir(os.path.join(INFORME, "Integrante5_Auditor_IA_Equipo4.pdf"), h,
              "Telecom I · Asignación Práctica N° 1 · Equipo 4 · Integrante 5", "Integrante 5 – Auditor de Calidad & IA")


# =============================================================================
# Informe técnico final
# =============================================================================
def portada():
    t = ParagraphStyle("pt", fontName="DVB", fontSize=12, leading=16, alignment=TA_CENTER, textColor=DARK)
    tn = ParagraphStyle("ptn", fontName="DV", fontSize=11, leading=15, alignment=TA_CENTER, textColor=DARK)
    big = ParagraphStyle("pbig", fontName="DVB", fontSize=22, leading=28, alignment=TA_CENTER, textColor=BLUE)
    sub = ParagraphStyle("psub", fontName="DV", fontSize=13, leading=18, alignment=TA_CENTER, textColor=MUTED)
    h = [P("República Bolivariana de Venezuela", tn),
         P("Universidad Nacional Experimental de Guayana", t),
         P("Vicerrectorado Académico · Ingeniería en Informática", tn),
         P("Telecomunicaciones I (Código 2472850)", tn),
         Spacer(1, 1.3 * inch),
         P("ASIGNACIÓN PRÁCTICA N° 1", sub),
         Spacer(1, 6),
         P("Cloud Networking y Arquitectura Segura en Azure", big),
         Spacer(1, 8),
         P("Informe Técnico · Equipo 4", sub),
         Spacer(1, 1.0 * inch)]
    rows = [["Integrante", "Rol"]] + [[nombre(n), f"{n}. {ROLES[n][0]}"] for n in range(1, 6)]
    tb = tabla(rows, [2.6 * inch, 3.0 * inch])
    tb.hAlign = "CENTER"
    h += [tb, Spacer(1, 0.9 * inch), P("Profesor: Ing. Oscar Cedeño", tn), Spacer(1, 4), P(FECHA, tn), PageBreak()]
    return h


def capturas():
    h = []
    for i, (archivo, pie) in enumerate(CAPTURAS, 1):
        ruta = os.path.join(CAPT_DIR, archivo)
        if os.path.exists(ruta):
            img = Image(ruta)
            r = img.imageHeight / img.imageWidth
            ancho = W
            alto = ancho * r
            if alto > 4.2 * inch:
                alto = 4.2 * inch
                ancho = alto / r
            img.drawWidth, img.drawHeight = ancho, alto
            h.append(KeepTogether([img, Spacer(1, 3), P(f"Figura {i + 1}. {pie}", st_cap)]))
        else:
            caja = Table([[P(f"<b>Insertar captura:</b> <font name='DVM'>capturas/{archivo}</font><br/>{pie}",
                             ParagraphStyle("ph", parent=st_cell, alignment=TA_CENTER, textColor=MUTED))]],
                         colWidths=[W], rowHeights=[0.62 * inch])
            caja.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E3B341")),
                                      ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFAEB")),
                                      ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            h += [caja, Spacer(1, 8)]
    return h


def informe_final():
    h = portada()
    # Parte I (máximo 1 página)
    h.append(P("1. Parte I: Fundamentación Técnica Aplicada", st_h1))
    for titulo, texto in [("2.1. On-Premise vs. Cloud Networking", R21_CORTA),
                          ("2.2. Modelo TCP/IP y Tráfico Este-Oeste", R22_CORTA),
                          ("2.3. Segmentación y Defensa en Profundidad", R23_CORTA),
                          ("2.4. Anatomía y Evaluación de Reglas en un NSG", R24_CORTA)]:
        h += [P(titulo, st_h2), P(texto)]
    h.append(PageBreak())
    # Parte II
    h.append(P("2. Parte II: Implementación Práctica y Automatización", st_h1))
    h.append(P("2.1. Topología", st_h))
    h += [diagrama(), Spacer(1, 3), P("Figura 1. Topología de red en Microsoft Azure (Equipo 4).", st_cap)]
    h.append(P("2.2. Direccionamiento y segmentación", st_h))
    h.append(tabla_direcciones())
    h.append(Spacer(1, 4))
    h.append(P("Cada subred /24 tiene 256 direcciones, de las que Azure reserva 5 (.0 red, .1 puerta de enlace, "
               ".2 y .3 DNS de Azure, .255 broadcast), por lo que quedan 251 utilizables. El /16 admite hasta 256 "
               "subredes /24, lo que deja margen de crecimiento. La subred privada se configura sin salida a "
               "Internet por defecto."))
    h.append(KeepTogether([P("2.3. Network Security Groups", st_h), P("nsg-web (asociado a snet-publica)", st_h2),
                           tabla_reglas("web")]))
    h.append(KeepTogether([P("nsg-db (asociado a snet-privada)", st_h2), tabla_reglas("db")]))
    h.append(P("2.4. Script de automatización", st_h))
    h.append(P("El archivo <b>despliegue_red_azure.sh</b> (Bash + Azure CLI) se entrega junto a este informe. "
               "Crea el grupo de recursos, la VNet y las subredes, los NSG con sus reglas y su asociación, las VMs "
               "(vm-web con IP pública; vm-db sin IP pública y sin NSG por NIC), los servicios de prueba, y ejecuta "
               "las validaciones. Su sintaxis se verificó con <i>bash -n</i> y ShellCheck, sin advertencias."))
    h.append(P("2.5. Pruebas de conectividad y validación", st_h))
    h.append(tabla_pruebas())
    h.append(P("2.6. Capturas de ejecución", st_h))
    h += capturas()
    h.append(PageBreak())
    # Parte III
    h.append(P("3. Parte III: Auditoría de IA y Transparencia Tecnológica", st_h1))
    h.append(P("3.1. Herramienta y modelo", st_h))
    h.append(tabla([["Herramienta", "Modelo / versión", "Uso"],
                    ["Claude (claude.ai)", "Claude Opus 5.5", "Plan de trabajo, explicación técnica, diagrama, textos de "
                     "la Parte I, script de despliegue y documentos del equipo"]],
                   [1.4 * inch, 1.4 * inch, W - 2.8 * inch]))
    h.append(P("3.2. Registro de prompts textuales", st_h))
    h.append(tabla_prompts())
    h.append(P("3.3. Refutación de errores de la IA", st_h))
    for i, (t, e, c) in enumerate(ERRORES, 1):
        h.append(bloque_error(i, t, e, c))
    h.append(P("3.4. Validación de seguridad del script", st_h))
    h.append(tabla_validacion())
    h.append(KeepTogether([P("3.5. Matriz de responsabilidades", st_h), tabla_matriz()]))
    salida = os.path.join(ENTREGA, "Telecom1_Asignacion1_Equipo4.pdf")
    construir(salida, h, "Telecom I · Asignación Práctica N° 1 · Equipo 4 · Informe Técnico",
              "Telecom1_Asignacion1_Equipo4")
    return salida


def crear_zip(pdf):
    ruta = os.path.join(ENTREGA, "Telecom1_Asignacion1_Equipo4.zip")
    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(pdf, "Telecom1_Asignacion1_Equipo4.pdf")
        z.write(DIAGRAMA, "diagrama_topologia.png")
        info = zipfile.ZipInfo.from_file(SCRIPT, "despliegue_red_azure.sh")
        info.external_attr = 0o100755 << 16
        with open(SCRIPT, "rb") as f:
            z.writestr(info, f.read(), zipfile.ZIP_DEFLATED)
    return ruta


if __name__ == "__main__":
    os.makedirs(INFORME, exist_ok=True)
    os.makedirs(ENTREGA, exist_ok=True)
    pdf_integrante1()
    pdf_integrante2()
    pdf_integrante3()
    pdf_integrante4()
    pdf_integrante5()
    final = informe_final()
    z = crear_zip(final)
    faltan = [a for a, _ in CAPTURAS if not os.path.exists(os.path.join(CAPT_DIR, a))]
    print("Generado:", os.path.relpath(final, BASE))
    print("Generado:", os.path.relpath(z, BASE))
    if faltan:
        print(f"Aviso: faltan {len(faltan)} capturas en capturas/ (el informe muestra recuadros para insertarlas).")
    if not all(INTEGRANTES.values()):
        print("Aviso: faltan nombres de integrantes en INTEGRANTES.")
