from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from datetime import datetime
import os

app = Flask(__name__)

# IVA fijo al 10%
IVA = 0.10

# Configuración de directorios
INVOICES_DIR = '/app/invoices'
LOGO_PATH = '/app/logo.png'

# Datos de la empresa (tu floristería)
DATOS_EMPRESA = {
    "nombre": "FLORES Y PLANTAS LOLI",
    "direccion": "C/ Escritor Jiménez Lora 15",
    "cp": "CP: 14014",
    "email": "lolifloresyplantas@gmail.com",
    "telefono": "+34 957 25 14 20",
}

# Crear directorio de facturas si no existe
os.makedirs(INVOICES_DIR, exist_ok=True)


def generar_factura_pdf(factura_num, fecha, cliente, items_raw, carpeta_destino):
    """
    Genera el PDF con el diseño exacto de tu aplicación Tkinter
    Mantiene el mismo estilo limpio y profesional
    """
    
    nombre_archivo = f"factura_{factura_num}.pdf"
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
    
    # Crear el canvas para dibujar
    c = canvas.Canvas(ruta_archivo, pagesize=A4)
    width, height = A4
    
    # ===== LOGO Y DATOS EMPRESA (ESQUINA SUPERIOR IZQUIERDA) =====
    y_pos = height - 30*mm
    
    # Logo (si existe)
    if os.path.exists(LOGO_PATH):
        try:
            c.drawImage(LOGO_PATH, 25*mm, y_pos, width=20*mm, height=20*mm, 
                       preserveAspectRatio=True, mask='auto')
        except:
            try:
                c.drawImage(LOGO_PATH, 25*mm, y_pos, width=20*mm, height=20*mm, 
                           preserveAspectRatio=True)
            except:
                pass
    
    # Datos empresa
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    text_x = 25*mm
    text_y = y_pos - 5*mm
    c.drawString(text_x, text_y, DATOS_EMPRESA['direccion'])
    text_y -= 4*mm
    c.drawString(text_x, text_y, DATOS_EMPRESA['cp'])
    text_y -= 4*mm
    c.drawString(text_x, text_y, DATOS_EMPRESA['email'])
    text_y -= 4*mm
    c.drawString(text_x, text_y, DATOS_EMPRESA['telefono'])
    
    # ===== DATOS FACTURA (ESQUINA SUPERIOR DERECHA) =====
    c.setFont("Helvetica-Bold", 11)
    factura_x = width - 70*mm
    factura_y = height - 30*mm
    c.drawRightString(factura_x + 50*mm, factura_y, f"FACTURA: {factura_num}")
    c.setFont("Helvetica", 10)
    factura_y -= 6*mm
    c.drawRightString(factura_x + 50*mm, factura_y, f"Fecha: {fecha}")
    
    # ===== SECCIÓN DATOS CLIENTE =====
    y_pos = height - 75*mm
    
    # Línea superior
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(25*mm, y_pos, width - 25*mm, y_pos)
    
    y_pos -= 8*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(25*mm, y_pos, "Datos cliente")
    
    y_pos -= 6*mm
    c.setFont("Helvetica", 9)
    c.drawString(25*mm, y_pos, f"Nombre: {cliente}")
    
    y_pos -= 8*mm
    # Línea inferior
    c.line(25*mm, y_pos, width - 25*mm, y_pos)
    
    # ===== TABLA DE PRODUCTOS =====
    y_pos -= 15*mm
    
    # Dimensiones de la tabla
    tabla_x = 25*mm
    tabla_width = width - 50*mm
    col_widths = [
        tabla_width * 0.40,  # Producto
        tabla_width * 0.15,  # Cantidad
        tabla_width * 0.15,  # Base
        tabla_width * 0.15,  # IVA
        tabla_width * 0.15   # Total
    ]
    
    # Cabecera de la tabla
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.black)
    
    x_offset = tabla_x
    c.drawString(x_offset + 2*mm, y_pos, "Producto")
    x_offset += col_widths[0]
    c.drawCentredString(x_offset + col_widths[1]/2, y_pos, "Cantidad")
    x_offset += col_widths[1]
    c.drawRightString(x_offset + col_widths[2] - 2*mm, y_pos, "Base")
    x_offset += col_widths[2]
    c.drawRightString(x_offset + col_widths[3] - 2*mm, y_pos, "IVA")
    x_offset += col_widths[3]
    c.drawRightString(x_offset + col_widths[4] - 2*mm, y_pos, "Total")
    
    # Línea debajo de cabecera
    y_pos -= 4*mm
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(tabla_x, y_pos, tabla_x + tabla_width, y_pos)
    
    # Dibujar filas de productos
    y_pos -= 8*mm
    c.setFont("Helvetica", 9)
    
    # Calcular totales
    subtotal_acumulado = 0
    iva_acumulado = 0
    total_acumulado = 0
    
    for item in items_raw:
        concepto = item['producto']
        cantidad = item['cantidad']
        precio_base = item['base'] / cantidad  # Precio unitario sin IVA
        
        x_offset = tabla_x
        c.drawString(x_offset + 2*mm, y_pos, concepto[:50])
        
        x_offset += col_widths[0]
        c.drawCentredString(x_offset + col_widths[1]/2, y_pos, str(cantidad))
        
        x_offset += col_widths[1]
        c.drawRightString(x_offset + col_widths[2] - 2*mm, y_pos, f"{precio_base:.2f} €")
        
        x_offset += col_widths[2]
        iva_item = precio_base * IVA
        c.drawRightString(x_offset + col_widths[3] - 2*mm, y_pos, f"{iva_item:.2f} €")
        
        x_offset += col_widths[3]
        total_item = item['total']
        c.drawRightString(x_offset + col_widths[4] - 2*mm, y_pos, f"{total_item:.2f} €")
        
        # Acumular totales
        subtotal_acumulado += item['base']
        iva_acumulado += item['iva']
        total_acumulado += item['total']
        
        # Línea separadora fina
        y_pos -= 4*mm
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.3)
        c.line(tabla_x, y_pos, tabla_x + tabla_width, y_pos)
        y_pos -= 4*mm
    
    # Línea final de tabla
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(tabla_x, y_pos + 4*mm, tabla_x + tabla_width, y_pos + 4*mm)
    
    # ===== TOTALES (PARTE INFERIOR DERECHA) =====
    y_pos -= 10*mm
    totales_x = width - 65*mm
    totales_label_x = totales_x - 35*mm
    
    c.setFont("Helvetica", 9)
    
    # Base Imponible
    c.drawString(totales_label_x, y_pos, "Base Imponible")
    c.drawRightString(totales_x + 40*mm, y_pos, f"{subtotal_acumulado:.2f} €")
    
    # IVA
    y_pos -= 6*mm
    c.drawString(totales_label_x, y_pos, "IVA")
    c.drawCentredString(totales_x + 10*mm, y_pos, "10%")
    c.drawRightString(totales_x + 40*mm, y_pos, f"{iva_acumulado:.2f} €")
    
    # Línea antes del total
    y_pos -= 4*mm
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(totales_label_x, y_pos, totales_x + 40*mm, y_pos)
    
    # Total
    y_pos -= 7*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(totales_label_x, y_pos, "Total")
    c.drawRightString(totales_x + 40*mm, y_pos, f"{total_acumulado:.2f} €")
    
    # Guardar PDF
    c.save()
    
    return ruta_archivo


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'pdf-generator-flores-loli',
        'empresa': DATOS_EMPRESA['nombre'],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/generar-factura', methods=['POST'])
