#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🚀 [1/4] Actualizando e instalando dependencias..."
pkg update -y
pkg install -y android-tools python libjpeg-turbo libpng tesseract-ocr

echo "📦 [2/4] Instalando uiautomator2 y paquetes auxiliares..."
pip install --upgrade pip
pip install uiautomator2 pillow pytesseract duckduckgo-search trafilatura

echo "🔧 [3/4] Iniciando servidor ADB local..."
adb start-server

echo "✅ [4/4] Instalación terminada."
echo ""
echo "📱 INSTRUCCIONES PARA VINCULAR ADB LOCAL:"
echo "1. Opciones de Desarrollador → Depuración inalámbrica → activar"
echo "2. Adentro: 'Vincular dispositivo con código' → anotar PUERTO y CÓDIGO"
echo "3. En Termux (rápido, expira en 1 min):"
echo "   adb pair 127.0.0.1:PUERTO_QUE_DICE"
echo "   (te pide el código de 6 dígitos)"
echo "4. Después: adb connect 127.0.0.1:5555"
echo "5. Verificar: adb devices"
