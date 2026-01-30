import streamlit as st
import pandas as pd
import numpy as np
import json
import os

st.set_page_config(page_title="Análisis Técnico Investing.com Style", layout="wide")

# ==================== CSS PERSONALIZADO ====================
css_investing = """
<style>
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

/* Contenedor principal */
.container-main {
    padding: 20px;
    background-color: #f8f9fa;
}

/* Resumen General */
.summary-box {
    padding: 24px;
    border-radius: 8px;
    margin-bottom: 20px;
    border-left: 4px solid;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.summary-box.strong-buy {
    background-color: #e8f5e9;
    border-left-color: #00aa00;
}

.summary-box.buy {
    background-color: #f1f8e9;
    border-left-color: #66ff66;
}

.summary-box.hold {
    background-color: #fff8e1;
    border-left-color: #ffc107;
}

.summary-box.sell {
    background-color: #ffebee;
    border-left-color: #ff5252;
}

.summary-box.strong-sell {
    background-color: #ffebee;
    border-left-color: #dd0000;
}

.summary-verdict {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 16px;
}

.summary-periods {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 16px;
}

.period-badge {
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
}

.period-badge.strong-buy { background-color: #00aa00; color: white; }
.period-badge.buy { background-color: #66ff66; color: black; }
.period-badge.hold { background-color: #cccccc; color: black; }
.period-badge.sell { background-color: #ff9999; color: black; }
.period-badge.strong-sell { background-color: #dd0000; color: white; }

/* Tablas de Indicadores */
.indicator-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}

.indicator-table thead {
    border-bottom: 2px solid #e0e0e0;
}

.indicator-table th {
    padding: 12px 8px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    color: #666;
    text-transform: uppercase;
}

.indicator-table td {
    padding: 14px 8px;
    border-bottom: 1px solid #f0f0f0;
}

.indicator-value {
    font-weight: 700;
    font-size: 14px;
}

.indicator-label {
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}

.indicator-label.positive { background-color: #e8f5e9; color: #00aa00; }
.indicator-label.negative { background-color: #ffebee; color: #dd0000; }
.indicator-label.neutral { background-color: #f5f5f5; color: #666; }

/* Sección de Medias Móviles */
.sma-section {
    background-color: white;
    padding: 16px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
}

.sma-row {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
}

.sma-row:last-child {
    border-bottom: none;
}

.sma-label {
    font-weight: 600;
    font-size: 13px;
    min-width: 100px;
    color: #333;
}

.sma-values {
    display: flex;
    gap: 16px;
    flex: 1;
    align-items: center;
}

.sma-value {
    font-weight: 700;
    font-size: 13px;
}

.sma-status {
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
}

.sma-status.above { background-color: #e8f5e9; color: #00aa00; }
.sma-status.below { background-color: #ffebee; color: #dd0000; }

/* Target de Precio */
.target-section {
    background-color: white;
    padding: 16px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    margin-bottom: 20px;
}

.target-header {
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 12px;
    color: #333;
}

.target-bar-container {
    position: relative;
    height: 40px;
    background-color: #f5f5f5;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
}

.target-bar {
    height: 100%;
    transition: width 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 8px;
    color: white;
    font-weight: 600;
    font-size: 12px;
}

.target-bar.positive { background-color: #00aa00; }
.target-bar.negative { background-color: #dd0000; }

.target-labels {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #666;
    margin-top: 4px;
}

/* Sección de Precios */
.price-info {
    background-color: white;
    padding: 16px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    margin-bottom: 20px;
}

.price-current {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 12px;
}

.price-value {
    font-size: 28px;
    font-weight: 700;
}

.price-change {
    font-size: 16px;
    font-weight: 600;
}

.price-change.positive { color: #00aa00; }
.price-change.negative { color: #dd0000; }

/* Caja de información */
.info-box {
    background-color: #f5f5f5;
    padding: 12px;
    border-radius: 4px;
    font-size: 12px;
    color: #666;
    margin-bottom: 16px;
}

/* Encabezado de secciones */
.section-title {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 16px;
    color: #333;
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 8px;
}

@media (prefers-color-scheme: dark) {
    .container-main { background-color: #1a1a1a; }
    .sma-section, .target-section, .price-info { background-color: #2d2d2d; border-color: #444; }
    .sma-label, .target-header, .section-title { color: #e0e0e0; }
    .sma-value, .price-value { color: #ffffff; }
    .indicator-label.neutral { background-color: #444; color: #aaa; }
    .info-box { background-color: #3a3a3a; color: #aaa; }
    
    /* Highlight Argentino Dark Mode - Professional */
    .arg-highlight {
        border-left: 4px solid #ffd700 !important;
        padding-left: 10px !important;
        border-radius: 0 !important;
        background: linear-gradient(90deg, rgba(255, 215, 0, 0.1) 0%, rgba(0,0,0,0) 100%) !important;
    }
}

/* Highlight Argentino Light Mode - Professional */
.arg-highlight {
    border-left: 4px solid #b8860b !important;
    padding-left: 10px !important;
    border-radius: 0 !important;
    background: linear-gradient(90deg, rgba(255, 215, 0, 0.15) 0%, rgba(255,255,255,0) 100%) !important;
}
</style>
<style>
/* Estilos para Rangos (Day/52w) */
.range-section {
    margin-top: 16px;
    margin-bottom: 12px;
}
.range-header {
    font-size: 12px;
    font-weight: 600;
    color: #666;
    margin-bottom: 6px;
}
.range-bar-bg {
    position: relative;
    height: 6px;
    background-color: #e0e0e0;
    border-radius: 3px;
    width: 100%;
    margin-bottom: 4px;
}
.range-marker {
    position: absolute;
    top: -4px;
    width: 4px;
    height: 14px;
    background-color: #333;
    border: 1px solid white;
    transform: translateX(-50%);
}
.range-values-row {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #333;
    font-weight: 600;
}
@media (prefers-color-scheme: dark) {
    .range-bar-bg { background-color: #444; }
    .range-marker { background-color: #fff; border-color: #333; }
    .range-values-row, .range-header { color: #ccc; }
}
/* ================= STATUS COLORS (STANDARD TRAFFIC LIGHT) ================= */
/* Matching the screenshot: Standard Green/Red, Light Green/Red variants */

/* Strong Buy - Standard Green */
td.strong-buy { 
    background-color: #008000 !important; /* Standard HTML Green */
    color: #ffffff !important; 
    font-weight: 700 !important;
}
/* Buy - Light Green */
td.buy { 
    background-color: #90EE90 !important; /* LightGreen */
    color: #000000 !important; /* Black Text */
    font-weight: 600 !important;
}
/* Strong Sell - Standard Red */
td.strong-sell { 
    background-color: #FF0000 !important; /* Standard HTML Red */
    color: #ffffff !important; 
    font-weight: 700 !important;
}
/* Sell - Light Red / Salmon */
td.sell { 
    background-color: #FA8072 !important; /* Salmon to match Pinkish Red */
    color: #000000 !important; /* Black Text */
    font-weight: 600 !important;
}
/* Hold - Light Grey */
td.hold, td.neutral { 
    background-color: #D3D3D3 !important; /* LightGray */
    color: #000000 !important; 
}

/* Base Table Styling - Readability Fix */
.dataframe {
    font-size: 1rem !important; /* Restored to normal size */
    font-family: 'Roboto', sans-serif !important; 
}
.dataframe td, .dataframe th {
    padding: 10px 12px !important; /* Increased padding */
    vertical-align: middle !important;
    text-align: center !important;
    border: 1px solid #444 !important; /* Clean borders */
}

/* TEXT ONLY COLORS */
.positivo { color: #008000 !important; font-weight: bold; }
.negativo { color: #FF0000 !important; font-weight: bold; }

/* Highlight Argentino */
.arg-highlight {
    border-left: 4px solid #FFD600 !important;
    background: linear-gradient(90deg, rgba(255, 214, 0, 0.15) 0%, rgba(0,0,0,0) 100%) !important;
    color: #e6edf3 !important; 
    font-weight: 600 !important;
}

@media (prefers-color-scheme: light) {
    .dataframe tbody td, table tbody td { color: #24292f !important; }
    .arg-highlight { color: #000 !important; }
}
</style>
"""

