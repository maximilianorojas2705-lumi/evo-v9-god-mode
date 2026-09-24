#!/data/data/com.termux/files/usr/bin/bash
# Supervisor: mantiene el cerebro local vivo para siempre
termux-wake-lock
while true; do
  echo "[supervisor] $(date) arrancando cerebro local..."
  bash ~/evo-brain/run_local.sh >> ~/evo-brain/cerebro.log 2>&1
  echo "[supervisor] $(date) cerebro cayo, reiniciando en 5s..." >> ~/evo-brain/cerebro.log
  sleep 5
done