def generar_factura():
    """
    Endpoint principal para generar facturas
    
    Formato esperado (compatible con tu estructura):
    {
      "numero": "2025-001",
      "fecha": "22/12/2025",
      "cliente": {
        "nombre": "Juan Pérez"
      },
      "items": [
        {
          "producto": "Ramo de rosas",
          "cantidad": 2,
          "base": 60.00,
          "iva": 6.00,
          "total": 66.00
        }
      ]
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['numero', 'fecha', 'cliente', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Campo requerido faltante: {field}'
                }), 400
        
        # Validar items
        if not data['items'] or len(data['items']) == 0:
            return jsonify({
                'error': 'Debe haber al menos un item en la factura'
            }), 400
        
        if len(data['items']) > 10:
            return jsonify({
                'error': 'Máximo 10 productos por factura'
            }), 400
        
        # Extraer datos
        numero = data['numero']
        fecha = data['fecha']
        cliente_nombre = data['cliente']['nombre']
        items = data['items']
        
        # Generar PDF
        archivo = generar_factura_pdf(
            numero, 
            fecha, 
            cliente_nombre, 
            items,
            INVOICES_DIR
        )
        
        # Calcular totales para la respuesta
        subtotal = sum(item['base'] for item in items)
        iva_total = sum(item['iva'] for item in items)
        total = sum(item['total'] for item in items)
        
        return jsonify({
            'success': True,
            'message': 'Factura generada correctamente',
            'factura': {
                'numero': numero,
                'filename': os.path.basename(archivo),
                'path': archivo,
                'cliente': cliente_nombre,
                'fecha': fecha,
                'subtotal': round(subtotal, 2),
                'iva': round(iva_total, 2),
                'total': round(total, 2),
                'num_items': len(items)
            },
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Error al generar la factura',
            'details': str(e)
        }), 500


@app.route('/facturas', methods=['GET'])
def listar_facturas():
    """Endpoint para listar todas las facturas generadas"""
    try:
        facturas = []
        for filename in sorted(os.listdir(INVOICES_DIR), reverse=True):
            if filename.endswith('.pdf'):
                filepath = os.path.join(INVOICES_DIR, filename)
                stat = os.stat(filepath)
                facturas.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / 1024 / 1024, 2),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        return jsonify({
            'success': True,
            'empresa': DATOS_EMPRESA['nombre'],
            'count': len(facturas),
            'facturas': facturas
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Error al listar facturas',
            'details': str(e)
        }), 500


@app.route('/factura/<filename>', methods=['GET'])
def descargar_factura(filename):
    """Endpoint para descargar una factura específica"""
    try:
        filepath = os.path.join(INVOICES_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({
                'error': 'Factura no encontrada'
            }), 404
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'error': 'Error al descargar la factura',
            'details': str(e)
        }), 500


@app.route('/info', methods=['GET'])
def info_empresa():
    """Endpoint con información de la empresa"""
    return jsonify({
        'empresa': DATOS_EMPRESA,
        'iva': f"{IVA * 100}%",
        'max_productos': 10,
        'formatos_aceptados': {
            'fecha': 'DD/MM/YYYY',
            'numero': 'Texto libre (ej: 2025-001)',
            'precios': 'Números con 2 decimales'
        }
    })


if __name__ == '__main__':
    print("🌸 Iniciando servicio de generación de PDFs - FLORES Y PLANTAS LOLI")
    print(f"📁 Directorio de facturas: {INVOICES_DIR}")
    print(f"🏢 Empresa: {DATOS_EMPRESA['nombre']}")
    print(f"📞 Teléfono: {DATOS_EMPRESA['telefono']}")
    print(f"📧 Email: {DATOS_EMPRESA['email']}")
    print(f"📊 IVA: {IVA * 100}%")
    app.run(host='0.0.0.0', port=5000, debug=True)