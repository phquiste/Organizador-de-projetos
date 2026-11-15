#!/usr/bin/env bash
# Instala (ou atualiza) o Organizador. Rode na pasta dos arquivos: bash instalar.sh

set -u

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$HOME/.local/bin"
AUTOSTART="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"
ARQUIVOS=(organizador.sh organizador_dialog.py organizador_dialog_gtk.py organizador_tray.py)

for f in "${ARQUIVOS[@]}"; do
    [ -f "$AQUI/$f" ] || { echo "Não encontrei $f em $AQUI. Deixe os arquivos juntos na mesma pasta."; exit 1; }
done

faltando=0
extra_gnome=0
for cmd in inotifywait notify-send xdg-open xdg-user-dir python3; do
    command -v "$cmd" >/dev/null || faltando=1
done
python3 -c "import PyQt6.QtWidgets" 2>/dev/null || faltando=1

# No GNOME a janela é nativa (GTK4 + libadwaita)
if [[ ${XDG_CURRENT_DESKTOP:-} == *GNOME* ]]; then
    python3 -c "import gi; gi.require_version('Adw', '1'); from gi.repository import Adw; Adw.EntryRow" 2>/dev/null \
        || { faltando=1; extra_gnome=1; }
fi

if [ "$faltando" -eq 1 ]; then
    if command -v pacman >/dev/null; then
        CMD="sudo pacman -S --needed inotify-tools python python-pyqt6 libnotify xdg-utils xdg-user-dirs"
        [ "$extra_gnome" -eq 1 ] && CMD="$CMD python-gobject libadwaita"
    elif command -v apt >/dev/null; then
        CMD="sudo apt install -y inotify-tools python3 python3-pyqt6 libnotify-bin xdg-utils xdg-user-dirs"
        [ "$extra_gnome" -eq 1 ] && CMD="$CMD python3-gi gir1.2-adw-1"
    elif command -v dnf >/dev/null; then
        CMD="sudo dnf install -y inotify-tools python3 python3-pyqt6 libnotify xdg-utils xdg-user-dirs"
        [ "$extra_gnome" -eq 1 ] && CMD="$CMD python3-gobject libadwaita"
    elif command -v zypper >/dev/null; then
        CMD="sudo zypper install -y inotify-tools python3 python3-qt6 libnotify-tools xdg-utils xdg-user-dirs"
        [ "$extra_gnome" -eq 1 ] && CMD="$CMD python3-gobject typelib-1_0-Adw-1"
    else
        echo "Distro não reconhecida. Instale: inotify-tools, python3, PyQt6, libnotify e xdg-utils (no GNOME, também python-gobject e libadwaita)."
        exit 1
    fi
    echo "Faltam programas. Comando de instalação (pede sua senha):"
    echo "  $CMD"
    read -r -p "Rodar agora? [s/N] " resposta
    case "$resposta" in
        s|S) $CMD || { echo "A instalação falhou."; exit 1; } ;;
        *) echo "Rode o comando acima e execute o instalar.sh de novo."; exit 1 ;;
    esac
fi

mkdir -p "$BIN" "$AUTOSTART"
for f in "${ARQUIVOS[@]}"; do
    install -m 755 "$AQUI/$f" "$BIN/$f"
done

printf '%s\n' \
    '[Desktop Entry]' \
    'Type=Application' \
    'Name=Organizador' \
    "Exec=$BIN/organizador_tray.py" \
    'Terminal=false' \
    'X-GNOME-Autostart-enabled=true' \
    > "$AUTOSTART/organizador-tray.desktop"

# Identidade da janela no GNOME (nome e ícone no Alt+Tab e no dock); não aparece no menu de apps
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$APPS"
printf '%s\n' \
    '[Desktop Entry]' \
    'Type=Application' \
    'Name=Organizador' \
    'Icon=folder' \
    'NoDisplay=true' \
    "Exec=$BIN/organizador.sh" \
    > "$APPS/local.organizador.dialogo.desktop"

# Reinicia a bandeja para pegar a versão nova
pkill -f organizador_tray.py 2>/dev/null
sleep 0.3
setsid nohup "$BIN/organizador_tray.py" >/dev/null 2>&1 &

case "${XDG_CURRENT_DESKTOP:-}" in
    *GNOME*)
        gnome-extensions list 2>/dev/null | grep -qi appindicator || {
            echo
            echo "GNOME: para a bolinha aparecer, ative a extensão AppIndicator (veja o README)."
        } ;;
esac

echo
echo "Pronto. Comandos para os atalhos de teclado:"
echo "  Premier League : sh -c '\$HOME/.local/bin/organizador.sh 1'"
echo "  Orlando Magic  : sh -c '\$HOME/.local/bin/organizador.sh 2'"
echo "  Jr. NBA Brasil : sh -c '\$HOME/.local/bin/organizador.sh 3'"
echo "  Parar          : sh -c '\$HOME/.local/bin/organizador.sh parar'"
