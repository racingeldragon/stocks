from analisis_profesional import send_email_alert

print("🚀 Iniciando prueba de email con DESCRIPCIONES LARGAS y LINKS...")

# Datos de prueba simulados con métricas técnicas
test_changes = [
    {
        'Ticker': 'AAPL',
        'Old': 'Venta',
        'New': 'Compra Fuerte',
        'Type': 'OPORTUNIDAD',
        'Price': 195.50,
        'Rating': 'Compra Fuerte',
        'RSI': 55.4,
        'MACD': 1.2
    },
    {
        'Ticker': 'NVDA',
        'Old': 'N/A',
        'New': 'Upside 45.2%',
        'Type': '💎 JOYA FUNDAMENTAL',
        'Price': 120.00,
        'Rating': 'Mantener',
        'Upside': 45.2
    },
    {
        'Ticker': 'TSLA',
        'Old': 'Compra',
        'New': 'Venta Fuerte',
        'Type': 'VENTA NECESARIA',
        'Price': 180.00,
        'Rating': 'Venta Fuerte',
        'SMA50': 210.50
    },
    {
        'Ticker': 'BABA',
        'Old': 'RSI 22.5',
        'New': 'Rebote?',
        'Type': '� SOBREVENDIDO',
        'Price': 75.20,
        'Rating': 'Mantener',
        'RSI': 22.1
    },
    {
        'Ticker': 'GE',
        'Old': 'x4.5 Vol',
        'New': '5.4%',
        'Type': '🔊 VOLUMEN EXPLOSIVO',
        'Price': 150.50,
        'Rating': 'Compra',
        'VolRel': 4.5
    }
]

try:
    send_email_alert(test_changes)
    print("\n✅ Prueba finalizada con éxito.")
except Exception as e:
    print(f"\n❌ Error durante la prueba: {e}")
