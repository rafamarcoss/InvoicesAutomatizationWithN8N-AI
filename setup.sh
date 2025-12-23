#!/bin/bash

# Script de configuración inicial para Flores y Plantas Loli
# Ejecutar desde: facturacion-volumes/

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   🌸 FLORES Y PLANTAS LOLI - Setup Inicial           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -d "ai-mock" ] || [ ! -d "pdf-service" ]; then
    echo -e "${RED}❌ Error: Ejecuta este script desde facturacion-volumes/${NC}"
    echo "   Estructura esperada:"
    echo "   facturacion-volumes/"
    echo "   ├── ai-mock/"
    echo "   └── pdf-service/"
    exit 1
fi

echo -e "${YELLOW}📋 Paso 1: Verificando estructura de directorios...${NC}"

# Crear directorios necesarios
mkdir -p volumes/invoices
mkdir -p volumes/n8n

echo -e "${GREEN}✓ Directorios creados/verificados${NC}"
echo ""

# Verificar archivos necesarios
echo -e "${YELLOW}📋 Paso 2: Verificando archivos...${NC}"

ARCHIVOS_REQUERIDOS=(
    "ai-mock/Dockerfile"
    "ai-mock/requirements.txt"
    "ai-mock/mock_ia.py"
    "pdf-service/Dockerfile"
    "pdf-service/requirements.txt"
    "pdf-service/app.py"
    "docker-compose.yml"
)

FALTANTES=0
for archivo in "${ARCHIVOS_REQUERIDOS[@]}"; do
    if [ -f "$archivo" ]; then
        echo -e "  ${GREEN}✓${NC} $archivo"
    else
        echo -e "  ${RED}✗${NC} $archivo ${RED}(FALTANTE)${NC}"
        FALTANTES=$((FALTANTES + 1))
    fi
done

if [ $FALTANTES -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ Faltan $FALTANTES archivos necesarios${NC}"
    echo "   Copia los archivos que te proporcioné en las ubicaciones indicadas"
    exit 1
fi

echo -e "${GREEN}✓ Todos los archivos necesarios están presentes${NC}"
echo ""

# Verificar logo
echo -e "${YELLOW}📋 Paso 3: Verificando logo...${NC}"
if [ -f "volumes/logo.png" ]; then
    echo -e "${GREEN}✓ Logo encontrado: volumes/logo.png${NC}"
else
    echo -e "${YELLOW}⚠ Logo no encontrado (opcional)${NC}"
    echo "  Si tienes un logo, cópialo a: volumes/logo.png"
fi
echo ""

# Verificar Docker
echo -e "${YELLOW}📋 Paso 4: Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker: $(docker --version)${NC}"
echo -e "${GREEN}✓ Docker Compose: $(docker-compose --version)${NC}"
echo ""

# Detener contenedores existentes si los hay
echo -e "${YELLOW}📋 Paso 5: Limpiando contenedores anteriores...${NC}"
if docker-compose ps -q 2>/dev/null | grep -q .; then
    echo "  Deteniendo contenedores existentes..."
    docker-compose down
    echo -e "${GREEN}✓ Contenedores detenidos${NC}"
else
    echo -e "${GREEN}✓ No hay contenedores previos${NC}"
fi
echo ""

# Construir imágenes
echo -e "${YELLOW}📋 Paso 6: Construyendo imágenes Docker...${NC}"
echo "  Esto puede tardar varios minutos la primera vez..."
echo ""

if docker-compose build; then
    echo -e "${GREEN}✓ Imágenes construidas exitosamente${NC}"
else
    echo -e "${RED}❌ Error al construir imágenes${NC}"
    exit 1
fi
echo ""

# Iniciar servicios
echo -e "${YELLOW}📋 Paso 7: Iniciando servicios...${NC}"
if docker-compose up -d; then
    echo -e "${GREEN}✓ Servicios iniciados${NC}"
else
    echo -e "${RED}❌ Error al iniciar servicios${NC}"
    exit 1
fi
echo ""

# Esperar a que los servicios estén listos
echo -e "${YELLOW}📋 Paso 8: Esperando a que los servicios estén listos...${NC}"
echo "  Esto puede tardar 10-20 segundos..."

sleep 5

# Verificar servicios
MAX_INTENTOS=12
INTERVALO=5

check_service() {
    local url=$1
    local nombre=$2
    local intentos=0
    
    while [ $intentos -lt $MAX_INTENTOS ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $nombre listo"
            return 0
        fi
        intentos=$((intentos + 1))
        if [ $intentos -lt $MAX_INTENTOS ]; then
            sleep $INTERVALO
        fi
    done
    
    echo -e "  ${RED}✗${NC} $nombre no responde"
    return 1
}

SERVICIOS_OK=0
SERVICIOS_TOTAL=3

check_service "http://localhost:5000/health" "PDF Service (5000)" && SERVICIOS_OK=$((SERVICIOS_OK + 1))
check_service "http://localhost:5001/health" "AI Mock (5001)" && SERVICIOS_OK=$((SERVICIOS_OK + 1))
check_service "http://localhost:5678/healthz" "n8n (5678)" && SERVICIOS_OK=$((SERVICIOS_OK + 1))

echo ""

if [ $SERVICIOS_OK -eq $SERVICIOS_TOTAL ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         ✅ SISTEMA LISTO Y FUNCIONANDO                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}🔗 URLS DISPONIBLES:${NC}"
    echo "  • n8n Panel:    http://localhost:5678"
    echo "                  Usuario: admin"
    echo "                  Contraseña: floristeria2025"
    echo ""
    echo "  • PDF Service:  http://localhost:5000"
    echo "                  Info: http://localhost:5000/info"
    echo ""
    echo "  • AI Mock:      http://localhost:5001"
    echo "                  Ejemplos: http://localhost:5001/ejemplos"
    echo ""
    echo -e "${BLUE}📁 DIRECTORIOS:${NC}"
    echo "  • Facturas: $(pwd)/volumes/invoices/"
    echo "  • Datos n8n: $(pwd)/volumes/n8n/"
    echo ""
    echo -e "${BLUE}🧪 SIGUIENTE PASO:${NC}"
    echo "  Ejecuta las pruebas con:"
    echo "  $ bash test_sistema.sh"
    echo ""
    echo -e "${BLUE}📖 COMANDOS ÚTILES:${NC}"
    echo "  • Ver logs:        docker-compose logs -f"
    echo "  • Detener:         docker-compose down"
    echo "  • Reiniciar:       docker-compose restart"
    echo "  • Ver estado:      docker-compose ps"
    echo ""
else
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║    ⚠️  ALGUNOS SERVICIOS NO ESTÁN LISTOS              ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Servicios funcionando: $SERVICIOS_OK/$SERVICIOS_TOTAL${NC}"
    echo ""
    echo "Verifica los logs con:"
    echo "  $ docker-compose logs"
    echo ""
    echo "O logs específicos:"
    echo "  $ docker-compose logs pdf-service"
    echo "  $ docker-compose logs ai-mock"
    echo "  $ docker-compose logs n8n"
    exit 1
fi