st.markdown(css_investing, unsafe_allow_html=True)

# ==================== INVESTING URLS ====================
from utils_links import get_investing_url

# Definición de Acciones Argentinas (ADRs + Locales)
ARGENTINE_ADRS = {
    'YPF', 'MELI', 'GLOB', 'VIST', 'PAM', 'LOMA', 'CEPU', 'BIOX',
    'TEO', 'CRESY', 'IRS', 'EDN', 'GGAL', 'BMA'
}

def is_argentine_stock(ticker):
    """Retorna True si es una acción argentina (BA o ADR)"""
    if str(ticker).endswith('.BA'):
        return True
    if ticker in ARGENTINE_ADRS:
        return True
    return False

# ==================== BOTÓN DE ACTUALIZAR DATOS EN SIDEBAR ====================
with st.sidebar:
    st.markdown("---")
    st.subheader("🔄 Datos")
    
    def actualizar_datos_backend():
        try:
            import importlib
            import analisis_profesional
            importlib.reload(analisis_profesional)
            
            # Elementos visuales de progreso
            progreso_bar = st.progress(0)
            progreso_text = st.empty()
            
            def callback_progreso(actual, total, ticker):
                progreso_bar.progress(actual / total)
                progreso_text.text(f"⏳ Analizando: {ticker} ({actual}/{total})")
            
            analisis_profesional.main(progress_callback=callback_progreso)
            
            # Limpiar al terminar
            progreso_bar.empty()
            progreso_text.empty()
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return False

    if st.button("🔄 Actualizar Datos", key='update_data', use_container_width=True):
        with st.spinner('⏳ Descargando datos y actualizando análisis... (Esto puede tardar 1-2 minutos)'):
            if actualizar_datos_backend():
                st.success("✅ Datos actualizados")
                st.rerun()

    st.markdown("---")
    st.subheader("⏱️ Auto-Actualización")
    intervalo_auto = st.selectbox("Intervalo:", ["Apagado", "1 min", "5 min", "10 min", "30 min"], index=0)
    
    should_auto_reload = False
    reload_seconds = 0
    timer_placeholder = st.empty()
    
    if intervalo_auto != "Apagado":
        import time
        import os
        mins = int(intervalo_auto.split()[0])
        reload_seconds = mins * 60
        should_auto_reload = True
        
        # Verificar antigüedad del archivo
        if os.path.exists('analisis_mercado.xlsx'):
            age = time.time() - os.path.getmtime('analisis_mercado.xlsx')
            if age > reload_seconds:
                with st.spinner('⚡ Auto-actualizando datos...'):
                    if actualizar_datos_backend():
                        st.rerun()
        
        st.caption(f"⚠️ La app se recargará cada {mins} min.")
    
    st.markdown("---")
    st.subheader("⚙️ Modo de Análisis")
    analysis_mode = st.radio(
        "Elige el modo de análisis técnico:",
        options=['aggressive', 'conservative'],
        format_func=lambda x: '🚀 Agresivo (Investing.com)' if x == 'aggressive' else '🛡️ Conservador',
        key='analysis_mode'
    )

    # Sidebar Notification Inbox
    st.sidebar.markdown("---")
    
    import os
    import json
    ALERTS_FILE = 'recent_alerts.json'

    # Cargar alertas primero para saber la cantidad
    alerts = []
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
        except:
            alerts = []

    badge_count = len(alerts)
    header_text = f"🔔 Notificaciones ({badge_count})" if badge_count > 0 else "🔔 Notificaciones"
    st.sidebar.subheader(header_text)
    
    if st.sidebar.button("🗑️ Limpiar", use_container_width=True):
        if os.path.exists(ALERTS_FILE):
            os.remove(ALERTS_FILE)
            st.rerun()

    if alerts:
        with st.sidebar.expander(f"Ver {badge_count} Alertas", expanded=False):
            for alert in alerts:
                # Icono segun tipo
                icon = "ℹ️"
                if alert.get('type_clean') == 'success': icon = "✅"
                elif alert.get('type_clean') == 'error': icon = "❌"
                elif alert.get('type_clean') == 'warning': icon = "⚠️"
                
                st.markdown(f"**{icon} {alert.get('ticker')}**")
                st.caption(f"{alert.get('action')} - ${alert.get('price')}")
                
                # Mostrar razón completa si existe, o fallback
                reason = alert.get('reason_full', alert.get('type_raw', ''))
                # Limpiar el nombre del tipo si está dentro de la razón (opcional/simple)
                st.caption(f"{reason}") 
                st.markdown("---")
    else:
        st.sidebar.caption("Sin nuevas notificaciones.")

    st.sidebar.markdown("---")
    
    # SECCIÓN: CONFIGURACIÓN DE EMAILS (Movido arriba para mayor estabilidad)
    with st.sidebar.expander("📧 Destinatarios de Alertas", expanded=False):
        CONFIG_FILE = 'email_config.json'
        # Función para cargar config
        def load_email_config():
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, 'r') as f:
                        return json.load(f)
                except:
                    pass
            return {"recipients": ["lchipasco@gmail.com"]}
        # Función para guardar config
        def save_email_config(config):
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        email_config = load_email_config()
        current_recipients = email_config.get("recipients", [])
        st.write("**Lista Actual:**")
        if not current_recipients:
            st.caption("No hay destinatarios.")
        else:
            for i, email in enumerate(current_recipients):
                c1, c2 = st.columns([0.8, 0.2])
                with c1: st.caption(email)
                with c2: 
                    if st.button("🗑️", key=f"del_cfg_{i}"):
                        current_recipients.pop(i)
                        save_email_config({"recipients": current_recipients})
                        st.rerun()
        new_mail = st.text_input("Nuevo Email:", key="new_mail_input")
        if st.button("➕ Agregar", key="btn_add_mail"):
            if "@" in new_mail and "." in new_mail:
                if new_mail not in current_recipients:
                    current_recipients.append(new_mail)
                    save_email_config({"recipients": current_recipients})
                    st.success("Agregado!")
                    st.rerun()
    st.sidebar.markdown("---")


st.title("🛡️ Análisis de Stocks CH")
# st.markdown("Análisis detallado por ticker con Technical Summary") # Subtitulo eliminado
st.markdown("---")

def get_period_suggestion(rsi, cambio, macd=None, macd_signal=None, precio=None, sma50=None, sma200=None):
    """Lógica AGRESIVA mejorada, más alineada con Investing.com"""
    
    # Si no hay datos suficientes, es Hold
    if np.isnan(rsi) and np.isnan(cambio):
        return "Hold"

    buy_score = 0
    sell_score = 0

    # 1. Medias Móviles (Tendencia - MUY IMPORTANTE)
    if not np.isnan(precio) and not np.isnan(sma50):
        if precio < sma50:
            sell_score += 3  # Tendencia bajista (Peso alto)
        else:
            buy_score += 3

    if not np.isnan(precio) and not np.isnan(sma200):
        if precio < sma200:
            sell_score += 2  # Tendencia largo plazo
        else:
            buy_score += 2
    
    # Golden/Death Cross
    if not np.isnan(sma50) and not np.isnan(sma200):
        if sma50 < sma200:
            sell_score += 1 # Confirmación de tendencia bajista
        else:
            buy_score += 1

    # 2. Osciladores (RSI - Momentum/Tendencia)
    # Investing: RSI > 50 es Buy, RSI < 50 es Sell
    if not np.isnan(rsi):
        if rsi < 50:
            sell_score += 2
            if rsi < 30: sell_score += 1 # Fuerte momentum bajista
        else:
            buy_score += 2
            if rsi > 70: buy_score += 1 # Fuerte momentum alcista

    # 3. Momentum (MACD)
    if not np.isnan(macd) and not np.isnan(macd_signal):
        if macd < macd_signal:
            sell_score += 2  # Cruce bajista
        else:
            buy_score += 2   # Cruce alcista

    # 4. Cambio de precio (Momentum inmediato)
    if not np.isnan(cambio):
        if cambio < 0:
            sell_score += 1
            if cambio < -2: sell_score += 1
        else:
            buy_score += 1
            if cambio > 2: buy_score += 1

    # Decisión final basada en la diferencia de puntajes
    diff = buy_score - sell_score
    
    if diff >= 6:
        return "Strong Buy"
    elif diff >= 2:
        return "Buy"
    elif diff <= -6:
        return "Strong Sell"
    elif diff <= -2:
        return "Sell"
    else:
        return "Hold"

