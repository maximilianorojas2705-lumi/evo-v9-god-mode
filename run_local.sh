#!/data/data/com.termux/files/usr/bin/bash
# Cargar secrets del .secrets de artemis-bridge
source ~/artemis-bridge/.secrets 2>/dev/null

# Exportar para Flask
export BOT_TOKEN="${BOT_TOKEN:-}"
export GROQ_API_KEY="${GROQ_KEY:-}"
export GEMINI_API_KEY="${GEMINI_KEY:-}"
export SUPABASE_URL="${SUPABASE_URL:-}"
export SUPABASE_KEY="${SUPABASE_KEY:-}"

# Correr Flask local en puerto 5000
cd ~/evo-brain
python app.py
