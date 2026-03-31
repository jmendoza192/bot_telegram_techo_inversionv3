"""
🏠 Bot Calculadora Inmobiliaria CLOU v3.Final
Plataforma: Telegram
Versión personalizada para Jancarlo Inmobiliario
Desarrollador: Jan
"""

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ConversationHandler, ContextTypes
)
import logging
import os

# ==========================================
# CONFIGURACIÓN
# ==========================================
TOKEN_TELEGRAM = os.getenv('TOKEN_TELEGRAM', 'TU_TOKEN_AQUI')

# Estados de la conversación (4 preguntas)
INGRESO, PRESTAMOS, TARJETAS, AHORROS = range(4)

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================================
# FUNCIONES DE CÁLCULO
# ==========================================

def calcular_auditoria_360(datos):
    """Calcula la capacidad de inversión inmobiliaria sin decimales."""
    
    # Cálculos
    capacidad_40 = datos['ingreso'] * 0.40
    deudas_totales = datos['prestamos'] + datos['tarjetas']
    cuota_hipotecaria = capacidad_40 - deudas_totales
    
    # Validar que la cuota sea positiva
    if cuota_hipotecaria < 0:
        cuota_hipotecaria = 0
    
    # Factor financiero: TEA 9%, 20 años = 111.14
    prestamo_max = cuota_hipotecaria * 111.14
    
    # AFP: Monto fijo disponible para primera vivienda
    afp = 30000
    inicial_total = datos['ahorros'] + afp
    
    # Escenarios de inversión
    escenario_1 = prestamo_max + inicial_total + 7300 + 5500  # BBP + Bono Verde
    escenario_2 = prestamo_max + inicial_total + 7300          # BBP
    escenario_3 = prestamo_max + inicial_total                 # Sin Bonos
    
    return {
        "cuota": int(round(cuota_hipotecaria)),
        "prestamo": int(round(prestamo_max)),
        "afp": afp,
        "inicial": int(round(inicial_total)),
        "escenario_1": int(round(escenario_1)),
        "escenario_2": int(round(escenario_2)),
        "escenario_3": int(round(escenario_3))
    }

def formato_moneda(numero):
    """Convierte número a formato S/ X.XXX con puntos como separadores de miles."""
    return f"S/ {numero:,}".replace(",", ".")

# ==========================================
# MANEJADORES DE CONVERSACIÓN
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia la conversación con 4 mensajes iniciales."""
    
    # MENSAJE 1: Bienvenida
    await update.message.reply_text(
        "👋 ¡Hola! Soy el asistente virtual de Jancarlo Inmobiliario.",
        parse_mode='Markdown'
    )
    
    # MENSAJE 2: Imagen sin texto
    url_imagen = "https://postimg.cc/T59N63cL"
    try:
        await update.message.reply_photo(photo=url_imagen)
    except:
        pass
    
    # MENSAJE 3: Propósito
    await update.message.reply_text(
        "Mi meta es que encuentres un depa que puedas pagar con total tranquilidad. "
        "Con *4 preguntas simples*, haremos un diagnóstico rápido siguiendo los *parámetros de los bancos*.\n\n"
        "Esto nos permitirá saber tu techo de inversión seguro, protegiendo tus ahorros y tu estabilidad.\n\n"
        "*¿Empezamos?*",
        parse_mode='Markdown'
    )
    
    # MENSAJE 4: Primera pregunta
    await update.message.reply_text(
        "📊 *Pregunta 1:* ¿Cuál es la suma de *Ingresos Netos Mensuales* en tu hogar?\n"
        "(Suma de sueldos después de descuentos, en Soles)",
        parse_mode='Markdown'
    )
    
    return INGRESO

async def obtener_ingreso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura el ingreso neto mensual."""
    try:
        ingreso = float(update.message.text.replace(",", "."))
        if ingreso < 0:
            await update.message.reply_text("❌ Por favor ingresa un monto positivo.")
            return INGRESO
        
        context.user_data['ingreso'] = ingreso
        
        # MENSAJE 5
        await update.message.reply_text(
            f"✅ Ingreso registrado: {formato_moneda(int(ingreso))}",
            parse_mode='Markdown'
        )
        
        # MENSAJE 6
        await update.message.reply_text(
            "*💳 Pregunta 2:* ¿Cuánto pagas mensualmente en total por *Préstamos Personales, de Estudios o Vehiculares*?\n"
            "(Suma los tres. Si no tienes, escribe 0)",
            parse_mode='Markdown'
        )
        return PRESTAMOS
        
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor ingresa un número válido."
        )
        return INGRESO

