"""OCR (reconocimiento de texto en imágenes) con Tesseract."""
import pytesseract
from PIL import Image
import io
import requests

def extraer_texto_desde_file_id(bot_token, file_id):
    """Descarga imagen de Telegram por file_id y extrae texto con OCR.
    
    Args:
        bot_token: Token del bot de Telegram
        file_id: ID del archivo de la imagen
    
    Returns:
        str: Texto extraído o mensaje de error
    """
    try:
        # Obtener ruta del archivo
        r = requests.get(f"https://api.telegram.org/bot{bot_token}/getFile",
                        params={"file_id": file_id}, timeout=10)
        if r.status_code != 200:
            return "❌ No pude obtener información del archivo"
        
        file_path = r.json()["result"]["file_path"]
        
        # Descargar imagen
        r = requests.get(f"https://api.telegram.org/file/bot{bot_token}/{file_path}",
                        timeout=30)
        if r.status_code != 200:
            return "❌ No pude descargar la imagen"
        
        # Abrir imagen
        img = Image.open(io.BytesIO(r.content))
        
        # OCR con español e inglés
        try:
            texto = pytesseract.image_to_string(img, lang='spa+eng')
        except Exception:
            texto = pytesseract.image_to_string(img, lang='eng')
        
        if not texto.strip():
            return "⚠️ No encontré texto en la imagen"
        
        return texto.strip()
    
    except Exception as e:
        return f"❌ Error en OCR: {str(e)[:100]}"

if __name__ == "__main__":
    print("✅ Módulo OCR listo")
    print("   Usa: extraer_texto_desde_file_id(bot_token, file_id)")


def preprocesar(img):
    """Grayscale + upscale + contraste + binarizado: mejora OCR en fotos reales."""
    from PIL import ImageOps
    img = img.convert('L')
    w, h = img.size
    img = img.resize((w * 2, h * 2), Image.LANCZOS)
    img = ImageOps.autocontrast(img)
    img = img.point(lambda p: 255 if p > 140 else 0)
    return img

def _ocr_variante(img, psm):
    for lang in ('spa+eng', 'eng'):
        try:
            return pytesseract.image_to_string(img, lang=lang, config=f'--psm {psm}').strip()
        except Exception:
            continue
    return ""

def extraer_texto_local(ruta):
    """OCR con preprocesamiento: prueba varias variantes y elige la mejor."""
    try:
        img = Image.open(ruta)
        mejor = ""
        for variante in (img, preprocesar(img)):
            for psm in (3, 6):
                t = _ocr_variante(variante, psm)
                if len(t) > len(mejor):
                    mejor = t
        return mejor or None
    except Exception as e:
        return f"❌ Error OCR: {str(e)[:100]}"
