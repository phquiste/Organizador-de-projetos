#!/bin/bash
# =====================================================================
#  organizador.sh - Organizador de projetos + monitor de Downloads
# =====================================================================

SCRIPT_NAME="$(basename "$0")"
PID_FILE="/tmp/monitor_downloads.pid"
INFO_FILE="/tmp/projeto_ativo.txt"
NOTIFY_ID_FILE="/tmp/notify_id.txt"
DOWNLOADS_DIR="$HOME/Downloads"
TRABALHO_DIR="$HOME/Trabalho"
TIMEOUT=10800   # 3 horas sem downloads = encerra automaticamente

DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null)"
[ -z "$DESKTOP_DIR" ] || [ ! -d "$DESKTOP_DIR" ] && DESKTOP_DIR="$HOME/Área de trabalho"
[ ! -d "$DESKTOP_DIR" ] && DESKTOP_DIR="$HOME/Desktop"

ATALHO_PROJETO="$DESKTOP_DIR/🛠️ SALVAR PROJETO"
ATALHO_EXPORT="$DESKTOP_DIR/✅ SALVAR EXPORT"

# ---------------------------------------------------------------------
# Seleção de cliente / comando
# ---------------------------------------------------------------------
MODO_PARAR=0
case "$1" in
    1|premier)    CLIENTE="Premier League" ;;
    2|magic)      CLIENTE="Orlando Magic" ;;
    3|jrnba)      CLIENTE="Jr. NBA Brasil" ;;
    0|parar|stop) MODO_PARAR=1 ;;
    *)
        notify-send -a "Organizador" -i dialog-error "Erro no Organizador" "Argumento inválido: '$1'" 2>/dev/null
        exit 1
        ;;
esac

# ---------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------
fechar_notificacao() {
    [ -f "$NOTIFY_ID_FILE" ] || return 0
    local NID
    NID=$(<"$NOTIFY_ID_FILE")
    if [ -n "$NID" ]; then
        gdbus call --session --dest org.freedesktop.Notifications \
            --object-path /org/freedesktop/Notifications \
            --method org.freedesktop.Notifications.CloseNotification "$NID" \
            >/dev/null 2>&1 || true
    fi
    rm -f "$NOTIFY_ID_FILE"
}

parar_monitor() {
    if [ -f "$PID_FILE" ]; then
        local OLD_PID
        OLD_PID=$(<"$PID_FILE")
        if [ -n "$OLD_PID" ] && grep -qa "$SCRIPT_NAME" "/proc/$OLD_PID/cmdline" 2>/dev/null; then
            kill "$OLD_PID" 2>/dev/null || true
            # Aguarda o encerramento limpo sem sleep fixo desnecessário
            for _ in {1..10}; do
                kill -0 "$OLD_PID" 2>/dev/null || break
                sleep 0.05
            done
        fi
        rm -f "$PID_FILE"
    fi
}

limpar_tudo() {
    parar_monitor
    fechar_notificacao
    rm -f "$INFO_FILE" "$ATALHO_PROJETO" "$ATALHO_EXPORT"
}

mover_arquivo() {
    local ARQUIVO="$1"
    local ORIGEM="$DOWNLOADS_DIR/$ARQUIVO"
    [ -f "$ORIGEM" ] || return 0

    local DESTINO="$PASTA_DOWNLOADS/$ARQUIVO"
    if [ -e "$DESTINO" ]; then
        local NOME_BASE="${ARQUIVO%.*}"
        local EXT="${ARQUIVO##*.}"
        local TIMESTAMP
        TIMESTAMP=$(date +%H%M%S)
        if [ "$NOME_BASE" = "$EXT" ] || [ -z "$EXT" ]; then
            DESTINO="$PASTA_DOWNLOADS/${ARQUIVO}_${TIMESTAMP}"
        else
            DESTINO="$PASTA_DOWNLOADS/${NOME_BASE}_${TIMESTAMP}.${EXT}"
        fi
    fi

    mv -- "$ORIGEM" "$DESTINO" 2>/dev/null || true
}