async def obtener_prestamos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura préstamos personales + vehiculares combinados."""
    try:
        prestamos = float(update.message.text.replace(",", "."))
        if prestamos < 0:
            await update.message.reply_text("❌ Por favor ingresa un monto positivo.")
            return PRESTAMOS
        
        context.user_data['prestamos'] = prestamos
        
        # MENSAJE 7
        await update.message.reply_text(
            f"✅ Préstamos registrados: {formato_moneda(int(prestamos))}",
            parse_mode='Markdown'
        )
        
        # MENSAJE 8
        await update.message.reply_text(
            "*🛒 Pregunta 3:* ¿Cuáles son tus *cuotas fijas de Tarjetas de crédito*?\n"
            "(Viajes, electrodomésticos, etc. Si pagas todo a fin de mes, coloca 0)",
            parse_mode='Markdown'
        )
        return TARJETAS
        
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor ingresa un número válido."
        )
        return PRESTAMOS

async def obtener_tarjetas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura las cuotas fijas de tarjeta de crédito."""
    try:
        tarjetas = float(update.message.text.replace(",", "."))
        if tarjetas < 0:
            await update.message.reply_text("❌ Por favor ingresa un monto positivo.")
            return TARJETAS
        
        context.user_data['tarjetas'] = tarjetas
        
        # MENSAJE 9
        await update.message.reply_text(
            f"✅ Cuotas de Tarjeta registradas: {formato_moneda(int(tarjetas))}",
            parse_mode='Markdown'
        )
        
        # MENSAJE 10
        await update.message.reply_text(
            "*💰 Pregunta 4 (última):* ¿Cuánto tienes de *Ahorros Propios*?\n"
            "(Capital inicial disponible, en Soles)",
            parse_mode='Markdown'
        )
        return AHORROS
        
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor ingresa un número válido."
        )
        return TARJETAS

