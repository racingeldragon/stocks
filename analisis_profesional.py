# -*- coding: utf-8 -*-

# Script Profesional - Análisis como Investing.com
import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD
import xlsxwriter
import time
import concurrent.futures
from datetime import datetime, timezone

# ==================== EMAIL ALERTS SYSTEM ====================
import smtplib
import ssl
import json
import os
from email.message import EmailMessage

# Credenciales (Soporta Streamlit Secrets para despliegue seguro)
import streamlit as st

def get_secret(key, default):
    try:
        return st.secrets.get(key, default)
    except:
        return default

EMAIL_SENDER = get_secret('EMAIL_SENDER', 'lchipasco@gmail.com')
EMAIL_PASSWORD = get_secret('EMAIL_PASSWORD', 'mlkz dkfw yuxw ycpt')
EMAIL_RECEIVER = EMAIL_SENDER

STATE_FILE = 'stock_states.json'

# ==================== INVESTING URLS ====================
from utils_links import get_investing_url

def load_previous_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_current_state(current_state):
    with open(STATE_FILE, 'w') as f:
        json.dump(current_state, f)

def send_email_alert(changes):
    if not changes:
        return

    # Detectar si estamos en horario de mercado (EST)
    import datetime
    import pytz
    est = pytz.timezone('US/Eastern')
    now_est = datetime.datetime.now(est)
    is_market_open = (now_est.weekday() < 5 and 9 <= now_est.hour < 16) # Simplificado
    market_status = "" if is_market_open else " [MERCADO CERRADO]"

    subject = f"🚨 ALERTA DE STOCKS: {len(changes)} Oportunidades{market_status}"
    
    # Pre-procesar alertas para enriquecer con textos completos
    enriched_changes = []
    
    for change in changes:
        tipo_raw = change['Type']
        ticker = change['Ticker']
        price = change['Price']
        rating = change.get('Rating', 'N/A')
        url = get_investing_url(ticker)
        
        # Datos técnicos para descripción
        rsi = change.get('RSI', 'N/A')
        upside = change.get('Upside', 'N/A')
        macd = change.get('MACD', 'N/A')
        sma50 = change.get('SMA50', 'N/A')
        
        # Determinar Acción y Razón Completa
        action = "INFO"
        reason_full = ""
        style = "color: #333;"
        
        if "OPORTUNIDAD" in tipo_raw:
            action = "COMPRAR"
            reason_full = f"<b>Cambio de Tendencia Confirmado.</b> Los indicadores técnicos se han alineado positivamente (Estatus: {rating}). "
            if rsi != 'N/A': reason_full += f"El RSI está en {rsi:.1f}, lo que muestra momentum creciente. "
            if macd != 'N/A' and macd > 0: reason_full += "El MACD está en terreno positivo, confirmando la fuerza del movimiento. "
            style = "color: #28a745; font-weight: bold;"
            
        elif "VENTA NECESARIA" in tipo_raw:
            action = "VENDER"
            reason_full = f"<b>Deterioro Técnico Grave.</b> La acción ha pasado a {rating}. El sistema sugiere salir para proteger capital. "
            if sma50 != 'N/A' and price < sma50: reason_full += f"El precio ha caído por debajo de la media de 50 días (${sma50:.2f}), confirmando debilidad."
            style = "color: #dc3545; font-weight: bold;"
            
        elif "JOYA" in tipo_raw:
            action = "COMPRAR"
            reason_full = f"<b>Oportunidad por Valoración.</b> Tiene un potencial de subida del {upside}% respecto al valor justo. "
            reason_full += "A diferencia de un movimiento técnico puro, aquí el análisis fundamental sugiere que la acción está muy barata."
            style = "color: #28a745; font-weight: bold;"
            
        elif "SOBREVENDIDO" in tipo_raw:
            action = "COMPRAR"
            reason_full = f"<b>Rebote Técnico Probable.</b> La acción está extremadamente sobrevendida (RSI: {rsi:.1f}). "
            reason_full += "Históricamente, niveles tan bajos de RSI suelen preceder a una recuperación rápida en el corto plazo."
            style = "color: #28a745; font-weight: bold;"
            
        elif "VOLUMEN" in tipo_raw:
            action = "ATENCIÓN"
            vol_rel = change.get('VolRel', 'N/A')
            reason_full = f"<b>Actividad Institucional Inusual.</b> El volumen es {vol_rel}x superior al promedio. "
            reason_full += "Esto indica que grandes inversores están entrando o saliendo, lo que suele anticipar volatilidad alta."
            style = "color: #007bff; font-weight: bold;"
            
        # Guardar todo en el objeto
        change['Action_Label'] = action
        change['Reason_Full'] = reason_full
        change['Style'] = style
        change['URL'] = url
        enriched_changes.append(change)

    # Construir Email
    body = "<h2>Resumen de Oportunidades:</h2>"
    body += "<ul style='font-size: 16px; line-height: 1.6; color: #333;'>"
    
    for c in enriched_changes:
        ticker = c['Ticker']
        price = c['Price']
        rating = c.get('Rating', 'N/A')
        action = c['Action_Label']
        reason = c['Reason_Full']
        style = c['Style']
        
        body += f"<li style='margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px;'>"
        body += f"<span style='{style}; font-size: 18px;'>[{action}] {ticker} (${price})</span><br>"
        body += f"<div style='margin-top: 5px; font-size: 15px; color: #444;'>{reason}</div>"
        body += f"<div style='margin-top: 8px;'><a href='{c.get('URL', '#')}' style='background-color: #0d47a1; color: white; text-decoration: none; padding: 5px 12px; border-radius: 4px; font-size: 13px;'>📊 Ver en Investing.com</a></div>"
        body += f"</li>"
        
    body += "</ul>"
    

    # Cargar destinatarios desde archivo de configuración
    recipients = [EMAIL_RECEIVER] # Default fallback
    try:
        import json
        if os.path.exists('email_config.json'):
            with open('email_config.json', 'r') as f:
                config = json.load(f)
                if 'recipients' in config and config['recipients']:
                    recipients = config['recipients']
    except Exception as e:
        print(f"⚠️ Error cargando destinatarios: {e}. Usando default.")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            
            # Enviar a cada destinatario
            for recipient in recipients:
                try:
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = EMAIL_SENDER
                    msg['To'] = recipient
                    msg.set_content(body, subtype='html')
                    smtp.send_message(msg)
                    print(f"✉️ Alerta enviada a: {recipient}")
                except Exception as ex:
                    print(f"❌ Falló envío a {recipient}: {ex}")
                    
        print("✅ Proceso de envío finalizado.")
        
        # Guardar en historial para Sidebar (app web)
        save_alerts_to_sidebar(enriched_changes)
        
    except Exception as e:
        print(f"⚠️ Error general SMTP: {e}")

