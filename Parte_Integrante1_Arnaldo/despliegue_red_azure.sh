#!/usr/bin/env bash
# =============================================================================
#  Telecom I – Asignación Práctica N° 1 · Equipo 4
#  despliegue_red_azure.sh
#
#  Despliega y valida en Microsoft Azure una VNet corporativa segmentada en:
#    - Subred pública  (Frontend) 10.0.1.0/24 -> vm-web, con IP pública
#    - Subred privada  (Backend)  10.0.2.0/24 -> vm-db,  SIN IP pública
#  protegidas por Network Security Groups (nsg-web y nsg-db) asociados a
#  nivel de subred.
#
#  Uso (Azure Cloud Shell o Linux/macOS con Azure CLI y sesión iniciada):
#      chmod +x despliegue_red_azure.sh
#      ./despliegue_red_azure.sh
#
#  Variables opcionales:
#      ADMIN_IP=203.0.113.25 ./despliegue_red_azure.sh   # IP del admin para SSH
#      VM_SIZE=Standard_B2s ./despliegue_red_azure.sh     # si no hay cupo de B1s
#      LIMPIAR=1 ./despliegue_red_azure.sh                # borra todo al final
#
#  Roles: VNet/CIDR (Integrante 1) · Subredes y enrutamiento (Integrante 2)
#         Reglas NSG (Integrante 3) · Automatización y pruebas (Integrante 4)
#         Auditoría y validación de seguridad (Integrante 5)
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# 0. Parámetros de la topología (diseño del Integrante 1)
# -----------------------------------------------------------------------------
LOCATION="${LOCATION:-eastus}"
RG="rg-telecom1-equipo4"

VNET_NAME="vnet-telecom1"
VNET_CIDR="10.0.0.0/16"

SUBNET_PUB="snet-publica"
SUBNET_PUB_CIDR="10.0.1.0/24"

SUBNET_PRIV="snet-privada"
SUBNET_PRIV_CIDR="10.0.2.0/24"

NSG_WEB="nsg-web"
NSG_DB="nsg-db"

VM_WEB="vm-web"
VM_WEB_IP="10.0.1.4"
VM_DB="vm-db"
VM_DB_IP="10.0.2.4"
PIP_WEB="pip-web"

VM_SIZE="${VM_SIZE:-Standard_B1s}"
VM_IMAGE="Ubuntu2204"
ADMIN_USER="azureuser"

DB_PORT=5432
ADMIN_IP="${ADMIN_IP:-}"
LIMPIAR="${LIMPIAR:-0}"

# IP pública de documentación (RFC 5737) usada para simular un atacante en Internet
IP_EXTERNA_PRUEBA="203.0.113.50"