async def obtener_ahorros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura los ahorros y calcula el resultado final."""
    try:
        ahorros = float(update.message.text.replace(",", "."))
        if ahorros < 0:
            await update.message.reply_text("❌ Por favor ingresa un monto positivo.")
            return AHORROS
        
        context.user_data['ahorros'] = ahorros
        
        # Calcular auditoría
        resultado = calcular_auditoria_360(context.user_data)
        
        # MENSAJE 11: Resultado - PARTE 1 (Solo Datos)
        respuesta_parte1 = (
            f"📌 *RESULTADO DE TU TECHO DE INVERSIÓN*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• Cuota para tu depa: *{formato_moneda(resultado['cuota'])}*\n"
            f"• Préstamo del Banco: *{formato_moneda(resultado['prestamo'])}*\n"
            f"• Ahorros Propios: *{formato_moneda(int(ahorros))}*\n"
            f"• Tu AFP (25% ingreso): *{formato_moneda(resultado['afp'])}*\n"
            f"• Tu Inicial Total: *{formato_moneda(resultado['inicial'])}*"
        )
        
        await update.message.reply_text(respuesta_parte1, parse_mode='Markdown')
        
        # MENSAJE 12: Resultado - PARTE 2 (Escenarios)
        respuesta_parte2 = (
            f"🏢 *TU TECHO DE INVERSIÓN SEGÚN PROYECTO:*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"1️⃣ *Depa Eco-Sostenible (BBP + Bono Verde)*\n"
            f"🔥 *{formato_moneda(resultado['escenario_1'])}*\n"
            f"✨ ganaste +S/ 12.800 en beneficios estatales\n\n"
            f"2️⃣ *Depa Tradicional (BBP sin Bono Verde)*\n"
            f"📍 *{formato_moneda(resultado['escenario_2'])}*\n"
            f"✨ ganaste +S/ 7.300 en bonificación\n\n"
            f"3️⃣ *Inversión Directa (Sin Bonos)*\n"
            f"📉 *{formato_moneda(resultado['escenario_3'])}*"
        )
        
        await update.message.reply_text(respuesta_parte2, parse_mode='Markdown')
        
        # MENSAJE 13: Reglas de oro
        await update.message.reply_text(
            "⚠️ *REGLAS DE ORO:*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Si compras un proyecto Mi Vivienda, puedes comprar un depa *S/ 12.800 más caro* gracias a los subsidios del Estado.\n\n"
            "💡 Si cancelas tus cuotas de tarjeta o préstamos antes de calificar, el precio máximo de tu depa *subirá automáticamente*.\n\n"
            "💡 El cálculo contempla un margen del 3% para *gastos notariales y registrales*.",
            parse_mode='Markdown'
        )
        
        # MENSAJE 14: Información referencial
        await update.message.reply_text(
            "ℹ️ Este dato es referencial y lo puedes usar como un 1er acercamiento. "
            "Si deseas conocer tu techo de inversión exacto, entonces necesitas una asesoría personalizada. "
            "📞 Puedes agendarla al Whatsapp 📲 920605559 o al siguiente link:",
            parse_mode='Markdown'
        )
        
        # MENSAJE 15: Link de WhatsApp
        await update.message.reply_text(
            "https://wa.link/ee1ojv"
        )
        
        # MENSAJE 16: Opción de nuevo cálculo
        await update.message.reply_text(
            "¿Deseas hacer otro cálculo? Escribe /start"
        )
        
        # Limpiar datos del usuario
        context.user_data.clear()
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor ingresa un número válido."
        )
        return AHORROS

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación."""
    await update.message.reply_text(
        "❌ Operación cancelada.\n\nEscribe /start para comenzar de nuevo.",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la ayuda."""
    await update.message.reply_text(
        "🆘 *AYUDA - Bot CLOU*\n\n"
        "*Comandos disponibles:*\n"
        "/start - Iniciar nuevo cálculo\n"
        "/ayuda - Ver esta ayuda\n"
        "/info - Información sobre el bot",
        parse_mode='Markdown'
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra información del bot."""
    await update.message.reply_text(
        "ℹ️ *INFORMACIÓN DEL BOT*\n\n"
        "*Bot:* Calculadora Inmobiliaria CLOU v.Final\n"
        "*Desarrollador:* Jancarlo Inmobiliario\n"
        "*Plataforma:* Telegram\n\n"
        "*Parámetros:*\n"
        "• Capacidad de endeudamiento: 40% del ingreso\n"
        "• TEA: 9% anual\n"
        "• Plazo: 20 años\n"
        "• AFP disponible: S/ 30.000 fijos\n\n"
        "*Bonificaciones:*\n"
        "• Bono del Buen Pagador: S/ 7.300\n"
        "• Bono Verde: S/ 5.500",
        parse_mode='Markdown'
    )

# ==========================================
# MAIN - Inicializar Bot
# ==========================================

def main():
    """Inicia el bot."""
    
    if TOKEN_TELEGRAM == 'TU_TOKEN_AQUI':
        logger.error("❌ ERROR: Debes configurar tu TOKEN_TELEGRAM")
        return
    
    application = Application.builder().token(TOKEN_TELEGRAM).build()
    
    # Manejador de conversación
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INGRESO: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_ingreso)],
            PRESTAMOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_prestamos)],
            TARJETAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_tarjetas)],
            AHORROS: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_ahorros)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('ayuda', ayuda))
    application.add_handler(CommandHandler('info', info))
    
    logger.info("🚀 Bot CLOU iniciado correctamente")
    application.run_polling()

if __name__ == '__main__':
    main()