def get_period_suggestion_conservative(rsi, cambio, macd=None, macd_signal=None, precio=None, sma50=None, sma200=None):
    """Lógica CONSERVADORA - Requiere confirmaciones fuertes"""
    momentum_signal = 0
    
    if not np.isnan(cambio):
        # Umbrales más altos para considerar movimiento significativo
        if cambio > 7:
            momentum_signal = 3
        elif cambio > 5:
            momentum_signal = 2
        elif cambio > 2.5:
            momentum_signal = 1.5
        elif cambio > 1:
            momentum_signal = 0.5
        elif cambio < -7:
            momentum_signal = -3
        elif cambio < -5:
            momentum_signal = -2
        elif cambio < -2.5:
            momentum_signal = -1.5
        elif cambio < -1:
            momentum_signal = -0.5
        else:
            momentum_signal = 0
    
    rsi_confirmation = 0
    
    # Más conservador: requiere RSI más extremo
    if momentum_signal > 0 and not np.isnan(rsi):
        if rsi > 75:
            rsi_confirmation = 2
        elif rsi > 65:
            rsi_confirmation = 1.5
        elif rsi > 55:
            rsi_confirmation = 1
        elif rsi > 40:
            rsi_confirmation = 0.5
            
    elif momentum_signal < 0 and not np.isnan(rsi):
        if rsi < 25:
            rsi_confirmation = 2
        elif rsi < 35:
            rsi_confirmation = 1.5
        elif rsi < 45:
            rsi_confirmation = 1
        elif rsi < 60:
            rsi_confirmation = 0.5
    
    total_signal = momentum_signal + rsi_confirmation
    
    # Thresholds más altos para ser conservador
    if total_signal >= 4.5:
        return "Strong Buy"
    elif total_signal >= 2.5:
        return "Buy"
    elif total_signal <= -4.5:
        return "Strong Sell"
    elif total_signal <= -2.5:
        return "Sell"
    else:
        return "Hold"

def get_suggestions_by_period(row, mode='aggressive'):
    """Retorna sugerencias para CADA período"""
    rsi_1d = pd.to_numeric(row.get('RSI 1d', np.nan), errors='coerce')
    rsi_1w = pd.to_numeric(row.get('RSI 1w', np.nan), errors='coerce')
    rsi_1m = pd.to_numeric(row.get('RSI 1m', np.nan), errors='coerce')
    cambio_dia = pd.to_numeric(row.get('Cambio % (día)', np.nan), errors='coerce')
    cambio_sem = pd.to_numeric(row.get('Cambio % (semana)', np.nan), errors='coerce')
    cambio_mes = pd.to_numeric(row.get('Cambio % (mes)', np.nan), errors='coerce')
    macd = pd.to_numeric(row.get('MACD', np.nan), errors='coerce')
    macd_signal = pd.to_numeric(row.get('MACD Signal', np.nan), errors='coerce')
    precio = pd.to_numeric(row.get('Precio', np.nan), errors='coerce')
    sma50 = pd.to_numeric(row.get('SMA 50', np.nan), errors='coerce')
    sma200 = pd.to_numeric(row.get('SMA 200', np.nan), errors='coerce')
    
    # Elegir función según modo
    func = get_period_suggestion if mode == 'aggressive' else get_period_suggestion_conservative
    
    return {
        'Hourly': func(rsi_1d, cambio_dia, macd, macd_signal, precio, sma50, sma200),
        'Daily': func(rsi_1d, cambio_dia, macd, macd_signal, precio, sma50, sma200),
        'Weekly': func(rsi_1w, cambio_sem, macd, macd_signal, precio, sma50, sma200),
        'Monthly': func(rsi_1m, cambio_mes, macd, macd_signal, precio, sma50, sma200)
    }

def get_rsi_tooltip(rsi_value, period="1D"):
    """Genera tooltip dinámico según valor actual de RSI"""
    if rsi_value < 30:
        return (
            "🟢 **SOBREVENDIDO**\n\n"
            f"Valor actual: {rsi_value:.0f}\n\n"
            "El activo está debajo de su equilibrio. "
            "Señal de posible COMPRA. El precio puede recuperarse.\n\n"
            "✓ Esto es POSITIVO - Oportunidad de compra"
        )
    elif rsi_value < 50:
        return (
            "🟡 **DÉBIL**\n\n"
            f"Valor actual: {rsi_value:.0f}\n\n"
            "Hay más presión vendedora. El momentum es negativo.\n\n"
            "⚠️ Para mejorar: RSI debería superar 50\n"
            f"Faltan ~{50-rsi_value:.0f} puntos para neutral"
        )
    elif rsi_value < 70:
        return (
            "⚪ **NEUTRAL**\n\n"
            f"Valor actual: {rsi_value:.0f}\n\n"
            "El activo está en equilibrio. "
            "Ni sobrecomprado ni sobrevendido.\n\n"
            "✓ Esto es POSITIVO - Tendencia equilibrada"
        )
    else:
        return (
            "🔴 **SOBRECOMPRADO**\n\n"
            f"Valor actual: {rsi_value:.0f}\n\n"
            "El activo está por encima de su equilibrio. "
            "Señal de posible VENTA. Riesgo de caída.\n\n"
            "⚠️ Para mejorar: RSI debería bajar a ~50-70\n"
            f"Exceso de {rsi_value-70:.0f} puntos sobre límite"
        )

def get_macd_tooltip(macd_value):
    """Genera tooltip dinámico según valor actual de MACD"""
    if macd_value > 0:
        return (
            "🟢 **POSITIVO**\n\n"
            f"Valor actual: {macd_value:.2f}\n\n"
            "El MACD está por encima de su línea de señal. "
            "MOMENTUM ALCISTA. Hay impulso al alza.\n\n"
            "✓ Esto es POSITIVO - Señal de compra"
        )
    else:
        return (
            "🔴 **NEGATIVO**\n\n"
            f"Valor actual: {macd_value:.2f}\n\n"
            "El MACD está por debajo de su línea de señal. "
            "MOMENTUM BAJISTA. Hay impulso a la baja.\n\n"
            "⚠️ Para mejorar: MACD debería cruzar hacia 0+\n"
            f"Está {abs(macd_value):.2f} puntos en negativo"
        )

