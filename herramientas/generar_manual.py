# -*- coding: utf-8 -*-
"""Genera el manual de próximos pasos del Equipo 4 (PDF)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar_documentos import *  # estilos, tabla(), recuadro(), construir(), bullets(), W...

M = lambda t: f"<font name='DVM' size='9'>{t}</font>"
st_n = ParagraphStyle("n", parent=st_b, fontSize=10.5, leading=14.5, alignment=0)


def paso_cab(n, titulo, quien):
    cab = Table([[P(f"<b>{n}</b>", ParagraphStyle("pn", fontName="DVB", fontSize=15, textColor=colors.white, alignment=1, leading=18)),
                  P(f"<b>{titulo}</b><br/><font size=8.5 color='#57606A'>{quien}</font>",
                    ParagraphStyle("pt", fontName="DV", fontSize=11.5, leading=14, textColor=DARK))]],
                colWidths=[0.45 * inch, W - 0.45 * inch])
    cab.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), BLUE), ("BACKGROUND", (1, 0), (1, 0), BLUE_BG),
                             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (1, 0), (1, 0), 10)]))
    return cab


def paso(n, titulo, quien, cuerpo):
    return [KeepTogether([paso_cab(n, titulo, quien), Spacer(1, 4), cuerpo[0]])] + cuerpo[1:] + [Spacer(1, 8)]


def num(items):
    return [Paragraph(t, st_bul, bulletText=f"{i}.") for i, t in enumerate(items, 1)]


h = []
banda = Table([[P("TELECOMUNICACIONES I · PROF. ING. OSCAR CEDEÑO · UNEG", ParagraphStyle("a", fontName="DV", fontSize=8.5, textColor=colors.HexColor("#BFD9F2"), leading=11))],
               [P("Pasos que faltan", ParagraphStyle("b", fontName="DVB", fontSize=21, textColor=colors.white, leading=26))],
               [P("Equipo 4 · Después del entregable del Integrante 1 · Entrega: viernes 20/11/2026, 12:00 PM",
                  ParagraphStyle("c", fontName="DV", fontSize=10, textColor=colors.white, leading=13))]], colWidths=[W])
banda.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("LINEBELOW", (0, 2), (-1, 2), 4, BLUE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, 0), 10),
                           ("BOTTOMPADDING", (0, 2), (-1, 2), 10)]))
h += [banda, Spacer(1, 10)]

# ---------------------------------------------------------------- 3
h.append(P("Pasos que faltan, en detalle", st_h1))

h += paso("1", "Completar la auditoría de IA (Parte III, vale 20 %)", "Todos · esta noche, en paralelo al paso 2", [
    P("Es la parte que más se olvida y es mucha nota. El informe ya trae dos errores reales de la IA refutados y "
      "una tabla de prompts, pero el profesor pide <b>los prompts textuales de todo el equipo</b>, así que cada quien "
      "debe aportar los suyos.", st_n),
    *bullets(["Cada integrante copia, <b>tal como los escribió</b>, los 3 a 5 prompts que usó con cualquier IA para su parte (sin corregirlos ni resumirlos).",
              "Anota la <b>herramienta y el modelo exacto</b> de cada sesión (por ejemplo, el nombre que aparece en el selector de modelos de Claude, ChatGPT o Gemini). "
              "El informe indica un modelo en la sección 3.1: confirma que coincide con el que se usó realmente y corrígelo si no.",
              "Si alguien detectó otro error de la IA (una respuesta incorrecta que él mismo tuvo que corregir), lo escribe con tres datos: "
              "<i>qué dijo la IA</i>, <i>por qué estaba mal</i> y <i>cómo se corrigió</i>. Con uno basta, pero más suma.",
              "Todo se le manda al Integrante 5, que lo agrega al generador (listas PROMPTS y ERRORES de <i>generar_documentos.py</i>) en el paso 6.",
              "Revisar también la matriz de roles: cada nombre debe estar junto a su rol y su aporte real."]),
])

h += paso("2", "Subir al repo la carpeta del generador del informe", "Arnaldo · esta noche", [
    P("En GitHub ya está tu parte (carpeta <i>Parte_Integrante1_Arnaldo</i>) y el README, pero <b>falta el programa que "
      "arma el informe final y el ZIP</b>. Sin él, el Integrante 5 no puede generar la entrega.", st_n),
    *num(["Descomprime <i>herramientas_para_repo.zip</i> en tu computador: sale una carpeta <i>herramientas</i>.",
          "Entra al repo en GitHub, pulsa <b>Add file → Upload files</b> y arrastra la carpeta <i>herramientas</i> completa (con la subcarpeta <i>fuentes</i>).",
          "Escribe un mensaje como «Agrega generador del informe» y pulsa <b>Commit changes</b>.",
          "Comprueba que en la raíz del repo ahora hay tres cosas: <i>Parte_Integrante1_Arnaldo</i>, <i>herramientas</i> y <i>README.md</i>."]),
])

h += paso("3", "Preparar la cuenta de Azure", "Integrante 4 · antes de correr nada", [
    P("Hace falta una suscripción de Azure con crédito disponible (por ejemplo, <b>Azure for Students</b>). El script "
      "crea dos máquinas pequeñas (Standard_B1s) y una IP pública estática, y todo se borra al final, así que el "
      "gasto es mínimo siempre que no se deje encendido.", st_n),
    *bullets(["Entrar a <b>portal.azure.com</b> con la cuenta de la suscripción.",
              "Comprobar en <b>Suscripciones</b> que el estado sea <i>Activa</i> y que quede crédito.",
              "La primera vez que se abre Cloud Shell, Azure pide elegir <b>Bash</b> y crear un almacenamiento "
              "(o usar la opción <i>Sin cuenta de almacenamiento</i>). Cualquiera de las dos sirve."]),
])

h += paso("4", "Traer el script del repo y correrlo en Cloud Shell", "Integrante 4 · esta noche", [
    P("El repo es público, así que Cloud Shell puede descargarlo directamente: no hace falta subir archivos a mano. "
      "Cloud Shell ya trae Azure CLI y la sesión iniciada (no se necesita <i>az login</i>).", st_n),
    *num(["Abrir Cloud Shell con el ícono " + M("&gt;_") + " de la barra superior del portal y elegir <b>Bash</b>.",
          "Descargar el repo y entrar a la carpeta del script:<br/>" +
          M("git clone https://github.com/ajpc17/telecom1-asignacion1-equipo4") + "<br/>" +
          M("cd telecom1-asignacion1-equipo4/Parte_Integrante1_Arnaldo"),
          "Dar permiso de ejecución: " + M("chmod +x despliegue_red_azure.sh"),
          "Ejecutarlo guardando una copia de la salida (sirve para las capturas y para revisar errores):<br/>" +
          M("./despliegue_red_azure.sh 2&gt;&amp;1 | tee salida_script.txt"),
          "Esperar entre 10 y 15 minutos aproximadamente. No cerrar la pestaña mientras corre.",
          "Al final debe aparecer: <b>Resumen: 8 pruebas correctas, 0 con fallo</b>."]),
    Spacer(1, 4),
    recuadro("Qué hace el script mientras espera",
             "Crea el grupo de recursos, la VNet y las dos subredes; crea los dos NSG con sus reglas y los asocia a las "
             "subredes; crea vm-web y vm-db; instala Nginx en vm-web y deja un servicio de prueba en el puerto 5432 de "
             "vm-db; y ejecuta las pruebas A, B, C y D. Los mensajes <b>[OK]</b> en verde son pruebas superadas.",
             BLUE, BLUE_BG),
])

h += paso("5", "Tomar las 9 capturas", "Integrante 4 · apenas termine el script", [
    P("Guárdalas con estos nombres exactos (el generador del informe las busca por nombre) dentro de la carpeta "
      "<i>capturas/</i> del repo. <b>No borres los recursos de Azure hasta tener las nueve.</b> Conviene que se vea "
      "en cada captura la ventana completa con el texto legible.", st_n),
    tabla([["Archivo", "Qué debe verse y de dónde sale"],
           ["01_grupo_recursos_vnet.png", "Terminal al inicio del script: grupo rg-telecom1-equipo4 y VNet vnet-telecom1 (10.0.0.0/16) creados"],
           ["02_subredes_nsg_asociados.png", "Tabla «Subredes y NSG asociados» de la sección 7 del script"],
           ["03_reglas_nsg_web.png", "Tabla «Reglas de nsg-web»: P100 y P110"],
           ["04_reglas_nsg_db.png", "Tabla «Reglas de nsg-db»: P100 Allow y P4000 Deny"],
           ["05_direcciones_vms.png", "Tabla «Direcciones de las VMs»: vm-web con IP pública, vm-db vacía"],
           ["06_prueba_web_exterior.png", "Línea [OK] de la prueba A (HTTP 200 desde Internet)"],
           ["07_prueba_bd_desde_web.png", "Línea [OK] de la prueba B (vm-web llega a 10.0.2.4:5432)"],
           ["08_prueba_bd_desde_internet.png", "Líneas [OK] de las pruebas C y D (sin IP pública y resultados Deny/Allow)"],
           ["09_resumen_pruebas.png", "Línea final con las 8 pruebas correctas"]],
          [2.4 * inch, W - 2.4 * inch]),
    Spacer(1, 6),
    P("<b>Si la salida ya se salió de la pantalla</b>, no hace falta repetir el script. Las capturas 02 a 05 se "
      "pueden volver a generar con estos comandos (copiar y pegar en Cloud Shell):", st_n),
    codigo("RG=rg-telecom1-equipo4\n"
           "az network vnet subnet list -g $RG --vnet-name vnet-telecom1 \\\n"
           "  --query '[].{Subred:name,CIDR:addressPrefix,NSG:networkSecurityGroup.id}' -o table\n"
           "az network nsg rule list -g $RG --nsg-name nsg-web \\\n"
           "  --query '[].{Prioridad:priority,Nombre:name,Accion:access,Origen:sourceAddressPrefix}' -o table\n"
           "az network nsg rule list -g $RG --nsg-name nsg-db \\\n"
           "  --query '[].{Prioridad:priority,Nombre:name,Accion:access,Origen:sourceAddressPrefix}' -o table\n"
           "az vm list-ip-addresses -g $RG \\\n"
           "  --query '[].{VM:virtualMachine.name,\n"
           "  IPPrivada:virtualMachine.network.privateIpAddresses[0],\n"
           "  IPPublica:virtualMachine.network.publicIpAddresses[0].ipAddress}' -o table"),
    Spacer(1, 4),
    P("Alternativa más vistosa para 03 y 04: en el portal, entrar a <b>Grupos de seguridad de red → nsg-web (o nsg-db) → "
      "Reglas de seguridad de entrada</b> y capturar esa pantalla. Cualquiera de las dos formas es válida.", st_n),
])

h += paso("6", "Borrar los recursos", "Integrante 4 · cuando tenga las 9 capturas", [
    P("Para no gastar crédito, ejecutar en Cloud Shell:", st_n),
    codigo("az group delete --name rg-telecom1-equipo4 --yes --no-wait"),
    Spacer(1, 4),
    P("La eliminación tarda unos minutos en segundo plano. Se puede comprobar en el portal que el grupo ya no aparece.", st_n),
])

h += paso("7", "Subir las capturas al repo y generar el informe final", "Integrante 5 · viernes temprano", [
    P("Todo lo necesario ya está en GitHub, así que se trabaja desde una copia del repo.", st_n),
    *num(["Integrante 4 sube las 9 capturas al repo: <b>Add file → Upload files</b>, dentro de una carpeta llamada <i>capturas</i>, "
          "con los nombres exactos del paso 5. (Se puede pegar <i>capturas/</i> delante del nombre al crear la carpeta desde la web.)",
          "Integrante 5 descarga el repo: " + M("git clone https://github.com/ajpc17/telecom1-asignacion1-equipo4") + " o el botón verde <b>Code → Download ZIP</b>.",
          "Abre <i>herramientas/generar_documentos.py</i> y escribe los cinco nombres en el bloque " + M("INTEGRANTES") +
          ". En ese mismo archivo están las listas " + M("PROMPTS") + " y " + M("ERRORES") + " donde se agregan los datos del paso 1.",
          "Instala la librería una sola vez: " + M("pip install reportlab"),
          "Desde la carpeta raíz del repo ejecuta: " + M("python3 herramientas/generar_documentos.py"),
          "Revisa el aviso final: si dice que faltan capturas o nombres, corrige y vuelve a ejecutar.",
          "Se crean <i>entrega/Telecom1_Asignacion1_Equipo4.zip</i> (informe, script y diagrama) y los PDF de cada integrante en <i>informe/</i>.",
          "Sube a GitHub la carpeta <i>entrega</i> para que todos tengan la versión final."]),
])

h += paso("8", "Subir al Aula Virtual", "Un solo integrante · antes de las 10:30 AM", [
    *bullets(["Entrar al Aula Virtual UNEG y buscar la actividad <i>Asignación Práctica N° 1</i>.",
              "Subir <b>únicamente</b> el archivo <i>Telecom1_Asignacion1_Equipo4.zip</i>. El nombre debe ser exacto.",
              "Confirmar que la plataforma muestre el estado <i>Entregado</i> y avisar al grupo con una captura.",
              "Esta es la única vía aceptada; no se recibe por correo ni por WhatsApp."]),
])

h += paso("9", "Revisión final antes de entregar", "Todos · viernes 8:00 AM", [
    P("Abrir el PDF del ZIP (no el borrador) y marcar cada punto:", st_n),
    tabla([["Revisión", "Detalle"],
           ["Portada", "Equipo 4, materia, profesor, fecha y los 5 nombres completos"],
           ["Parte I", "Las preguntas 2.1 a 2.4 ocupan <b>una sola página</b>"],
           ["Diagrama", "Se lee bien y coincide con el script (IPs, puertos, prioridades)"],
           ["Parte II", "Las 9 capturas están en su sitio; ya no hay recuadros amarillos"],
           ["Parte III", "Herramienta y modelo de IA, prompts textuales, al menos un error de la IA refutado y la matriz de roles"],
           ["ZIP", "Contiene el informe en PDF, el script <i>.sh</i> y el diagrama; el nombre del ZIP es correcto"],
           ["Script", "Es el mismo archivo que se ejecutó en Azure (si se modificó algo, volver a probarlo)"]],
          [1.4 * inch, W - 1.4 * inch]),
])

# ---------------------------------------------------------------- 4
h.append(P("Si algo falla en la ejecución", st_h1))
h.append(tabla([["Síntoma", "Causa probable", "Qué hacer"],
                ["Error de cuota o «SKU not available» para Standard_B1s", "Sin cupo en la región o suscripción limitada",
                 "Correr con " + M("VM_SIZE=Standard_B2s") + " (si quedó a medias, borrar antes el grupo)"],
                ["Se queda sin capacidad en eastus", "La región está saturada", "Correr con " + M("LOCATION=westus2") + " (o centralus)"],
                ["«No se pudo detectar la IP pública del administrador»", "Cloud Shell sin salida a api.ipify.org",
                 "Buscar la IP en cualquier web de «cuál es mi IP» y correr con " + M("ADMIN_IP=x.x.x.x")],
                ["Prueba A sin código 200", "Nginx aún arrancando", "Esperar un minuto y probar: " + M("curl -I http://IP_PUBLICA")],
                ["Prueba B falla", "El servicio de vm-db no arrancó", "Revisar con " + M("az vm run-command invoke -g rg-telecom1-equipo4 -n vm-db --command-id RunShellScript --scripts \"ss -ltn\"")],
                ["Pruebas D salen como AVISO", "Network Watcher no está disponible en la suscripción",
                 "Capturar el resto y anotar la limitación en el informe"],
                ["Se cortó la conexión de Cloud Shell", "Inactividad o red", "Reabrir Cloud Shell, borrar el grupo y volver a correr desde cero"],
                ["Quedó a medias o hay recursos sueltos", "Ejecución interrumpida", "Borrar el grupo de recursos y repetir; el script no es reanudable"]],
               [1.95 * inch, 1.65 * inch, W - 3.6 * inch]))

construir(os.path.join(BASE, "entrega", "Manual_Proximos_Pasos_Equipo4.pdf"), h,
          "Telecom I · Asignación Práctica N° 1 · Equipo 4 · Manual de próximos pasos", "Manual de próximos pasos – Equipo 4")
print("Manual generado")