def save_alerts_to_sidebar(new_alerts):
    ALERTS_FILE = 'recent_alerts.json'
    import datetime
    
    # Cargar existentes
    existing = []
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, 'r') as f:
                existing = json.load(f)
        except:
            existing = []
    
    # Agregar nuevos
    timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
    
    for alert in new_alerts:
        action = alert.get('Action_Label', 'INFO')
        # Determinar tipo limpio para iconos
        type_clean = "info"
        if action == "COMPRAR": type_clean = "success"
        elif action == "VENDER": type_clean = "error"
        elif action == "ATENCIÓN": type_clean = "warning"
        
        alert_obj = {
            "time": timestamp,
            "ticker": alert['Ticker'],
            "action": action,
            "price": alert['Price'],
            "rating": alert.get('Rating', 'N/A'),
            "reason_full": alert.get('Reason_Full', alert['Type']), # Guardar la razón completa
            "type_clean": type_clean
        }
        existing.insert(0, alert_obj) # Insertar al principio
        
    # Mantener solo ultimos 50
    existing = existing[:50]
    
    with open(ALERTS_FILE, 'w') as f:
        json.dump(existing, f)

tickers_100 = sorted(list(set([
    # Lista Usuario
    "AAL", "AAPL", "ABEV", "ADBE", "AEM", "ALUA.BA", "AGRO.BA", "AMD", "AMZN", "ANF", "ARKK", "ARGT",
    "ARS=X", "ASML", "AVGO", "B", "BABA", "BBD", "BIDU", "BIOX", "BITF", "BRK-B",
    "BYMA.BA", "CAT", "CECO2.BA", "CELU.BA", "CEPU", "CGPA2.BA", "COIN", "CADO.BA", "COME.BA",
    "CRM", "CVX", "DIA", "DIS", "DOW", "EBAY", "ES", "ECOG.BA", "EEM", "EMBJ", "ETHA", "EWZ",
    "FXI", "GCDI.BA", "GE", "GGB", "GGAL.BA", "GLOB", "GLD", "GOOGL", "GPRK", "GS",
    "HARG.BA", "HMY", "HPQ", "HUT", "IBB", "IBM", "IBIT", "INTC", "IWM", "JD", "JMIA",
    "JNJ", "JPM", "KO", "LAC", "LAR", "LMT", "LOMA", "LLY", "MCD", "MELI", "META", "METR.BA",
    "MRK", "MRVL", "MSFT", "MSTR", "MU", "NFLX", "NIO", "NKE", "NVS", "NU",
    "NVDA", "PAGS", "OKLO", "PAM", "PANW", "PBR", "PEP", "PFE", "PG", "PLTR", "PYPL",
    "QCOM", "QQQ", "RBLX", "RIO", "SBUX", "SMH", "SLV", "SPOT", "SPY", "TGSU2.BA",
    "TRAN.BA", "TRIP", "TSLA", "TSM", "UBER", "UNH", "UPST", "URA", "URTH", "V", "VALO.BA",
    "VALE", "VIST", "VRSN", "VZ", "WMT", "XLC", "XLE", "XLF", "XLP", "XP", "XLK", "XPZ", "XLV",
    "XYZ", "YPF",
    # Lista Antigua (para no perder ninguno)
    'HD', 'BA', 'TXN', 'CSCO', 'ABBV', 'ACN', 'XOM', 'ABT', 'TMUS', 'DXCM', 'SQ', 'ETSY', 'ZM', 'ROKU',
    'SNAP', 'LYFT', 'DASH', 'SHOP', 'ZS', 'CRWD', 'OKTA', 'NET', 'ANET', 'LRCX', 'KLAC', 'SNPS', 'CDNS',
    'ANSS', 'PSTG', 'NOW', 'SPLK', 'DB', 'MS', 'BLK', 'SCHW', 'CME', 'ICE', 'CBOE', 'EFA', 'AGG', 'LQD',
    'HYG', 'TLT', 'IEF', 'SHV', 'USO', 'DBC', 'GSG', 'VTI', 'VEA', 'BND', 'BSV', 'BIV', 'BLV', 'SCHF'
    ])))

