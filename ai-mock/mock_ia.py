from flask import Flask, request, jsonify
from datetime import datetime
import re

app = Flask(__name__)

# IVA fijo al 10% (como en tu aplicación)
IVA = 0.10


def extraer_productos(texto):
    """
    Extrae productos, cantidades y precios del texto
    Detecta patrones comunes en mensajes de WhatsApp
    """
    productos = []
    
    # Patrones mejorados para detectar productos de floristería
    patrones = [
        # "2 ramos de rosas a 30 euros"
        r'(\d+)\s+(ramos?|centros?|plantas?|arreglos?|bouquets?|coronas?)[^0-9]*?([a-záéíóúñ\s]+?)\s+a\s+(\d+(?:[.,]\d{1,2})?)\s*(?:euros?|€|eur)',
        # "ramo de rosas 30€"
        r'(ramos?|centros?|plantas?|arreglos?|bouquets?|coronas?)\s+(?:de\s+)?([a-záéíóúñ\s]+?)\s+(\d+(?:[.,]\d{1,2})?)\s*(?:euros?|€|eur)',
        # "2x ramo de rosas - 30€"
        r'(\d+)\s*x?\s+(ramos?|centros?|plantas?|arreglos?)[^0-9]*?([a-záéíóúñ\s]+?)\s*[-–]\s*(\d+(?:[.,]\d{1,2})?)\s*(?:euros?|€|eur)',
        # Patrón genérico: "cantidad producto precio"
        r'(\d+)\s+([a-záéíóúñ\s]{3,30}?)\s+(\d+(?:[.,]\d{1,2})?)\s*(?:euros?|€|eur)',
    ]
    
    texto_lower = texto.lower()
    
    for patron in patrones:
        matches = re.finditer(patron, texto_lower, re.IGNORECASE)
        for match in matches:
            grupos = match.groups()
            
            # Determinar cantidad, tipo y precio según el patrón
            if len(grupos) == 4:
                # Patrón con tipo de producto explícito
                cantidad_str = grupos[0]
                tipo = grupos[1]
                nombre = grupos[2]
                precio_str = grupos[3]
                
                try:
                    cantidad = int(cantidad_str) if cantidad_str.isdigit() else 1
                except:
                    cantidad = 1
                    
                producto = f"{tipo.title()} {nombre.strip().title()}"
            elif len(grupos) == 3:
                # Patrón simple
                if grupos[0].isdigit():
                    # "2 rosas 30€"
                    cantidad = int(grupos[0])
                    producto = grupos[1].strip().title()
                    precio_str = grupos[2]
                else:
                    # "ramo de rosas 30€"
                    cantidad = 1
                    producto = f"{grupos[0].title()} {grupos[1].strip().title()}"
                    precio_str = grupos[2]
            else:
                continue
            
            # Limpiar y convertir precio
            precio_str = precio_str.replace(',', '.')
            try:
                precio_unitario = float(precio_str)
            except:
                continue
            
            # Calcular valores (precio base sin IVA)
            base_unitaria = precio_unitario
            base_total = base_unitaria * cantidad
            iva_total = base_total * IVA
            total = base_total + iva_total
            
            productos.append({
                'producto': producto.strip(),
                'cantidad': cantidad,
                'base': round(base_total, 2),
                'iva': round(iva_total, 2),
                'total': round(total, 2)
            })
    
    # Si no se encontraron productos, intentar detectar solo precios y asumir cantidad 1
    if not productos:
        precios = re.findall(r'(\d+(?:[.,]\d{1,2})?)\s*(?:euros?|€|eur)', texto_lower)
        if precios:
            precio = float(precios[0].replace(',', '.'))
            base = precio
            iva = base * IVA
            total = base + iva
            
            productos.append({
                'producto': 'Producto Genérico',
                'cantidad': 1,
                'base': round(base, 2),
                'iva': round(iva, 2),
                'total': round(total, 2)
            })
    
    return productos


def extraer_numero_factura(texto):
    """
    Intenta extraer un número de factura si está mencionado
    """
    patrones = [
        r'factura\s*[:#]?\s*(\d{4}-\d{3})',  # factura: 2025-001
        r'n[uúº]mero\s+(\d{4}-\d{3})',        # número 2025-001
        r'factura\s+n[uúº]\s*(\d+)',          # factura nº 123
    ]
    
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Si no se encuentra, generar uno basado en fecha
    ahora = datetime.now()
    return f"{ahora.year}-{ahora.month:02d}{ahora.day:02d}{ahora.hour:02d}{ahora.minute:02d}"


def extraer_cliente(texto):
    """
    Intenta extraer el nombre del cliente del texto
    """
    patrones = [
        r'para\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})',
        r'cliente:?\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})',
        r'a nombre de\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})',
        r'destinatario:?\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})',
    ]
    
    for patron in patrones:
        match = re.search(patron, texto)
        if match:
            return match.group(1).strip()
    
    return "Cliente"


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'mock-ia-flores-loli',
        'empresa': 'Flores y Plantas Loli',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/procesar-pedido', methods=['POST'])