# -----------------------------------------------------------------------------
# Utilidades de salida
# -----------------------------------------------------------------------------
PASARON=0
FALLARON=0
paso()   { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
info()   { printf '    %s\n' "$*"; }
ok()     { printf '\033[1;32m  [OK]\033[0m %s\n' "$*"; PASARON=$((PASARON + 1)); }
fallo()  { printf '\033[1;31m  [FALLO]\033[0m %s\n' "$*"; FALLARON=$((FALLARON + 1)); }
aviso()  { printf '\033[1;33m  [AVISO]\033[0m %s\n' "$*"; }

# -----------------------------------------------------------------------------
# Verificaciones previas
# -----------------------------------------------------------------------------
paso "Verificaciones previas"
command -v az >/dev/null 2>&1 || { echo "Azure CLI no está instalado. Usa Azure Cloud Shell."; exit 1; }
az account show -o none 2>/dev/null || { echo "No hay sesión de Azure. Ejecuta 'az login'."; exit 1; }
info "Suscripción: $(az account show --query name -o tsv)"

if [[ -z "$ADMIN_IP" ]]; then
  ADMIN_IP="$(curl -s --max-time 10 https://api.ipify.org || true)"
fi
if [[ ! "$ADMIN_IP" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]]; then
  echo "No se pudo detectar la IP pública del administrador."
  echo "Ejecuta: ADMIN_IP=<tu-ip-publica> ./despliegue_red_azure.sh"
  exit 1
fi
info "IP del administrador para SSH: ${ADMIN_IP}/32"

# -----------------------------------------------------------------------------
# 1. Grupo de recursos
# -----------------------------------------------------------------------------
paso "1. Grupo de recursos: $RG ($LOCATION)"
az group create --name "$RG" --location "$LOCATION" -o none

# -----------------------------------------------------------------------------
# 2. Red virtual y subredes (3.1 y 3.2)
# -----------------------------------------------------------------------------
paso "2. VNet $VNET_NAME ($VNET_CIDR) y subredes"
az network vnet create \
  --resource-group "$RG" \
  --name "$VNET_NAME" \
  --location "$LOCATION" \
  --address-prefixes "$VNET_CIDR" \
  --subnet-name "$SUBNET_PUB" \
  --subnet-prefixes "$SUBNET_PUB_CIDR" \
  -o none
info "Subred pública $SUBNET_PUB ($SUBNET_PUB_CIDR) creada"

az network vnet subnet create \
  --resource-group "$RG" \
  --vnet-name "$VNET_NAME" \
  --name "$SUBNET_PRIV" \
  --address-prefixes "$SUBNET_PRIV_CIDR" \
  -o none
info "Subred privada $SUBNET_PRIV ($SUBNET_PRIV_CIDR) creada"

# La subred privada se marca explícitamente como privada: sin acceso de salida
# por defecto a Internet (comportamiento por defecto en VNets nuevas desde 31/03/2026).
az network vnet subnet update \
  --resource-group "$RG" --vnet-name "$VNET_NAME" --name "$SUBNET_PRIV" \
  --default-outbound false -o none 2>/dev/null \
  && info "Subred privada sin salida a Internet por defecto (defaultOutboundAccess=false)" \
  || aviso "Esta versión de Azure CLI no admite --default-outbound; se mantiene el valor por defecto"

# -----------------------------------------------------------------------------
# 3. Network Security Groups y reglas (3.3)
# -----------------------------------------------------------------------------
paso "3. NSG $NSG_WEB (Frontend)"
az network nsg create --resource-group "$RG" --name "$NSG_WEB" --location "$LOCATION" -o none

# P100: HTTP y HTTPS desde cualquier origen de Internet
az network nsg rule create \
  --resource-group "$RG" --nsg-name "$NSG_WEB" \
  --name Allow-HTTP-HTTPS-Internet \
  --priority 100 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes Internet --source-port-ranges '*' \
  --destination-address-prefixes "$SUBNET_PUB_CIDR" --destination-port-ranges 80 443 \
  --description "Trafico web publico hacia la subred Frontend" \
  -o none
info "P100 Allow TCP 80,443 desde Internet"

# P110: SSH solo desde la IP del administrador (/32), nunca desde 0.0.0.0/0
az network nsg rule create \
  --resource-group "$RG" --nsg-name "$NSG_WEB" \
  --name Allow-SSH-Admin \
  --priority 110 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes "${ADMIN_IP}/32" --source-port-ranges '*' \
  --destination-address-prefixes "$SUBNET_PUB_CIDR" --destination-port-ranges 22 \
  --description "Administracion SSH restringida a la IP del administrador" \
  -o none
info "P110 Allow TCP 22 solo desde ${ADMIN_IP}/32"

paso "3. NSG $NSG_DB (Backend)"
az network nsg create --resource-group "$RG" --name "$NSG_DB" --location "$LOCATION" -o none

# P100: PostgreSQL únicamente si el origen es la subred pública
az network nsg rule create \
  --resource-group "$RG" --nsg-name "$NSG_DB" \
  --name Allow-PostgreSQL-From-Web \
  --priority 100 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes "$SUBNET_PUB_CIDR" --source-port-ranges '*' \
  --destination-address-prefixes "$SUBNET_PRIV_CIDR" --destination-port-ranges "$DB_PORT" \
  --description "Solo la subred web puede consultar la base de datos" \
  -o none
info "P100 Allow TCP $DB_PORT solo desde $SUBNET_PUB_CIDR"

# P4000: Deny explícito de todo lo demás. Se evalúa ANTES que AllowVnetInBound
# (65000), así que también bloquea cualquier otro origen interno de la VNet.
az network nsg rule create \
  --resource-group "$RG" --nsg-name "$NSG_DB" \
  --name Deny-All-Inbound \
  --priority 4000 --direction Inbound --access Deny --protocol '*' \
  --source-address-prefixes '*' --source-port-ranges '*' \
  --destination-address-prefixes '*' --destination-port-ranges '*' \
  --description "Deniega cualquier otra conexion entrante a la base de datos" \
  -o none
info "P4000 Deny todo el tráfico entrante restante"

paso "3. Asociación de los NSG a sus subredes"
az network vnet subnet update --resource-group "$RG" --vnet-name "$VNET_NAME" \
  --name "$SUBNET_PUB" --network-security-group "$NSG_WEB" -o none
info "$NSG_WEB -> $SUBNET_PUB"
az network vnet subnet update --resource-group "$RG" --vnet-name "$VNET_NAME" \
  --name "$SUBNET_PRIV" --network-security-group "$NSG_DB" -o none
info "$NSG_DB -> $SUBNET_PRIV"

# -----------------------------------------------------------------------------
# 4. Máquinas virtuales
#    --nsg "" evita que Azure cree un NSG por NIC con SSH abierto a cualquier
#    origen (comportamiento por defecto de 'az vm create'). La seguridad se
#    controla solo con los NSG de subred.
# -----------------------------------------------------------------------------
paso "4. VM $VM_WEB en $SUBNET_PUB (con IP pública $PIP_WEB)"
az vm create \
  --resource-group "$RG" --name "$VM_WEB" \
  --image "$VM_IMAGE" --size "$VM_SIZE" \
  --vnet-name "$VNET_NAME" --subnet "$SUBNET_PUB" \
  --private-ip-address "$VM_WEB_IP" \
  --public-ip-address "$PIP_WEB" --public-ip-sku Standard \
  --nsg "" \
  --admin-username "$ADMIN_USER" --generate-ssh-keys \
  -o none

paso "4. VM $VM_DB en $SUBNET_PRIV (SIN IP pública)"
az vm create \
  --resource-group "$RG" --name "$VM_DB" \
  --image "$VM_IMAGE" --size "$VM_SIZE" \
  --vnet-name "$VNET_NAME" --subnet "$SUBNET_PRIV" \
  --private-ip-address "$VM_DB_IP" \
  --public-ip-address "" \
  --nsg "" \
  --admin-username "$ADMIN_USER" --generate-ssh-keys \
  -o none

# -----------------------------------------------------------------------------
# 5. Servicios
#    vm-web: Nginx en los puertos 80/443 (tiene salida a Internet por su IP pública).
#    vm-db : al estar en una subred privada sin salida a Internet no puede
#            descargar paquetes; se levanta un servicio TCP en el puerto 5432
#            con python3 (incluido en la imagen) para validar la conectividad
#            Este-Oeste. En producción se instalaría PostgreSQL usando una
#            NAT Gateway o una imagen preparada.
#    'az vm run-command' usa el agente de Azure, no la red, por lo que funciona
#    aunque nsg-db bloquee SSH.
# -----------------------------------------------------------------------------
paso "5. Instalando Nginx en $VM_WEB"
az vm run-command invoke --resource-group "$RG" --name "$VM_WEB" \
  --command-id RunShellScript \
  --scripts "apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y nginx && systemctl enable --now nginx" \
  -o none
info "Nginx activo"

paso "5. Servicio en el puerto $DB_PORT de $VM_DB"
az vm run-command invoke --resource-group "$RG" --name "$VM_DB" \
  --command-id RunShellScript \
  --scripts "systemd-run --unit=servicio-bd-$DB_PORT --property=Restart=always python3 -m http.server $DB_PORT --bind 0.0.0.0" \
  -o none
info "Servicio escuchando en $VM_DB_IP:$DB_PORT"

# -----------------------------------------------------------------------------
# 6. Pruebas de conectividad y validación (3.4)
# -----------------------------------------------------------------------------
paso "6. Pruebas de conectividad y validación"
WEB_PUBLIC_IP="$(az network public-ip show --resource-group "$RG" --name "$PIP_WEB" --query ipAddress -o tsv)"
info "IP pública de $VM_WEB: $WEB_PUBLIC_IP"

# Prueba A: el puerto web responde desde el exterior
CODIGO="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "http://${WEB_PUBLIC_IP}" || true)"
if [[ "$CODIGO" == "200" ]]; then
  ok "A. HTTP 80 de $VM_WEB responde desde Internet (código $CODIGO)"
else
  fallo "A. HTTP 80 de $VM_WEB no respondió desde Internet (código '${CODIGO}')"
fi

# Prueba B: la base de datos es accesible desde la subred web
SALIDA_NC="$(az vm run-command invoke --resource-group "$RG" --name "$VM_WEB" \
  --command-id RunShellScript \
  --scripts "nc -zv -w 5 $VM_DB_IP $DB_PORT 2>&1 || true" \
  --query 'value[0].message' -o tsv || true)"
info "$(echo "$SALIDA_NC" | grep -i -E 'succeeded|refused|timed out|open' | head -1 || true)"
if echo "$SALIDA_NC" | grep -q -i 'succeeded'; then
  ok "B. $VM_WEB ($SUBNET_PUB_CIDR) llega a $VM_DB_IP:$DB_PORT"
else
  fallo "B. $VM_WEB no pudo conectar a $VM_DB_IP:$DB_PORT"
fi

# Prueba C: la base de datos no tiene IP pública (no existe ruta desde Internet)
IP_PUBLICA_DB="$(az vm list-ip-addresses --resource-group "$RG" --name "$VM_DB" \
  --query '[0].virtualMachine.network.publicIpAddresses[0].ipAddress' -o tsv || true)"
if [[ -z "$IP_PUBLICA_DB" ]]; then
  ok "C. $VM_DB no tiene IP pública: es inalcanzable desde Internet"
else
  fallo "C. $VM_DB tiene IP pública ($IP_PUBLICA_DB): falla de diseño"
fi

# Prueba D: verificación de reglas con Network Watcher (IP flow verify).
# Simula paquetes contra las reglas efectivas y devuelve la regla que coincide.
az group create --name NetworkWatcherRG --location "$LOCATION" -o none 2>/dev/null || true
az network watcher configure --resource-group NetworkWatcherRG --locations "$LOCATION" --enabled true -o none 2>/dev/null || true

verificar_flujo() {
  local vm="$1" local_ep="$2" remoto="$3" esperado="$4" descripcion="$5" resultado
  resultado="$(az network watcher test-ip-flow --resource-group "$RG" --vm "$vm" \
    --direction Inbound --protocol TCP --local "$local_ep" --remote "$remoto" \
    --query '[access, ruleName]' -o tsv 2>/dev/null | tr '\n' ' ' || true)"
  if [[ -z "$resultado" ]]; then
    aviso "D. $descripcion: Network Watcher no disponible en esta suscripción"
  elif [[ "$resultado" == "$esperado"* ]]; then
    ok "D. $descripcion -> $resultado"
  else
    fallo "D. $descripcion -> $resultado (se esperaba $esperado)"
  fi
}
verificar_flujo "$VM_DB"  "${VM_DB_IP}:${DB_PORT}"  "${IP_EXTERNA_PRUEBA}:50000" "Deny"  "Internet -> $VM_DB:$DB_PORT"
verificar_flujo "$VM_DB"  "${VM_DB_IP}:${DB_PORT}"  "${VM_WEB_IP}:50000"         "Allow" "$VM_WEB -> $VM_DB:$DB_PORT"
verificar_flujo "$VM_DB"  "${VM_DB_IP}:22"          "${VM_WEB_IP}:50000"         "Deny"  "$VM_WEB -> $VM_DB:22 (otro puerto)"
verificar_flujo "$VM_WEB" "${VM_WEB_IP}:443"        "${IP_EXTERNA_PRUEBA}:50000" "Allow" "Internet -> $VM_WEB:443"
verificar_flujo "$VM_WEB" "${VM_WEB_IP}:22"         "${IP_EXTERNA_PRUEBA}:50000" "Deny"  "Internet (no admin) -> $VM_WEB:22"

# -----------------------------------------------------------------------------
# 7. Evidencias para el informe (tablas para las capturas)
# -----------------------------------------------------------------------------
paso "7. Evidencias"
echo; echo "--- Subredes y NSG asociados ---"
az network vnet subnet list --resource-group "$RG" --vnet-name "$VNET_NAME" \
  --query '[].{Subred:name, CIDR:addressPrefix, NSG:networkSecurityGroup.id}' -o table || true
echo; echo "--- Reglas de $NSG_WEB ---"
az network nsg rule list --resource-group "$RG" --nsg-name "$NSG_WEB" \
  --query '[].{Prioridad:priority, Nombre:name, Accion:access, Origen:sourceAddressPrefix, Puertos:join(`,`, destinationPortRanges || [destinationPortRange])}' -o table || true
echo; echo "--- Reglas de $NSG_DB ---"
az network nsg rule list --resource-group "$RG" --nsg-name "$NSG_DB" \
  --query '[].{Prioridad:priority, Nombre:name, Accion:access, Origen:sourceAddressPrefix, Puertos:destinationPortRange}' -o table || true
echo; echo "--- Direcciones de las VMs ---"
az vm list-ip-addresses --resource-group "$RG" \
  --query '[].{VM:virtualMachine.name, IPPrivada:virtualMachine.network.privateIpAddresses[0], IPPublica:virtualMachine.network.publicIpAddresses[0].ipAddress}' -o table || true

# -----------------------------------------------------------------------------
# 8. Resumen y limpieza
# -----------------------------------------------------------------------------
paso "Resumen: $PASARON pruebas correctas, $FALLARON con fallo"
if [[ "$LIMPIAR" == "1" ]]; then
  paso "Eliminando el grupo de recursos $RG"
  az group delete --name "$RG" --yes --no-wait
  info "Eliminación en curso."
else
  info "Para no gastar crédito, al terminar las capturas ejecuta:"
  info "  az group delete --name $RG --yes --no-wait"
fi

[[ "$FALLARON" -eq 0 ]]