def get_sentiment_and_suggestion(rsi, macd, macd_signal, price, sma_50, sma_200):
    """
    Lógica coherente como Investing.com:
    - Compra: Cuando técnicos están al alza
    - Venta: Cuando técnicos están a la baja
    - Mantener: Cuando están mixtos
    """
    if np.isnan(rsi) or np.isnan(macd):
        return 'Mantener', 'Neutro'
    
    # Contar señales positivas y negativas
    signals_buy = 0
    signals_sell = 0
    
    # RSI: Lógica de Tendencia (Más agresiva)
    if rsi < 30:
        signals_buy += 2      # Sobrevendido (posible rebote)
    elif rsi < 45:
        signals_sell += 2     # Tendencia bajista clara
    elif rsi > 70:
        signals_sell += 2     # Sobrecomprado (posible corrección)
    elif rsi > 55:
        signals_buy += 2      # Tendencia alcista clara
    
    # MACD: Línea por encima = buy, por debajo = sell
    if macd > macd_signal:
        signals_buy += 2
    else:
        signals_sell += 2
    
    # SMA: Precio arriba = buy, abajo = sell
    if not np.isnan(sma_50):
        if price > sma_50:
            signals_buy += 2
            if not np.isnan(sma_200) and price > sma_200:
                signals_buy += 3  # Bonus fuerte por estar arriba de 200 (Tendencia alcista LP)
        elif price < sma_50:
            signals_sell += 2
            if not np.isnan(sma_200) and price < sma_200:
                signals_sell += 3  # Bonus fuerte por estar abajo de 200 (Tendencia bajista LP)
    
    # Determinar sugerencia
    if signals_buy >= signals_sell + 4:
        suggestion = 'Compra Fuerte'
        sentiment = 'Positivo'
    elif signals_buy >= signals_sell + 2:
        suggestion = 'Compra'
        sentiment = 'Positivo'
    elif signals_sell >= signals_buy + 4:
        suggestion = 'Venta Fuerte'
        sentiment = 'Negativo'
    elif signals_sell >= signals_buy + 2:
        suggestion = 'Venta'
        sentiment = 'Negativo'
    else:
        suggestion = 'Mantener'
        sentiment = 'Neutro'
    
    return suggestion, sentiment