def get_sma_tooltip(precio, sma_value, sma_period):
    """Genera tooltip dinámico según relación precio/SMA"""
    if precio > sma_value:
        if sma_period == 50:
            diferencia = ((precio - sma_value) / sma_value) * 100
            return (
                "🟢 **COMPRA**\n\n"
                f"Precio: ${precio:.2f}\n"
                f"SMA 50: ${sma_value:.2f}\n"
                f"Diferencia: +{diferencia:.1f}%\n\n"
                "Tendencia ALCISTA A CORTO PLAZO. "
                "El precio está por encima del promedio. Señal positiva.\n\n"
                "✓ Esto es POSITIVO - Compra recomendada"
            )
        else:
            diferencia = ((precio - sma_value) / sma_value) * 100
            return (
                "📈 **UPTREND**\n\n"
                f"Precio: ${precio:.2f}\n"
                f"SMA 200: ${sma_value:.2f}\n"
                f"Diferencia: +{diferencia:.1f}%\n\n"
                "Tendencia ALCISTA A LARGO PLAZO. Muy positivo. "
                "El precio está por encima del promedio de 200 días.\n\n"
                "✓ Esto es POSITIVO - Tendencia fuerte al alza"
            )
    else:
        if sma_period == 50:
            diferencia = ((sma_value - precio) / sma_value) * 100
            return (
                "🔴 **VENTA**\n\n"
                f"Precio: ${precio:.2f}\n"
                f"SMA 50: ${sma_value:.2f}\n"
                f"Diferencia: -{diferencia:.1f}%\n\n"
                "Tendencia BAJISTA A CORTO PLAZO. "
                "El precio está por debajo del promedio. Señal negativa.\n\n"
                f"⚠️ Para mejorar: Precio debe llegar a ${sma_value:.2f}"
            )
        else:
            diferencia = ((sma_value - precio) / sma_value) * 100
            return (
                "📉 **DOWNTREND**\n\n"
                f"Precio: ${precio:.2f}\n"
                f"SMA 200: ${sma_value:.2f}\n"
                f"Diferencia: -{diferencia:.1f}%\n\n"
                "Tendencia BAJISTA A LARGO PLAZO. Muy negativo. "
                "El precio está por debajo del promedio de 200 días.\n\n"
                f"⚠️ Para mejorar: Precio debe llegar a ${sma_value:.2f}"
            )

@st.cache_data(ttl=300)
def cargar_datos(mode='aggressive'):
    """Carga datos del Excel"""
    df = pd.read_excel('analisis_mercado.xlsx')
    df.columns = df.columns.str.strip()
    
    suggestions_by_period = []
    for idx, row in df.iterrows():
        sug_dict = get_suggestions_by_period(row, mode=mode)
        suggestions_by_period.append(sug_dict)
    
    df['Hourly'] = [s['Hourly'] for s in suggestions_by_period]
    df['Daily'] = [s['Daily'] for s in suggestions_by_period]
    df['Weekly'] = [s['Weekly'] for s in suggestions_by_period]
    df['Monthly'] = [s['Monthly'] for s in suggestions_by_period]
    
    def get_overall(row):
        suggestions = [row['Hourly'], row['Daily'], row['Weekly'], row['Monthly']]
        buy_count = sum(1 for s in suggestions if 'Buy' in s)
        sell_count = sum(1 for s in suggestions if 'Sell' in s)
        
        if buy_count >= 3:
            return "Strong Buy" if row['Monthly'] in ['Strong Buy', 'Buy'] else "Buy"
        elif sell_count >= 3:
            return "Strong Sell" if row['Monthly'] in ['Strong Sell', 'Sell'] else "Sell"
        elif buy_count > sell_count:
            return "Buy"
        elif sell_count > buy_count:
            return "Sell"
        else:
            return "Hold"
    
    df['Overall'] = df.apply(get_overall, axis=1)
    
    def get_analyst_sentiment(row):
        """Sentimiento basado en Overall + RSI + Cambio"""
        overall = row.get('Overall', 'Hold')
        cambio_mes = pd.to_numeric(row.get('Cambio % (mes)', np.nan), errors='coerce')
        rsi_1m = pd.to_numeric(row.get('RSI 1m', np.nan), errors='coerce')
        
        # Si Overall es Strong Buy/Buy, Analyst Sentiment debería ser similar o más conservador
        if overall == "Strong Buy":
            return "Strong Buy"
        elif overall == "Buy":
            return "Buy"
        elif overall == "Strong Sell":
            return "Strong Sell"
        elif overall == "Sell":
            return "Sell"
        else:
            # Para Hold, revisar cambio y RSI
            if cambio_mes and cambio_mes > 20 and rsi_1m and rsi_1m < 70:
                return "Buy"
            elif cambio_mes and cambio_mes < -20:
                return "Sell"
            else:
                return "Hold"
    
    def get_price_target(row):
        """Target basado en volatilidad + RSI"""
        precio = pd.to_numeric(row.get('Precio', np.nan), errors='coerce')
        cambio_mes = pd.to_numeric(row.get('Cambio % (mes)', np.nan), errors='coerce')
        rsi_1m = pd.to_numeric(row.get('RSI 1m', np.nan), errors='coerce')
        
        if pd.isna(precio):
            return np.nan
        
        volatilidad = 0.30
        
        if rsi_1m and rsi_1m > 75:
            target = precio * (1 - volatilidad * 0.15)
        elif rsi_1m and rsi_1m < 25:
            target = precio * (1 + volatilidad * 0.10)
        elif cambio_mes and cambio_mes > 40:
            target = precio * (1 + min(cambio_mes / 100 * 0.4, 0.25))
        elif cambio_mes and cambio_mes > 20:
            target = precio * (1 + cambio_mes / 100 * 0.3)
        elif cambio_mes and cambio_mes < -30:
            target = precio * (1 - abs(cambio_mes) / 100 * 0.3)
        else:
            target = precio * (1 + (cambio_mes / 100 * 0.1 if cambio_mes else 0))
        
        return round(target, 2)
    
    def get_upside(precio, target):
        if pd.isna(precio) or pd.isna(target):
            return np.nan
        upside = ((target - precio) / precio) * 100
        return round(upside, 2)
    
    df['Analyst Sentiment'] = df.apply(get_analyst_sentiment, axis=1)
    df['Price Target'] = df.apply(get_price_target, axis=1)
    df['Upside %'] = df.apply(lambda row: get_upside(row['Precio'], row['Price Target']), axis=1)
    
    return df