monitorar() {
    coproc INOT {
        exec inotifywait -m -q -e close_write -e moved_to --format "%f" "$DOWNLOADS_DIR" 2>/dev/null
    }
    trap 'kill "$INOT_PID" 2>/dev/null || true' EXIT

    local ARQUIVO STATUS
    while true; do
        IFS= read -r -t "$TIMEOUT" -u "${INOT[0]}" ARQUIVO
        STATUS=$?
        [ "$STATUS" -ne 0 ] && break

        case "$ARQUIVO" in
            ""|.*|*.crdownload|*.part|*.tmp) continue ;;
        esac

        mover_arquivo "$ARQUIVO"
    done

    rm -f "$PID_FILE" "$INFO_FILE" "$ATALHO_PROJETO" "$ATALHO_EXPORT"
    fechar_notificacao

    if [ "$STATUS" -gt 128 ]; then
        notify-send -a "Organizador" -i process-stop "🔴 Monitoramento Inativo" "3 horas sem downloads. Projeto desativado."
    else
        notify-send -a "Organizador" -i dialog-error "⚠️ Monitoramento parou" "Erro ao vigiar a pasta Downloads."
    fi
}

# ---------------------------------------------------------------------
# Modo Parar
# ---------------------------------------------------------------------
if [ "$MODO_PARAR" -eq 1 ]; then
    if [ -f "$PID_FILE" ] || [ -f "$INFO_FILE" ]; then
        limpar_tudo
        notify-send -a "Organizador" -i process-stop "⏹️ Monitoramento parado" "Os downloads ficam na pasta Downloads."
    else
        notify-send -a "Organizador" -i dialog-information "Organizador" "Nenhum projeto estava ativo."
    fi
    exit 0
fi

# ---------------------------------------------------------------------
# 1. Janela de seleção (PyQt6)
# ---------------------------------------------------------------------
mkdir -p "$TRABALHO_DIR"

RESULTADO=$(python3 - "$CLIENTE" "$TRABALHO_DIR" << 'PYEOF'
import os
import sys
from pathlib import Path
from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QPushButton, QVBoxLayout
)

cliente = sys.argv[1]
trabalho_dir = Path(sys.argv[2])

pastas = sorted(
    (p.name for p in trabalho_dir.glob(f"* - {cliente} - *") if p.is_dir()),
    reverse=True,
)

app = QApplication(sys.argv)
dlg = QDialog()
dlg.setWindowTitle(f"Organizador — {cliente}")
dlg.setMinimumWidth(460)

layout = QVBoxLayout(dlg)

layout.addWidget(QLabel("<b>Novo projeto</b> (digite o nome e aperte Enter):"))
input_nome = QLineEdit()
input_nome.setPlaceholderText("Ex: Jogo 1 vs Celtics")
layout.addWidget(input_nome)

lbl_lista = QLabel("<b>Ou selecione um existente</b> (Setas ↓/↑ ou duplo clique):")
layout.addWidget(lbl_lista)

lista = QListWidget()
lista.addItems(pastas)
if not pastas:
    lista.setEnabled(False)
    lbl_lista.setText("<i>Nenhum projeto anterior encontrado para este cliente.</i>")
layout.addWidget(lista)

btn_layout = QHBoxLayout()
btn_cancelar = QPushButton("Cancelar")
btn_ok = QPushButton("Confirmar")
btn_ok.setDefault(True)
btn_layout.addStretch()
btn_layout.addWidget(btn_cancelar)
btn_layout.addWidget(btn_ok)
layout.addLayout(btn_layout)

escolha = {"tipo": None, "valor": ""}

def confirmar():
    texto = input_nome.text().strip()
    if texto:
        escolha["tipo"] = "NOVO"
        escolha["valor"] = texto
        dlg.accept()
    elif lista.currentItem() is not None:
        escolha["tipo"] = "EXISTENTE"
        escolha["valor"] = lista.currentItem().text()
        dlg.accept()

class KeyFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if obj is input_nome and event.key() == Qt.Key.Key_Down and lista.count() > 0:
                lista.setFocus()
                if lista.currentRow() < 0:
                    lista.setCurrentRow(0)
                return True
            if obj is lista and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                confirmar()
                return True
        return super().eventFilter(obj, event)

filtro = KeyFilter(dlg)
input_nome.installEventFilter(filtro)
lista.installEventFilter(filtro)

input_nome.textChanged.connect(lambda t: lista.clearSelection() if t.strip() else None)
lista.itemClicked.connect(lambda _: input_nome.clear())
lista.itemDoubleClicked.connect(lambda _: confirmar())

btn_ok.clicked.connect(confirmar)
btn_cancelar.clicked.connect(dlg.reject)

input_nome.setFocus()
if dlg.exec() == QDialog.DialogCode.Accepted and escolha["tipo"]:
    print(f"{escolha['tipo']}|{escolha['valor']}")
PYEOF
)

[ -z "$RESULTADO" ] && exit 0

TIPO="${RESULTADO%%|*}"
VALOR="${RESULTADO#*|}"

if [ "$TIPO" = "NOVO" ]; then
    DATA=$(date +%y-%m-%d)
    # Remove apenas caracteres proibidos em nomes de pasta (/ e :) preservando espaços
    NOME_LIMPO=$(printf '%s' "$VALOR" | tr '/:' '--' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    PASTA_PROJETO="$TRABALHO_DIR/${DATA} - ${CLIENTE} - ${NOME_LIMPO}"
    if [ "$CLIENTE" = "Orlando Magic" ]; then
        mkdir -p "$PASTA_PROJETO"
    else
        mkdir -p "$PASTA_PROJETO/"{01_Brutos,02_Projetos,03_Exports}
    fi
elif [ "$TIPO" = "EXISTENTE" ]; then
    PASTA_PROJETO="$TRABALHO_DIR/$VALOR"
else
    exit 0
fi

if [ "$CLIENTE" = "Orlando Magic" ]; then
    PASTA_DOWNLOADS="$PASTA_PROJETO"
    DESTINO_LABEL="pasta do projeto"
else
    PASTA_DOWNLOADS="$PASTA_PROJETO/01_Brutos"
    DESTINO_LABEL="01_Brutos"
fi

# ---------------------------------------------------------------------
# 2. Encerra monitoramento anterior e ativa o novo projeto
# ---------------------------------------------------------------------
parar_monitor
fechar_notificacao

rm -f "$ATALHO_PROJETO" "$ATALHO_EXPORT"
if [ "$CLIENTE" = "Orlando Magic" ]; then
    ln -snf "$PASTA_PROJETO" "$ATALHO_EXPORT"
else
    ln -snf "$PASTA_PROJETO/02_Projetos" "$ATALHO_PROJETO"
    ln -snf "$PASTA_PROJETO/03_Exports" "$ATALHO_EXPORT"
fi

# Escrita atômica para o QFileSystemWatcher da bandeja nunca ler arquivo vazio
NOME_PROJETO_ATIVO=$(basename "$PASTA_PROJETO")
printf '%s\n' "$NOME_PROJETO_ATIVO" > "${INFO_FILE}.tmp"
mv -f "${INFO_FILE}.tmp" "$INFO_FILE"

NOTIFY_OUTPUT=$(notify-send -p -t 5000 -a "Organizador" -i folder-sync "🟢 Projeto Ativo: $CLIENTE" "$NOME_PROJETO_ATIVO"$'\n'"(Downloads indo para $DESTINO_LABEL)")
[ -n "$NOTIFY_OUTPUT" ] && printf '%s\n' "$NOTIFY_OUTPUT" > "$NOTIFY_ID_FILE"

# ---------------------------------------------------------------------
# 3. Inicia monitoramento em background
# ---------------------------------------------------------------------
monitorar >/dev/null 2>&1 &
printf '%s\n' "$!" > "$PID_FILE"