def calc_sma(hist, window):
    if len(hist) < window:
        return np.nan
    return hist['Close'].rolling(window=window).mean().iloc[-1]

def calc_atr14(hist: pd.DataFrame) -> float:
    """ATR(14) a partir de OHLC diario (Wilder simple: SMA de TR)."""
    if hist is None or hist.empty:
        return np.nan
    required = {"High", "Low", "Close"}
    if not required.issubset(set(hist.columns)):
        return np.nan
    if len(hist) < 15:
        return np.nan

    high = hist["High"]
    low = hist["Low"]
    close = hist["Close"]
    prev_close = close.shift(1)

    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr = tr.rolling(window=14).mean().iloc[-1]
    return float(atr) if not pd.isna(atr) else np.nan

def parse_next_earnings_date(info: dict):
    """Intenta obtener una fecha de próximos resultados desde `info`."""
    try:
        ed = info.get("earningsDate")
        # Puede venir como lista/tupla de timestamps o datetime
        if isinstance(ed, (list, tuple)) and len(ed) > 0:
            ed0 = ed[0]
        else:
            ed0 = ed

        if ed0 is None:
            return None

        # pandas.Timestamp / datetime
        if hasattr(ed0, "to_pydatetime"):
            dt = ed0.to_pydatetime()
        elif isinstance(ed0, datetime):
            dt = ed0
        else:
            # timestamp (segundos)
            try:
                dt = datetime.fromtimestamp(float(ed0), tz=timezone.utc)
            except Exception:
                return None

        # Normalizar a fecha
        return dt.date().isoformat()
    except Exception:
        return None