try:
    df = cargar_datos(mode=analysis_mode)
    
    # Búsqueda robusta de columna de cambio día
    cols_cambio = [col for col in df.columns if 'Cambio' in col and ('día' in col or 'dia' in col)]
    col_cambio_dia = cols_cambio[0] if cols_cambio else 'Cambio % (día)'
    if col_cambio_dia not in df.columns:
        df[col_cambio_dia] = 0 # Fallback
    
    # ==================== SELECTOR DE TICKER EN TOP ====================
    st.markdown("### 🔍 Selecciona una acción para analizar")
    col1, col2, col3 = st.columns([2.8, 1.2, 1])
    with col1:
        ticker_sel = st.selectbox(
            'Elige una acción:',
            options=sorted(df['Ticker'].unique()),
            key='ticker_select',
            label_visibility='collapsed'
        )
    with col2:
        investing_url = get_investing_url(ticker_sel)
        st.markdown(
            f"""
            <div style="display: flex; gap: 8px; margin-top: 8px;">
                <a href="{investing_url}" target="_blank" style="
                    text-decoration: none;
                    color: #58a6ff;
                    font-weight: 500;
                    padding: 0.4rem 0.8rem;
                    border: 1px solid #30363d;
                    border-radius: 6px;
                    font-size: 13px;
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                ">📊 Investing</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        if st.button("🔄 Refrescar", key='refresh_btn', use_container_width=True):
            st.cache_data.clear()
    
    st.markdown("---")
    
    # ==================== SIDEBAR FILTROS ====================
    st.sidebar.header("🔧 Filtros para Tabla")
    
    # Favoritos
    st.sidebar.subheader("⭐ Mis Inversiones")
    
    # Persistencia de favoritos (Portafolios Múltiples)
    FAV_FILE = 'mis_inversiones.json'
    
    def cargar_favs_dict():
        """Carga el diccionario de portafolios, con migración si es necesario."""
        if os.path.exists(FAV_FILE):
            try:
                with open(FAV_FILE, 'r') as f:
                    data = json.load(f)
                # Migración: si es una lista (formato viejo), convertir a dict
                if isinstance(data, list):
                    return {"Mi Portafolio": data}
                return data
            except:
                return {"Mi Portafolio": []}
        return {"Mi Portafolio": []}
        
    def guardar_favs_dict(portafolios_dict):
        with open(FAV_FILE, 'w') as f:
            json.dump(portafolios_dict, f)

    # Cargar todos los portafolios
    all_portfolios = cargar_favs_dict()
    portfolio_names = list(all_portfolios.keys())

    # 1. Selector de Portafolio
    col_sel, col_del = st.sidebar.columns([0.8, 0.2])
    with col_sel:
        active_portfolio_name = st.selectbox(
            "Selecciona Portafolio:",
            options=portfolio_names,
            index=0,
            key='active_port_name'
        )
    with col_del:
        st.write("") # Espaciador
        if st.button("🗑️", key="del_port_btn", help="Eliminar este portafolio"):
            if len(portfolio_names) > 1:
                del all_portfolios[active_portfolio_name]
                guardar_favs_dict(all_portfolios)
                st.rerun()
            else:
                st.toast("⚠️ No puedes borrar el único portafolio")

    # 2. Agregar nuevo portafolio
    with st.sidebar.expander("➕ Nuevo Portafolio"):
        new_port_name = st.text_input("Nombre del portafolio:", key="new_port_input_name")
        if st.button("Crear", use_container_width=True):
            if new_port_name and new_port_name not in all_portfolios:
                all_portfolios[new_port_name] = []
                guardar_favs_dict(all_portfolios)
                st.rerun()

    # 3. Editar acciones del portafolio activo
    lista_tickers_all = sorted(df['Ticker'].unique())
    current_stocks = all_portfolios.get(active_portfolio_name, [])
    
    favoritos = st.sidebar.multiselect(
        f"Editar '{active_portfolio_name}':",
        options=lista_tickers_all,
        default=[t for t in current_stocks if t in lista_tickers_all],
        placeholder="Agrega acciones...",
        key='fav_tickers_multi'
    )
    
    # Guardar cambios si cambian las acciones
    if set(favoritos) != set(current_stocks):
        all_portfolios[active_portfolio_name] = favoritos
        guardar_favs_dict(all_portfolios)

    activar_favs = st.sidebar.checkbox("Ver solo este portafolio", value=False)
    
    # Período
    st.sidebar.subheader("📅 Período Principal")
    periodo_sel = st.sidebar.selectbox(
        'Filtrar por período:',
        options=['Overall', 'Hourly', 'Daily', 'Weekly', 'Monthly'],
        index=4,
        key='periodo'
    )
    
    # Sugerencia
    todas_las_sugerencias = ["Strong Sell", "Sell", "Hold", "Buy", "Strong Buy"]
    sugerencias_sel = st.sidebar.multiselect(
        '📌 Sugerencia:',
        options=todas_las_sugerencias,
        default=todas_las_sugerencias,
        key='sugerencias'
    )
    
    # Rango de precio
    st.sidebar.subheader("💰 Precio")
    precio_min = float(df['Precio'].min())
    precio_max = float(df['Precio'].max())
    min_precio, max_precio = st.sidebar.slider(
        'Rango de precio:',
        precio_min,
        precio_max,
        (precio_min, precio_max),
        key='slider_precio'
    )
    
    # Rango de cambio día
    st.sidebar.subheader("📈 Cambio % (día)")
    cambio_dia_min = float(df[col_cambio_dia].min())
    cambio_dia_max = float(df[col_cambio_dia].max())
    min_cambio_dia, max_cambio_dia = st.sidebar.slider(
        'Rango:',
        cambio_dia_min,
        cambio_dia_max,
        (cambio_dia_min, cambio_dia_max),
        key='slider_cambio_dia'
    )
    
    # Volumen
    st.sidebar.subheader("📊 Volumen")
    vol_disponible = df['Volumen (M)'].dropna()
    if len(vol_disponible) > 0:
        vol_min = float(vol_disponible.min())
        vol_max = float(vol_disponible.max())
        min_vol, max_vol = st.sidebar.slider(
            'Volumen (M):',
            vol_min,
            vol_max,
            (vol_min, vol_max),
            key='slider_vol'
        )
    else:
        min_vol, max_vol = 0, 1000
    
    # Aplicar filtros a tabla
    df_filt = df[
        (df[periodo_sel].isin(sugerencias_sel)) &
        (df['Precio'] >= min_precio) &
        (df['Precio'] <= max_precio) &
        (df[col_cambio_dia] >= min_cambio_dia) &
        (df[col_cambio_dia] <= max_cambio_dia)
    ].copy()
    
    # Filtro de Favoritos
    if activar_favs:
        if favoritos:
            df_filt = df_filt[df_filt['Ticker'].isin(favoritos)]
        else:
            st.warning("Tu portafolio está vacío. Agrega acciones en la barra lateral.")
            df_filt = df_filt.iloc[0:0]
    
    if 'Volumen (M)' in df_filt.columns:
        df_filt = df_filt[(df_filt['Volumen (M)'].notna()) & 
                          (df_filt['Volumen (M)'] >= min_vol) & 
                          (df_filt['Volumen (M)'] <= max_vol)]
    
    # Obtener datos del ticker
    ticker_data = df[df['Ticker'] == ticker_sel].iloc[0]
    
    # ==================== INFORMACIÓN DEL PRECIO ====================
    col1, col2 = st.columns([2, 1])
    
    with col1:
        precio = ticker_data['Precio']
        cambio_dia = pd.to_numeric(ticker_data.get('Cambio % (día)', 0), errors='coerce')
        
        precio_html = f"""
        <div class="price-info">
            <div class="price-current">
                <div class="price-value">${precio:.2f}</div>
                <div class="price-change {'positive' if cambio_dia > 0 else 'negative'}">
                    {'▲' if cambio_dia > 0 else '▼'} {abs(cambio_dia):.2f}%
                </div>
            </div>
        </div>
        """
        st.markdown(precio_html, unsafe_allow_html=True)
    
    with col2:
        vol = ticker_data.get('Volumen (M)', 'N/A')
        per = ticker_data.get('PER', 'N/A')
        st.markdown(f"""
        <div class="info-box">
        <strong>Vol (M):</strong> {vol}<br>
        <strong>P/E:</strong> {per}
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== RESUMEN GENERAL (OVERALL) ====================
    overall = ticker_data['Overall']
    overall_lower = overall.lower().replace(' ', '-')
    
    period_badges = f"""
    <div class="summary-box {overall_lower}">
        <div class="summary-verdict">{overall}</div>
        <div class="summary-periods">
            <span class="period-badge {ticker_data['Hourly'].lower().replace(' ', '-')}">Hourly: {ticker_data['Hourly']}</span>
            <span class="period-badge {ticker_data['Daily'].lower().replace(' ', '-')}">Daily: {ticker_data['Daily']}</span>
            <span class="period-badge {ticker_data['Weekly'].lower().replace(' ', '-')}">Weekly: {ticker_data['Weekly']}</span>
            <span class="period-badge {ticker_data['Monthly'].lower().replace(' ', '-')}">Monthly: {ticker_data['Monthly']}</span>
        </div>
    </div>
    """
    st.markdown(period_badges, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== SECCIONES EN COLUMNAS ====================
    col1, col2 = st.columns(2)
    
    # COLUMNA IZQUIERDA: Indicadores Técnicos
    with col1:
        st.markdown('<div class="section-title">📊 Indicadores Técnicos</div>', unsafe_allow_html=True)
        
        rsi_1d = pd.to_numeric(ticker_data.get('RSI 1d', np.nan), errors='coerce')
        rsi_1w = pd.to_numeric(ticker_data.get('RSI 1w', np.nan), errors='coerce')
        rsi_1m = pd.to_numeric(ticker_data.get('RSI 1m', np.nan), errors='coerce')
        macd = ticker_data.get('MACD', np.nan)
        
        # RSI 1d
        if not np.isnan(rsi_1d):
            col_a, col_b, col_c = st.columns([1.5, 1, 1.5])
            with col_a:
                col_label, col_info = st.columns([4, 1])
                with col_label:
                    st.write("**RSI (1D)**")
                with col_info:
                    with st.popover("?", help="Información del indicador"):
                        tooltip_rsi_1d = get_rsi_tooltip(rsi_1d, "1D")
                        st.markdown(tooltip_rsi_1d)
            with col_b:
                st.write(f"{rsi_1d:.0f}")
            with col_c:
                if rsi_1d < 30:
                    st.write("🟢 Sobrevendido")
                elif rsi_1d < 50:
                    st.write("🟡 Débil")
                elif rsi_1d < 70:
                    st.write("⚪ Neutral")
                else:
                    st.write("🔴 Sobrecomprado")
            st.divider()
        
        # RSI 1w
        if not np.isnan(rsi_1w):
            col_a, col_b, col_c = st.columns([1.5, 1, 1.5])
            with col_a:
                col_label, col_info = st.columns([4, 1])
                with col_label:
                    st.write("**RSI (1W)**")
                with col_info:
                    with st.popover("?", help="Información del indicador"):
                        tooltip_rsi_1w = get_rsi_tooltip(rsi_1w, "1W")
                        st.markdown(tooltip_rsi_1w)
            with col_b:
                st.write(f"{rsi_1w:.0f}")
            with col_c:
                if rsi_1w < 30:
                    st.write("🟢 Sobrevendido")
                elif rsi_1w < 50:
                    st.write("🟡 Débil")
                elif rsi_1w < 70:
                    st.write("⚪ Neutral")
                else:
                    st.write("🔴 Sobrecomprado")
            st.divider()
        
        # RSI 1m
        if not np.isnan(rsi_1m):
            col_a, col_b, col_c = st.columns([1.5, 1, 1.5])
            with col_a:
                col_label, col_info = st.columns([4, 1])
                with col_label:
                    st.write("**RSI (1M)**")
                with col_info:
                    with st.popover("?", help="Información del indicador"):
                        tooltip_rsi_1m = get_rsi_tooltip(rsi_1m, "1M")
                        st.markdown(tooltip_rsi_1m)
            with col_b:
                st.write(f"{rsi_1m:.0f}")
            with col_c:
                if rsi_1m < 30:
                    st.write("🟢 Sobrevendido")
                elif rsi_1m < 50:
                    st.write("🟡 Débil")
                elif rsi_1m < 70:
                    st.write("⚪ Neutral")
                else:
                    st.write("🔴 Sobrecomprado")
            st.divider()
        
        # MACD
        if macd != 'N/A' and not pd.isna(macd):
            col_a, col_b, col_c = st.columns([1.5, 1, 1.5])
            with col_a:
                col_label, col_info = st.columns([4, 1])
                with col_label:
                    st.write("**MACD**")
                with col_info:
                    try:
                        macd_val = float(macd)
                        with st.popover("?", help="Información del indicador"):
                            tooltip_macd = get_macd_tooltip(macd_val)
                            st.markdown(tooltip_macd)
                    except:
                        pass
            with col_b:
                try:
                    macd_val = float(macd)
                    st.write(f"{macd_val:.2f}")
                except:
                    st.write(macd)
            with col_c:
                try:
                    macd_val = float(macd)
                    st.write("🟢 Positivo" if macd_val > 0 else "🔴 Negativo")
                except:
                    st.write("N/A")
            st.divider()
        
        # Sentimiento
        sentiment = ticker_data.get('Analyst Sentiment', 'N/A')
        if sentiment != 'N/A':
            col_a, col_b, col_c = st.columns([1.5, 1.5, 1.5])
            with col_a:
                col_label, col_info = st.columns([4, 1])
                with col_label:
                    st.write("**Sentimiento**")
                with col_info:
                    with st.popover("?", help="Información del indicador"):
                        if sentiment == "Strong Buy":
                            st.markdown("🟢🟢 **STRONG BUY**\n\nLos analistas son MUY optimistas. Señal muy positiva. Más compradores que vendedores.")
                        elif sentiment == "Buy":
                            st.markdown("🟢 **BUY**\n\nLos analistas son optimistas. Señal positiva. Hay interés de compra.")
                        elif sentiment == "Hold":
                            st.markdown("⚪ **HOLD**\n\nMantener posición. Los analistas están en equilibrio. Esperar cambios.")
                        elif sentiment == "Sell":
                            st.markdown("🔴 **SELL**\n\nLos analistas son pesimistas. Señal negativa. Hay interés de venta.")
                        elif sentiment == "Strong Sell":
                            st.markdown("🔴🔴 **STRONG SELL**\n\nLos analistas son MUY pesimistas. Señal muy negativa. Más vendedores que compradores.")
            with col_b:
                st.write(sentiment)
            with col_c:
                if sentiment == "Strong Buy":
                    st.write("🟢🟢")
                elif sentiment == "Buy":
                    st.write("🟢")
                elif sentiment == "Hold":
                    st.write("⚪")
                elif sentiment == "Sell":
                    st.write("🔴")
                elif sentiment == "Strong Sell":
                    st.write("🔴🔴")
                else:
                    st.write("N/A")
    
    # COLUMNA DERECHA: Medias Móviles
    with col2:
        st.markdown('<div class="section-title">📈 Medias Móviles</div>', unsafe_allow_html=True)
        
        sma_50 = ticker_data.get('SMA 50', np.nan)
        sma_200 = ticker_data.get('SMA 200', np.nan)
        precio = ticker_data['Precio']
        
        # SMA 50
        if sma_50 != 'N/A' and not pd.isna(sma_50):
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                col_label, col_info = st.columns([4, 1])
                with col_label:
                    st.write("**SMA 50**")
                with col_info:
                    try:
                        sma_50_val = float(sma_50)
                        with st.popover("?", help="Información del indicador"):
                            tooltip_sma50 = get_sma_tooltip(precio, sma_50_val, 50)
                            st.markdown(tooltip_sma50)
                    except:
                        pass
            with col_b:
                try:
                    sma_50_val = float(sma_50)
                    st.write(f"${sma_50_val:.2f}")
                except:
                    st.write(sma_50)
            with col_c:
                try:
                    sma_50_val = float(sma_50)
                    if precio > sma_50_val:
                        st.write("🟢 COMPRA")
                    else:
                        st.write("🔴 VENTA")
                except:
                    st.write("N/A")
        
        st.divider()
        
        # SMA 200
        if sma_200 != 'N/A' and not pd.isna(sma_200):
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                col_label, col_info = st.columns([4, 1])
                with col_label:
                    st.write("**SMA 200**")
                with col_info:
                    try:
                        sma_200_val = float(sma_200)
                        with st.popover("?", help="Información del indicador"):
                            tooltip_sma200 = get_sma_tooltip(precio, sma_200_val, 200)
                            st.markdown(tooltip_sma200)
                    except:
                        pass
            with col_b:
                try:
                    sma_200_val = float(sma_200)
                    st.write(f"${sma_200_val:.2f}")
                except:
                    st.write(sma_200)
            with col_c:
                try:
                    sma_200_val = float(sma_200)
                    if precio > sma_200_val:
                        st.write("📈 UPTREND")
                    else:
                        st.write("📉 DOWNTREND")
                except:
                    st.write("N/A")
        
        st.divider()
        
        # ==================== RANGOS (Day / 52w) ====================
        st.markdown('<div class="section-title">📊 Rangos</div>', unsafe_allow_html=True)
        
        def render_range_bar(label, low, high, current):
            if pd.isna(low) or pd.isna(high) or pd.isna(current) or high == low:
                return ""
            
            # Calcular porcentaje (clamped 0-100)
            percent = ((current - low) / (high - low)) * 100
            percent = max(0, min(100, percent))
            
            return f"""
            <div class="range-section">
                <div class="range-header">{label}</div>
                <div class="range-values-row">
                    <span>{low:.2f}</span>
                    <span>{high:.2f}</span>
                </div>
                <div class="range-bar-bg">
                    <div class="range-marker" style="left: {percent}%;"></div>
                </div>
            </div>
            """
        
        day_low = pd.to_numeric(ticker_data.get('Day Low', np.nan), errors='coerce')
        day_high = pd.to_numeric(ticker_data.get('Day High', np.nan), errors='coerce')
        low_52w = pd.to_numeric(ticker_data.get('52w Low', np.nan), errors='coerce')
        high_52w = pd.to_numeric(ticker_data.get('52w High', np.nan), errors='coerce')
        
        html_ranges = ""
        html_ranges += render_range_bar("Rango Diario", day_low, day_high, precio)
        html_ranges += render_range_bar("Rango 52 Semanas", low_52w, high_52w, precio)
        st.markdown(html_ranges, unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # MAIN CONTENT
    # ---------------------------------------------------------
    
    st.markdown("---")
    
    st.markdown("---")
    
    # ==================== ANÁLISIS AVANZADO (MOVIDO ARRIBA) ====================
    st.markdown('<div class="section-title">🧠 Análisis Avanzado</div>', unsafe_allow_html=True)

    def indicator_row(title: str, value: str, status: str, tooltip_md: str, color_status=None):
        """Fila con indicador, valor, estado y tooltip explicativo."""
        if pd.isna(value) or str(value).strip() in ["N/A", "nan", "None", ""]:
            return
            
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            # Título y popover ("coso de info")
            sub1, sub2 = st.columns([4, 1])
            with sub1:
                st.markdown(f"**{title}**")
            with sub2:
                with st.popover("?", help=f"Más info sobre {title}"):
                    st.markdown(tooltip_md)
        with c2:
            st.write(value)
        with c3:
            if color_status:
                st.markdown(f"<span style='color:{color_status}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
            else:
                st.write(status)
        st.divider()

    # 1) Fair Value (Valor Razonable)
    fair_val = pd.to_numeric(ticker_data.get('Fair Value', np.nan), errors='coerce')
    precio_actual = pd.to_numeric(ticker_data.get('Precio', np.nan), errors='coerce')
    
    if not pd.isna(fair_val) and not pd.isna(precio_actual):
        upside = ((fair_val - precio_actual) / precio_actual) * 100
        
        if upside > 5:
            fv_status = f"🟢 Infravalorada ({upside:+.2f}%)"
            fv_color = "#00aa00"
        elif upside < -5:
            fv_status = f"🔴 Sobrevalorada ({upside:+.2f}%)"
            fv_color = "#dd0000"
        else:
            fv_status = f"⚪ Bien Valorada ({upside:+.2f}%)"
            fv_color = "#888888"
        
        indicator_row(
            "Fair Value (Valor Justo)",
            f"${fair_val:.2f}",
            fv_status,
            f"**¿Qué es?**\nEstimación del valor real de la acción basada en el consenso de analistas o fundamentales (Graham).\n\n**Precio Actual:** ${precio_actual:.2f}\n**Objetivo:** ${fair_val:.2f}\n**Potencial:** {upside:+.2f}%",
            fv_color
        )

    # 2) Ranking Sectorial (Con color de tendencia del sector)
    sector_1m = pd.to_numeric(ticker_data.get('Sector 1M', np.nan), errors='coerce')
    rank_val = str(ticker_data.get('Ranking Sectorial', 'N/A'))
    sector_name = str(ticker_data.get('Sector', 'N/A'))
    
    if rank_val != 'N/A':
        sec_status = "⚪ Neutro"
        sec_color = None
        if not pd.isna(sector_1m):
            if sector_1m > 0:
                sec_status = f"🟢 Sector Alcista ({sector_1m:+.2f}%)"
                sec_color = "#00aa00"
            else:
                sec_status = f"🔴 Sector Bajista ({sector_1m:+.2f}%)"
                sec_color = "#dd0000"
        
        indicator_row(
            "Ranking Sectorial", 
            rank_val, 
            sec_status, 
            f"**¿Qué es?**\nLa posición de esta acción comparada con otras de su mismo sector ({sector_name}) en el último mes.\n\n**Interpretación:**\n- Si el sector está en **Verde**, la 'marea' ayuda a subir.\n- Si está en **Rojo**, el sector está cayendo y arrastra a la acción.",
            sec_color
        )

    # 3) Beta (Volatilidad)
    beta_val = pd.to_numeric(ticker_data.get('Beta', np.nan), errors='coerce')
    if not pd.isna(beta_val):
        beta_status = "🟢 Estable" if beta_val < 1 else "🟡 Volátil" if beta_val < 1.5 else "🔴 Muy Agresiva"
        indicator_row(
            "Beta (Volatilidad)",
            f"{beta_val:.2f}",
            beta_status,
            "**¿Qué es?**\nMide cuánto se mueve la acción en relación al mercado (S&P 500).\n\n**Interpretación:**\n- **1.0**: Se mueve igual que el mercado.\n- **> 1.5**: Sube (y baja) mucho más rápido que el mercado (Alto Riesgo).\n- **< 0.8**: Es más defensiva y estable."
        )

    # 4) Soportes y Resistencias (Pivot Points)
    try:
        h = pd.to_numeric(ticker_data.get("Day High", np.nan), errors="coerce")
        l = pd.to_numeric(ticker_data.get("Day Low", np.nan), errors="coerce")
        c = pd.to_numeric(ticker_data.get("Precio", np.nan), errors="coerce")
        if not pd.isna(h) and not pd.isna(l) and not pd.isna(c) and h != l:
            p = (h + l + c) / 3
            s1 = 2 * p - h
            r1 = 2 * p - l
            indicator_row(
                "Punto Pivote (P)",
                f"${p:.2f}",
                f"S1: {s1:.2f} | R1: {r1:.2f}",
                "**¿Qué es?**\nNiveles matemáticos basados en el precio de ayer donde el precio tiende a rebotar.\n\n**Interpretación:**\n- **P (Pivote):** Eje central. Si el precio está arriba, es alcista intradía.\n- **S1 (Soporte):** Piso probable. Buen lugar para comprar.\n- **R1 (Resistencia):** Techo probable. Buen lugar para vender."
            )
    except:
        pass

    # 5) Volumen Relativo
    vol_col = 'Volumen Relativo'
    rel_vol = pd.to_numeric(ticker_data.get(vol_col, np.nan), errors="coerce")
    if not pd.isna(rel_vol):
        if rel_vol >= 1.5:
            status = "🟢 Fuerte Interés"
            color = "#00aa00"
        elif rel_vol >= 0.75:
            status = "⚪ Normal"
            color = None
        else:
            status = "🟡 Débil"
            color = "#aaaa00"
        indicator_row(
            "Volumen Relativo",
            f"{rel_vol:.2f}x",
            status,
            "**¿Qué es?**\nComparación del volumen de hoy contra el promedio de los últimos 20 días.\n\n**Interpretación:**\n- **> 1.5x**: Mucho interés institucional (Movimiento fuerte).\n- **< 0.8x**: Poco interés (Movimiento débil).",
            color
        )

    # 6) ATR (Volatilidad en $)
    atr = pd.to_numeric(ticker_data.get('ATR 14', np.nan), errors='coerce')
    atr_pct = pd.to_numeric(ticker_data.get('ATR %', np.nan), errors='coerce')
    if not pd.isna(atr):
        indicator_row(
            "ATR (Rango Diario)",
            f"${atr:.2f}",
            f"±{atr_pct:.2f}%" if not pd.isna(atr_pct) else "",
            f"**¿Qué es?**\nEl rango promedio que se mueve el precio en un día (Average True Range).\n\n**Uso:**\nSirve para poner Stop Loss. Si la acción se mueve ${atr:.2f} por día, tu stop debería estar al menos a esa distancia para que no te saque el 'ruido' normal."
        )

    # 7) Próximos Resultados (Earnings)
    earnings = str(ticker_data.get('Earnings Date', 'N/A'))
    if earnings != 'N/A' and earnings != 'None':
        indicator_row(
            "Próximos Resultados",
            earnings,
            "📅 Evento",
            "**¿Qué es?**\nFecha estimada del próximo reporte de ganancias.\n\n**Riesgo:**\nOperar cerca de esta fecha es muy riesgoso debido a la alta volatilidad posible (Gaps).",
            "#ffaa00"
        )
    
    st.markdown("---")

    # ==================== OBJETIVO DE PRECIO (MOVIDO AL MEDIO) ====================
    st.markdown('<div class="section-title">🎯 Objetivo de Precio</div>', unsafe_allow_html=True)
    
    price_target = ticker_data.get('Price Target', np.nan)
    upside = ticker_data.get('Upside %', np.nan)
    
    if not pd.isna(price_target) and not pd.isna(upside):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.metric("Precio Actual", f"${precio:.2f}")
        with col2:
            st.write("")
            st.write("")
            if upside > 0:
                st.write(f"📈 **{upside:+.2f}%** UPSIDE")
            else:
                st.write(f"📉 **{upside:+.2f}%** DOWNSIDE")
        with col3:
            st.metric("Objetivo", f"${price_target:.2f}")
    else:
        st.info("⚠️ Datos de precio objetivo no disponibles")
    
    st.markdown("---")
    
    # ==================== DATOS ADICIONALES (MOVIDO AL FINAL) ====================
    st.markdown('<div class="section-title">📋 Datos Adicionales</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cambio_sem = ticker_data.get('Cambio % (semana)', 'N/A')
        st.metric("Cambio Semana", f"{cambio_sem}%")
    
    with col2:
        cambio_mes = ticker_data.get('Cambio % (mes)', 'N/A')
        st.metric("Cambio Mes", f"{cambio_mes}%")
    
    with col3:
        div_yield = ticker_data.get('Div Yield (%)', 'N/A')
        st.metric("Div Yield", f"{div_yield}%")
    
    with col4:
        vol = ticker_data.get('Volumen (M)', 'N/A')
        st.metric("Volumen (M)", vol)
    
    st.markdown("---")
    st.markdown("#  Comparar con Otras Acciones")
    
    # ==================== ORDENAMIENTO ====================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_col = st.selectbox(
            'Ordenar por:',
            options=['Ticker', 'Precio', col_cambio_dia, 'Cambio % (semana)', 'Cambio % (mes)', 'RSI 1m', 'Upside %'],
            key='sort_col'
        )
    
    with col2:
        sort_order = st.radio(
            'Orden:',
            options=['↓ Mayor a menor', '↑ Menor a mayor'],
            key='sort_order'
        )
    
    # Aplicar ordenamiento
    ascending = sort_order == '↑ Menor a mayor'
    try:
        df_filt = df_filt.sort_values(by=sort_col, ascending=ascending, na_position='last')
    except:
        pass
    
    # ==================== TABLA COMPARATIVA ====================
    display_cols = [
        'Ticker', 'Precio', col_cambio_dia, 'Cambio % (semana)', 'Cambio % (mes)',
        'Volumen (M)', 'RSI 1m', 'Hourly', 'Daily', 'Weekly', 'Monthly',
        'Analyst Sentiment', 'Price Target', 'Upside %'
    ]
    display_cols = [col for col in display_cols if col in df_filt.columns]
    
    tabla_html = '<style>'
    tabla_html += '''
    @media (prefers-color-scheme: dark) {
        table { background-color: #1e1e1e; color: #ffffff; }
        th { background-color: #0d47a1; color: #ffffff; }
        td { background-color: #2d2d2d; color: #ffffff; border-color: #444; }
        tr:nth-child(even) { background-color: #262626; }
        tr:hover { background-color: #333333; }
    }
    
    @media (prefers-color-scheme: light) {
        table { background-color: #ffffff; color: #000000; }
        th { background-color: #003366; color: #ffffff; }
        td { background-color: #ffffff; color: #000000; border-color: #ddd; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #efefef; }
    }
    
    table { 
        width: 100%; 
        border-collapse: collapse; 
        font-family: Arial, sans-serif; 
        font-size: 11px; 
    }
    th { 
        padding: 8px; 
        text-align: center; 
        font-weight: bold; 
        border: 1px solid; 
    }
    td { 
        padding: 6px; 
        border: 1px solid; 
        text-align: center; 
    }
    
    .strong-buy { background-color: #00AA00 !important; color: white; font-weight: bold; }
    .buy { background-color: #66FF66 !important; color: black; font-weight: bold; }
    .sell { background-color: #FF9999 !important; color: black; font-weight: bold; }
    .strong-sell { background-color: #DD0000 !important; color: white; font-weight: bold; }
    .hold { background-color: #CCCCCC !important; color: black; }
    .positivo { color: #00AA00; font-weight: bold; }
    .negativo { color: #DD0000; font-weight: bold; }
    .ticker { text-align: left; font-weight: bold; }
    '''
    tabla_html += '</style>'
    tabla_html += '<table>'
    
    # Encabezados
    tabla_html += '<tr>'
    for col in display_cols:
        tabla_html += f'<th>{col}</th>'
    tabla_html += '</tr>'
    
    # Filas
    for idx, row in df_filt[display_cols].iterrows():
        tabla_html += '<tr>'
        for col in display_cols:
            val = row[col]
            
            # Formatear valor
            if isinstance(val, float):
                val_str = f"{val:.2f}"
            else:
                val_str = str(val)
            
            clase = ''
            
            # Chequear si es ticker argentino para highlight
            is_arg = False
            if 'Ticker' in row:
                 is_arg = is_arg_check = is_argentine_stock(row['Ticker'])

            if col == 'Ticker':
                clase = 'ticker'
                if is_arg:
                    clase += ' arg-highlight'
                
                # Crear link a Investing.com
                ticker_url = get_investing_url(val_str)
                tabla_html += f'<td class="{clase}"><a href="{ticker_url}" target="_blank" style="color: #58a6ff; text-decoration: none; cursor: pointer;">{val_str}</a></td>'
                continue
            
            # Colorear sugerencias por período
            if col in ['Hourly', 'Daily', 'Weekly', 'Monthly', 'Analyst Sentiment']:
                clase = {
                    'Strong Buy': 'strong-buy',
                    'Buy': 'buy',
                    'Strong Sell': 'strong-sell',
                    'Sell': 'sell',
                    'Hold': 'hold'
                }.get(val, '')
            
            # Colorear cambios porcentuales
            elif 'Cambio' in col or 'Upside' in col:
                try:
                    num_val = float(val)
                    clase = 'positivo' if num_val > 0 else 'negativo' if num_val < 0 else ''
                except:
                    pass
            
            elif col == 'Ticker':
                # Esto ya se manejó arriba, pero mantenemos el continue por si acaso el orden cambia
                continue
            
            if clase:
                # Regresar a Full Cell Styling pero con colores pasteles
                if clase == 'ticker arg-highlight': 
                     # Caso especial Highlight
                     ticker_url = get_investing_url(val_str)
                     tabla_html += f'<td class="{clase}"><a href="{ticker_url}" target="_blank" style="color: #fff; text-decoration: none; cursor: pointer;">{val_str}</a></td>'
                elif 'arg-highlight' in clase:
                     tabla_html += f'<td class="{clase}">{val_str}</td>'
                else:
                     # Standard classes (strong-buy, etc) applied to TD
                     tabla_html += f'<td class="{clase}">{val_str}</td>'
            else:
                tabla_html += f'<td>{val_str}</td>'
        tabla_html += '</tr>'
    
    tabla_html += '</table>'
    
    st.markdown(tabla_html, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("❌ No encontrado: analisis_mercado.xlsx")
    st.info("Ejecuta primero: `python analisis_profesional.py`")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    import traceback
    st.error(traceback.format_exc())
    st.error(traceback.format_exc())

# Lógica de Auto-Recarga con Cuenta Regresiva
if 'should_auto_reload' in locals() and should_auto_reload:
    import time
    import os
    
    # Calcular tiempo restante real
    wait_time = reload_seconds
    if os.path.exists('analisis_mercado.xlsx'):
        age = time.time() - os.path.getmtime('analisis_mercado.xlsx')
        wait_time = max(0, reload_seconds - age)
    
    # Cuenta regresiva visual
    for i in range(int(wait_time), -1, -1):
        mm, ss = divmod(i, 60)
        timer_placeholder.markdown(f"⏳ Actualización en: **{mm:02d}:{ss:02d}**")
        time.sleep(1)
        
    st.rerun()