def procesar_pedido():
    """
    Endpoint que recibe texto en lenguaje natural y devuelve JSON estructurado
    Formato de salida compatible con tu aplicación
    
    Ejemplo de entrada:
    {
        "texto": "Pedido para Juan Pérez: 2 ramos de rosas a 30 euros y 1 centro de mesa a 45 euros",
        "numero": "2025-001"  // Opcional
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        
        if 'texto' not in data:
            return jsonify({
                'error': 'Campo "texto" requerido'
            }), 400
        
        texto = data['texto']
        
        # Extraer información del texto
        cliente_nombre = extraer_cliente(texto)
        productos = extraer_productos(texto)
        
        # Número de factura (usar el proporcionado o generar uno)
        numero = data.get('numero', extraer_numero_factura(texto))
        
        # Validar que se encontraron productos
        if not productos:
            return jsonify({
                'error': 'No se pudieron extraer productos del texto',
                'sugerencia': 'Formato esperado: "2 ramos de rosas a 30 euros"'
            }), 400
        
        # Limitar a 10 productos (como en tu app)
        if len(productos) > 10:
            productos = productos[:10]
            mensaje_warning = 'Solo se procesaron los primeros 10 productos'
        else:
            mensaje_warning = None
        
        # Generar fecha actual
        fecha = datetime.now().strftime('%d/%m/%Y')
        
        # Construir respuesta en formato compatible con tu PDF
        respuesta = {
            'numero': numero,
            'fecha': fecha,
            'cliente': {
                'nombre': cliente_nombre
            },
            'items': productos
        }
        
        # Calcular totales
        subtotal = sum(item['base'] for item in productos)
        iva_total = sum(item['iva'] for item in productos)
        total = sum(item['total'] for item in productos)
        
        response_data = {
            'success': True,
            'mensaje': 'Pedido procesado correctamente',
            'texto_original': texto,
            'factura': respuesta,
            'resumen': {
                'subtotal': round(subtotal, 2),
                'iva': round(iva_total, 2),
                'total': round(total, 2),
                'num_items': len(productos)
            }
        }
        
        if mensaje_warning:
            response_data['warning'] = mensaje_warning
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error al procesar el pedido',
            'details': str(e)
        }), 500


@app.route('/ejemplos', methods=['GET'])
def ejemplos():
    """
    Endpoint que devuelve ejemplos de uso para floristería
    """
    return jsonify({
        'service': 'Mock IA - Flores y Plantas Loli',
        'empresa': {
            'nombre': 'FLORES Y PLANTAS LOLI',
            'ubicacion': 'C/ Escritor Jiménez Lora 15, CP: 14014',
            'contacto': '+34 957 25 14 20'
        },
        'ejemplos': [
            {
                'descripcion': 'Pedido simple con ramo',
                'texto': 'Para María García: 1 ramo de rosas a 35 euros'
            },
            {
                'descripcion': 'Pedido múltiple',
                'texto': 'Para Juan Pérez: 2 ramos de rosas a 30 euros y 1 centro de mesa a 45 euros'
            },
            {
                'descripcion': 'Pedido con plantas',
                'texto': 'Cliente Ana López: 3 plantas de interior a 15 euros cada una'
            },
            {
                'descripcion': 'Arreglo floral',
                'texto': '1 arreglo floral para evento a 120 euros, cliente: Hotel Plaza'
            },
            {
                'descripcion': 'Corona funeral',
                'texto': 'Para familia Rodríguez: 1 corona de flores a 80 euros'
            }
        ],
        'formato_salida': {
            'numero': 'string (generado automáticamente: YYYY-MMDDHHMMSS)',
            'fecha': 'string (DD/MM/YYYY - fecha actual)',
            'cliente': {'nombre': 'string'},
            'items': [
                {
                    'producto': 'string',
                    'cantidad': 'number',
                    'base': 'number (sin IVA)',
                    'iva': 'number (10%)',
                    'total': 'number (base + IVA)'
                }
            ]
        },
        'notas': [
            'IVA aplicado: 10%',
            'Máximo 10 productos por factura',
            'Detecta automáticamente: ramos, centros, plantas, arreglos, coronas, bouquets',
            'Formatos de precio aceptados: "30 euros", "30€", "30 eur"'
        ]
    })


@app.route('/test', methods=['POST'])
def test_extraccion():
    """
    Endpoint de prueba para ver qué extrae el sistema de un texto
    Útil para debugging
    """
    try:
        data = request.get_json()
        texto = data.get('texto', '')
        
        return jsonify({
            'texto': texto,
            'cliente_detectado': extraer_cliente(texto),
            'productos_detectados': extraer_productos(texto),
            'numero_factura_generado': extraer_numero_factura(texto)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("🤖 Iniciando Mock IA - FLORES Y PLANTAS LOLI")
    print("🌸 Sistema de procesamiento de pedidos por lenguaje natural")
    print("📝 Endpoint principal: POST /procesar-pedido")
    print("📚 Ejemplos disponibles: GET /ejemplos")
    print("🧪 Test de extracción: POST /test")
    app.run(host='0.0.0.0', port=5001, debug=True)