def get_ticker_data(ticker):
    """Obtiene datos completos similar a Investing.com"""
    try:
        stock = yf.Ticker(ticker)
        
        # OPTIMIZACIÓN: Descargar 2 años de una vez y filtrar en memoria
        # Esto reduce de 4 peticiones HTTP a 1 sola por acción, manteniendo la misma data.
        hist_full = stock.history(period='2y')
        
        if hist_full.empty:
            raise ValueError('Datos insuficientes')
            
        hist_1m = hist_full.tail(252) # ~1 año (252 días de trading)
        hist_1w = hist_full.tail(64)  # ~3 meses
        
        if hist_1m.empty or len(hist_1m) < 50:
            raise ValueError('Datos insuficientes')
        
        # Precios
        price = hist_1m['Close'].iloc[-1]
        
        # Cambios porcentuales
        pct_day = ((hist_1m['Close'].iloc[-1] - hist_1m['Close'].iloc[-2]) / hist_1m['Close'].iloc[-2] * 100) if len(hist_1m) > 1 else 0
        
        # Info fundamental (Movido arriba para usar en precio)
        try:
            info = stock.info
        except:
            info = {}

        # CORRECCIÓN: Prioridad Info > Fast_Info > History
        # Info suele tener 'regularMarketPrice' que coincide mejor con Investing/Yahoo Web
        curr_price = info.get('currentPrice') or info.get('regularMarketPrice')
        prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
        
        if curr_price and prev_close:
            price = curr_price
            pct_day = ((curr_price - prev_close) / prev_close) * 100
        else:
            # Fallback a fast_info si info falla
            try:
                fast_info = stock.fast_info
                if hasattr(fast_info, 'last_price') and hasattr(fast_info, 'previous_close'):
                    rt_price = fast_info.last_price
                    rt_prev_close = fast_info.previous_close
                    if rt_price and rt_prev_close:
                        price = rt_price
                        pct_day = ((rt_price - rt_prev_close) / rt_prev_close) * 100
            except:
                pass

        # Fluctuación semanal (5 días de trading)
        if len(hist_1m) >= 6:
            price_week_ago = hist_1m['Close'].iloc[-6]
            pct_week = ((price - price_week_ago) / price_week_ago) * 100
        else:
            pct_week = pct_day
        
        # Fluctuación mensual (Cálculo exacto por fecha - 30 días)
        try:
            current_date = hist_1m.index[-1]
            target_date = current_date - pd.Timedelta(days=30)
            # Encontrar el índice más cercano a hace 30 días
            idx_month = hist_1m.index.searchsorted(target_date)
            idx_month = max(0, min(idx_month, len(hist_1m) - 1))
            price_month_ago = hist_1m['Close'].iloc[idx_month]
            pct_month = ((price - price_month_ago) / price_month_ago) * 100
        except:
            pct_month = pct_day * 20 # Fallback aproximado
        
        # Volumen promedio (en millones)
        curr_volume_m = (hist_1m['Volume'].iloc[-1] / 1_000_000) if 'Volume' in hist_1m.columns and len(hist_1m) > 0 else np.nan
        avg_volume_20_m = (hist_1m['Volume'].tail(20).mean() / 1_000_000) if 'Volume' in hist_1m.columns else np.nan
        rel_volume = (curr_volume_m / avg_volume_20_m) if (not np.isnan(curr_volume_m) and not np.isnan(avg_volume_20_m) and avg_volume_20_m != 0) else np.nan

        # ATR(14) + ATR% (volatilidad)
        atr14 = calc_atr14(hist_1m.tail(90))
        atr_pct = (atr14 / price * 100) if (not np.isnan(atr14) and price) else np.nan
        
        # Calcular indicadores para 1 mes (período principal)
        def calc_indicators(hist):
            if len(hist) < 14:
                return None
            try:
                rsi = RSIIndicator(hist['Close'], window=14).rsi().iloc[-1]
                macd_obj = MACD(hist['Close'])
                macd = macd_obj.macd().iloc[-1]
                macd_sig = macd_obj.macd_signal().iloc[-1]
                sma_50 = calc_sma(hist, 50)
                sma_200 = calc_sma(hist, 200)
                return {'rsi': rsi, 'macd': macd, 'macd_sig': macd_sig, 'sma_50': sma_50, 'sma_200': sma_200}
            except:
                return None
        
        # RSI 1d = RSI más reciente de hist_1m (últimas 30 días)
        tech_1d = calc_indicators(hist_1m) if len(hist_1m) >= 14 else None
        tech_1w = calc_indicators(hist_1w)
        tech_1m = calc_indicators(hist_1m)
        
        # Sugerencia principal (basada en 1 mes)
        if tech_1m:
            sugg_1m, sent = get_sentiment_and_suggestion(
                tech_1m['rsi'], tech_1m['macd'], tech_1m['macd_sig'],
                price, tech_1m['sma_50'], tech_1m['sma_200']
            )
        else:
            sugg_1m, sent = 'Mantener', 'Neutro'
        
        # Sugerencias para otros períodos
        if tech_1d:
            sugg_1d, _ = get_sentiment_and_suggestion(
                tech_1d['rsi'], tech_1d['macd'], tech_1d['macd_sig'],
                price, tech_1d['sma_50'], tech_1d['sma_200']
            )
        else:
            sugg_1d = 'Mantener'
        
        if tech_1w:
            sugg_1w, _ = get_sentiment_and_suggestion(
                tech_1w['rsi'], tech_1w['macd'], tech_1w['macd_sig'],
                price, tech_1w['sma_50'], tech_1w['sma_200']
            )
        else:
            sugg_1w = 'Mantener'
        
        # Info fundamental
        per = info.get('trailingPE', np.nan)
        eps = info.get('trailingEps', np.nan)
        book_value = info.get('bookValue', np.nan)
        beta = info.get('beta', np.nan)
        sector = info.get('sector', None)
        industry = info.get('industry', None)
        earnings_date = parse_next_earnings_date(info)
        div = (info.get('dividendYield', 0) * 100) if info.get('dividendYield') else 0
        
        # Fair Value: Prioridad al Target de Analistas, sino Graham
        target_price = info.get('targetMeanPrice', np.nan)
        fair_value = target_price
        
        if pd.isna(fair_value) and eps and book_value and eps > 0 and book_value > 0:
            # Fallback a Graham Number si no hay target de analistas
            fair_value = np.sqrt(22.5 * eps * book_value)
        
        # Datos adicionales para expandir información
        recommendation = info.get('recommendationKey', None)
        # Intentar obtener Market Cap de fast_info (más fiable)
        mkt_cap = stock.fast_info.market_cap if hasattr(stock.fast_info, 'market_cap') else info.get('marketCap', np.nan)
        fwd_pe = info.get('forwardPE', np.nan)
        price_to_book = info.get('priceToBook', np.nan)
        
        # Máximo y mínimo de 52 semanas
        # Intentar usar fast_info primero (más rápido y actual), fallback a info
        try:
            fi = stock.fast_info
            high_52w = fi.year_high if hasattr(fi, 'year_high') else info.get('fiftyTwoWeekHigh', np.nan)
            low_52w = fi.year_low if hasattr(fi, 'year_low') else info.get('fiftyTwoWeekLow', np.nan)
            day_low = fi.day_low if hasattr(fi, 'day_low') else info.get('dayLow', np.nan)
            day_high = fi.day_high if hasattr(fi, 'day_high') else info.get('dayHigh', np.nan)
        except:
            high_52w = info.get('fiftyTwoWeekHigh', np.nan)
            low_52w = info.get('fiftyTwoWeekLow', np.nan)
            day_low = info.get('dayLow', np.nan)
            day_high = info.get('dayHigh', np.nan)
        
        return {
            'Ticker': ticker,
            'Precio': round(price, 2),
            'Cambio % (día)': round(pct_day, 2),
            'Cambio % (semana)': round(pct_week, 2),
            'Cambio % (mes)': round(pct_month, 2),
            'Volumen (M)': round(curr_volume_m, 2) if not np.isnan(curr_volume_m) else np.nan,
            'Volumen Promedio (M)': round(avg_volume_20_m, 2) if not np.isnan(avg_volume_20_m) else np.nan,
            'Volumen Relativo': round(rel_volume, 2) if not np.isnan(rel_volume) else np.nan,
            'ATR 14': round(atr14, 4) if not np.isnan(atr14) else np.nan,
            'ATR %': round(atr_pct, 2) if not np.isnan(atr_pct) else np.nan,
            'RSI 1d': round(tech_1d['rsi'], 2) if tech_1d else np.nan,
            'RSI 1w': round(tech_1w['rsi'], 2) if tech_1w else np.nan,
            'RSI 1m': round(tech_1m['rsi'], 2) if tech_1m else np.nan,
            'SMA 50': round(tech_1m['sma_50'], 2) if tech_1m else np.nan,
            'SMA 200': round(tech_1m['sma_200'], 2) if tech_1m else np.nan,
            'MACD': round(tech_1m['macd'], 4) if tech_1m else np.nan,
            'MACD Signal': round(tech_1m['macd_sig'], 4) if tech_1m else np.nan,
            'PER': round(per, 2) if per else np.nan,
            'EPS (TTM)': round(eps, 4) if eps else np.nan,
            'Beta': round(beta, 2) if beta else np.nan,
            'Fair Value': round(fair_value, 2) if not np.isnan(fair_value) else np.nan,
            'Analyst Target': round(target_price, 2) if target_price else np.nan,
            'Analyst Rating': recommendation.capitalize() if recommendation else 'N/A',
            'Market Cap': mkt_cap,
            'Forward PE': round(fwd_pe, 2) if fwd_pe else np.nan,
            'P/B': round(price_to_book, 2) if price_to_book else np.nan,
            'Sector': sector if sector else None,
            'Industria': industry if industry else None,
            'Earnings Date': earnings_date if earnings_date else None,
            'Div Yield (%)': round(div, 2) if div else 0,
            'Day Low': round(day_low, 2) if day_low else np.nan,
            'Day High': round(day_high, 2) if day_high else np.nan,
            '52w Low': round(low_52w, 2) if low_52w else np.nan,
            '52w High': round(high_52w, 2) if high_52w else np.nan,
            'Sentimiento': sent,
            'Sugerencia 1d': sugg_1d,
            'Sugerencia 1w': sugg_1w,
            'Sugerencia 1m': sugg_1m
        }
    except Exception as e:
        return None

