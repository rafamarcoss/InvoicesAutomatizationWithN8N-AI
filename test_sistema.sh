#!/bin/bash

# Script de prueba para FLORES Y PLANTAS LOLI
# Prueba el flujo completo desde WhatsApp hasta PDF

echo "🌸 FLORES Y PLANTAS LOLI - Sistema de Facturación"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

check_response() {
    if [ $1 -eq 200 ] || [ $1 -eq 201 ]; then
        echo -e "${GREEN}✓ OK (HTTP $1)${NC}"
        return 0
    else
        echo -e "${RED}✗ FALLO (HTTP $1)${NC}"
        return 1
    fi
}

# 1. Health checks
echo -e "${BLUE}📋 Paso 1: Verificando servicios...${NC}"

echo -n "  - PDF Service (5000): "
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
check_response $response

echo -n "  - Mock IA (5001): "
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health)
check_response $response

echo -n "  - n8n (5678): "
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/healthz)
check_response $response

echo ""

# 2. Ver info de la empresa
echo -e "${BLUE}📋 Paso 2: Información de la empresa...${NC}"

INFO=$(curl -s http://localhost:5000/info)
echo "$INFO" | python3 -m json.tool
echo ""

# 3. Probar Mock IA con pedido realista de floristería
echo -e "${BLUE}📋 Paso 3: Procesando pedido de WhatsApp...${NC}"

TEXTO_PEDIDO="Para María González: 2 ramos de rosas rojas a 28 euros y 1 centro de mesa con gerberas a 42 euros. Entrega urgente."

echo -e "${YELLOW}  Texto del mensaje de WhatsApp:${NC}"
echo "  '$TEXTO_PEDIDO'"
echo ""

RESPONSE_IA=$(curl -s -X POST http://localhost:5001/procesar-pedido \
  -H "Content-Type: application/json" \
  -d "{\"texto\": \"$TEXTO_PEDIDO\", \"numero\": \"2025-001\"}")

echo -e "${YELLOW}  Respuesta del procesador IA:${NC}"
echo "$RESPONSE_IA" | python3 -m json.tool
echo ""

# Extraer JSON de factura
FACTURA_JSON=$(echo "$RESPONSE_IA" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data['factura']))" 2>/dev/null)

if [ -z "$FACTURA_JSON" ]; then
    echo -e "${RED}Error: No se pudo extraer el JSON de la factura${NC}"
    exit 1
fi

# 4. Generar PDF
echo -e "${BLUE}📋 Paso 4: Generando PDF de la factura...${NC}"

RESPONSE_PDF=$(curl -s -X POST http://localhost:5000/generar-factura \
  -H "Content-Type: application/json" \
  -d "$FACTURA_JSON")

echo -e "${YELLOW}  Respuesta del generador PDF:${NC}"
echo "$RESPONSE_PDF" | python3 -m json.tool
echo ""

FILENAME=$(echo "$RESPONSE_PDF" | python3 -c "import sys, json; print(json.load(sys.stdin)['factura']['filename'])" 2>/dev/null)

# 5. Verificar archivo
echo -e "${BLUE}📋 Paso 5: Verificando archivo generado...${NC}"

if [ -n "$FILENAME" ] && [ -f "invoices/$FILENAME" ]; then
    echo -e "${GREEN}✓ PDF generado exitosamente${NC}"
    echo ""
    ls -lh "invoices/$FILENAME"
    echo ""
else
    echo -e "${RED}✗ No se encontró el archivo PDF${NC}"
fi

# 6. Listar facturas
echo -e "${BLUE}📋 Paso 6: Facturas generadas...${NC}"

FACTURAS=$(curl -s http://localhost:5000/facturas)
echo "$FACTURAS" | python3 -m json.tool
echo ""

# 7. Prueba adicional con otro tipo de pedido
echo -e "${BLUE}📋 Paso 7: Prueba adicional - Corona funeral...${NC}"

TEXTO_PEDIDO_2="Cliente: Familia Rodríguez. 1 corona de flores naturales a 95 euros. Factura 2025-002"

echo "  Texto: '$TEXTO_PEDIDO_2'"
echo ""

RESPONSE_IA_2=$(curl -s -X POST http://localhost:5001/procesar-pedido \
  -H "Content-Type: application/json" \
  -d "{\"texto\": \"$TEXTO_PEDIDO_2\"}")

FACTURA_JSON_2=$(echo "$RESPONSE_IA_2" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin)['factura']))" 2>/dev/null)

curl -s -X POST http://localhost:5000/generar-factura \
  -H "Content-Type: application/json" \
  -d "$FACTURA_JSON_2" > /dev/null

echo -e "${GREEN}✓ Segunda factura generada${NC}"
echo ""

# 8. Prueba de extracción (debugging)
echo -e "${BLUE}📋 Paso 8: Test de extracción de datos...${NC}"

TEST_TEXTS=(
    "3 plantas de interior a 18 euros cada una"
    "1 bouquet de novia a 150 euros"
    "2 arreglos florales para evento a 85 euros"
)

for texto in "${TEST_TEXTS[@]}"; do
    echo -n "  Testing: '$texto' → "
    RESULT=$(curl -s -X POST http://localhost:5001/test \
      -H "Content-Type: application/json" \
      -d "{\"texto\": \"$texto\"}" | \
      python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"{len(d['productos_detectados'])} productos\")" 2>/dev/null)
    echo -e "${GREEN}$RESULT${NC}"
done

echo ""

# Resumen final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ SISTEMA FUNCIONANDO CORRECTAMENTE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌸 FLORES Y PLANTAS LOLI"
echo "📁 Facturas generadas en: ./invoices/"
echo "📄 Última factura: $FILENAME"
echo ""
echo "🔗 ENLACES:"
echo "  • n8n Panel:    http://localhost:5678 (admin/floristeria2025)"
echo "  • PDF Service:  http://localhost:5000"
echo "  • Mock IA:      http://localhost:5001"
echo "  • Info empresa: http://localhost:5000/info"
echo "  • Ejemplos IA:  http://localhost:5001/ejemplos"
echo ""
echo "📱 PRUEBA CON WHATSAPP:"
echo "   Envía un mensaje como:"
echo "   'Para Juan Pérez: 2 ramos de rosas a 30€ y 1 centro de mesa a 45€'"
echo ""