def main(progress_callback=None):
    # print(f"Analizando {len(tickers_100)} acciones...") # Comentado para evitar error I/O
    resultados = []
    
    # OPTIMIZACIÓN: Ejecución en paralelo (10 acciones a la vez)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(get_ticker_data, ticker): ticker for ticker in tickers_100}
        
        completed = 0
        total = len(tickers_100)
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            completed += 1
            if progress_callback:
                progress_callback(completed, total, ticker)
            
            try:
                data = future.result()
                if data:
                    resultados.append(data)
            except Exception:
                pass
    
    df = pd.DataFrame(resultados)
    # print(f"\n> {len(df)} acciones analizadas\n")
    
    # Ordenar por sugerencia principal
    orden = {'Compra Fuerte': 1, 'Compra': 2, 'Mantener': 3, 'Venta': 4, 'Venta Fuerte': 5}
    df['Orden'] = df['Sugerencia 1m'].map(orden).fillna(99)
    df = df.sort_values(['Orden', 'Cambio % (día)'], ascending=[True, False]).drop('Orden', axis=1)

    # ==================== CONTEXTO DE MERCADO: SPY + Sector (1M) + Ranking ====================
    def get_1m_return(symbol: str) -> float:
        try:
            data = yf.download(symbol, period="2mo", interval="1d", progress=False, auto_adjust=False)
            if data is None or data.empty or "Close" not in data.columns:
                return np.nan
            close = data["Close"].dropna()
            if len(close) < 10:
                return np.nan
            last = close.iloc[-1]
            # ~21 ruedas = 1 mes de trading
            prev = close.iloc[-22] if len(close) >= 22 else close.iloc[0]
            return float((last - prev) / prev * 100) if prev else np.nan
        except Exception:
            return np.nan

    SECTOR_ETF = {
        "Technology": "XLK",
        "Financial Services": "XLF",
        "Financial": "XLF",
        "Healthcare": "XLV",
        "Health Care": "XLV",
        "Consumer Cyclical": "XLY",
        "Consumer Defensive": "XLP",
        "Energy": "XLE",
        "Industrials": "XLI",
        "Communication Services": "XLC",
        "Real Estate": "XLRE",
        "Utilities": "XLU",
        "Basic Materials": "XLB",
        "Materials": "XLB",
    }

    spy_1m = get_1m_return("SPY")
    df["SPY 1M"] = round(spy_1m, 2) if not np.isnan(spy_1m) else np.nan

    # calcular 1M por sector ETF, cacheando
    sector_perf_cache = {}

    def sector_1m_for_row(sector_name: str) -> float:
        if not isinstance(sector_name, str) or sector_name in ["", "N/A"]:
            return np.nan
        etf = SECTOR_ETF.get(sector_name, None)
        if not etf:
            return np.nan
        if etf not in sector_perf_cache:
            sector_perf_cache[etf] = get_1m_return(etf)
        return sector_perf_cache[etf]

    df["Sector 1M"] = df["Sector"].apply(sector_1m_for_row) if "Sector" in df.columns else np.nan
    df["Sector 1M"] = pd.to_numeric(df["Sector 1M"], errors="coerce").round(2)

    # Ranking sectorial: ordenar por Cambio % (mes) dentro del sector
    if "Sector" in df.columns and "Cambio % (mes)" in df.columns:
        df["_rank_sector"] = (
            df.groupby("Sector")["Cambio % (mes)"]
            .rank(ascending=False, method="min")
        )
        df["_sector_count"] = df.groupby("Sector")["Ticker"].transform("count")
        df["Ranking Sectorial"] = df.apply(
            lambda r: f"{int(r['_rank_sector'])}/{int(r['_sector_count'])}"
            if (not pd.isna(r["_rank_sector"]) and not pd.isna(r["_sector_count"]) and r["_sector_count"] > 0)
            else "N/A",
            axis=1,
        )
        df = df.drop(columns=["_rank_sector", "_sector_count"])
    
    # Exportar a Excel
    with pd.ExcelWriter('analisis_mercado.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Análisis')
        workbook = writer.book
        worksheet = writer.sheets['Análisis']
        
        # Formato de encabezado
        header_format = workbook.add_format({
            'bold': True, 
            'bg_color': '#003366', 
            'font_color': 'white', 
            'border': 1,
            'align': 'center'
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Ancho de columnas
        worksheet.set_column('A:A', 12)  # Ticker
        worksheet.set_column('B:B', 14)  # Precio
        worksheet.set_column('C:E', 14)  # Cambios %
        worksheet.set_column('F:H', 18)  # Volumen, Vol Prom, Vol Rel
        worksheet.set_column('I:J', 10)  # RSI
        worksheet.set_column('K:M', 12)  # SMA/MACD
        worksheet.set_column('N:V', 14)  # Fundamentales extendidos
        worksheet.set_column('R:S', 18)  # Sector/Industria
        worksheet.set_column('T:V', 16)  # Earnings/ATR
        worksheet.set_column('W:Z', 16)  # Contexto (SPY/Sector/Ranking) + sugerencias
        
        worksheet.freeze_panes(1, 0)
    
    # print("\n✓ Archivo actualizado: analisis_mercado.xlsx")

    # Lógica de detección de cambios (Email Alerts)
    try:
        prev_state = load_previous_state()
        current_state = {}
        changes_to_alert = []

        for idx, row in df.iterrows():
            ticker = row['Ticker']
            new_sugg = row['Sugerencia 1m']
            price = row['Precio']
            current_state[ticker] = new_sugg
            
            # Capturar métricas técnicas comunes
            rsi_1d = row.get('RSI 1d', np.nan)
            macd_val = row.get('MACD', np.nan)
            sma_50 = row.get('SMA 50', np.nan)
            vol_rel = row.get('Volumen Relativo', np.nan)
            fair_val = row.get('Fair Value', 0)
            upside_val = 0
            if fair_val > 0 and price > 0:
                upside_val = round(((fair_val - price) / price) * 100, 1)

            if ticker in prev_state:
                old_sugg = prev_state[ticker]
                
                # Caso 1: OPORTUNIDAD
                if old_sugg not in ['Compra', 'Compra Fuerte'] and new_sugg == 'Compra Fuerte':
                    changes_to_alert.append({
                        'Ticker': ticker, 'Old': old_sugg, 'New': new_sugg, 
                        'Type': 'OPORTUNIDAD', 'Price': price, 'Rating': new_sugg,
                        'RSI': rsi_1d, 'MACD': macd_val, 'SMA50': sma_50
                    })
                
                # Caso 2: SALIDA NECESARIA
                elif old_sugg not in ['Venta', 'Venta Fuerte'] and new_sugg == 'Venta Fuerte':
                    changes_to_alert.append({
                        'Ticker': ticker, 'Old': old_sugg, 'New': new_sugg, 
                        'Type': 'VENTA NECESARIA', 'Price': price, 'Rating': new_sugg,
                        'RSI': rsi_1d, 'SMA50': sma_50
                    })
            
            # ==================== SMART ALERTS (FILTRADOS) ====================
            tech_is_bearish = new_sugg in ['Venta', 'Venta Fuerte']
            
            already_alerted = any(a['Ticker'] == ticker for a in changes_to_alert)
            if not already_alerted and not tech_is_bearish:
                # 1. JOYA FUNDAMENTAL
                analyst_rating = row.get('Analyst Rating', '').lower()
                if fair_val > 0 and price > 0:
                    if upside_val > 40 and 'sell' not in analyst_rating and 'venta' not in analyst_rating:
                        changes_to_alert.append({
                            'Ticker': ticker, 'Old': 'N/A', 'New': f"Upside {upside_val}%", 
                            'Type': '💎 JOYA FUNDAMENTAL', 'Price': price, 'Rating': new_sugg,
                            'Upside': upside_val
                        })
                        already_alerted = True

            if not already_alerted and not tech_is_bearish:
                # 2. SOBREVENDIDO
                if rsi_1d < 25:
                     changes_to_alert.append({
                        'Ticker': ticker, 'Old': f"RSI {rsi_1d:.1f}", 'New': 'Rebote?', 
                        'Type': '📉 SOBREVENDIDO', 'Price': price, 'Rating': new_sugg,
                        'RSI': rsi_1d
                    })
                     already_alerted = True

            if not already_alerted:
                 # 3. VOLUMEN EXPLOSIVO
                 pct_day = row.get('Cambio % (día)', 0)
                 if vol_rel > 3.0 and pct_day > 0:
                     changes_to_alert.append({
                        'Ticker': ticker, 'Old': f"x{vol_rel} Vol", 'New': f"{pct_day}%", 
                        'Type': '🔊 VOLUMEN EXPLOSIVO', 'Price': price, 'Rating': new_sugg,
                        'VolRel': vol_rel
                    })

        # Guardar nuevo estado
        
        # Guardar nuevo estado
        save_current_state(current_state)
        
        # Enviar alerta si hay cambios
        if changes_to_alert:
            send_email_alert(changes_to_alert)
            
    except Exception as e:
        print(f"Error en sistema de alertas: {e}")

if __name__ == '__main__':
    main()
