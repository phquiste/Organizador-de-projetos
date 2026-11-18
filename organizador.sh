#!/usr/bin/env bash
# Uso: organizador.sh {1|2|3|parar}
# Cria o projeto do cliente na pasta mãe (~/Trabalho por padrão), copia os modelos
# e move os downloads para a 01_Brutos do projeto ativo.

# Pasta mãe dos projetos: ~/Trabalho, ou a escolhida no menu da bandeja (guardada no arquivo abaixo)
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/organizador.conf"
TRABALHO="$HOME/Trabalho"
PASTA_INDISPONIVEL=""
if [ -r "$CONFIG" ]; then
    read -r PASTA_ESCOLHIDA < "$CONFIG"
    if [ -n "$PASTA_ESCOLHIDA" ] && [ -d "$PASTA_ESCOLHIDA" ]; then
        TRABALHO="${PASTA_ESCOLHIDA%/}"
    else
        PASTA_INDISPONIVEL="$PASTA_ESCOLHIDA"
    fi
fi
# Modelos de projeto: pasta "Modelos" dentro da pasta mãe (criada quando preciso)
MODELOS="$TRABALHO/Modelos"
ESTADO="/tmp/organizador-$UID"
PID_FILE="$ESTADO/monitor.pid"
INFO_FILE="$ESTADO/projeto"
NOTIFY_FILE="$ESTADO/notificacao"
# Atalhos de pasta que aparecem na pasta mãe enquanto um projeto está ativo
ATALHO_BRUTOS="$TRABALHO/📦 BRUTOS"
ATALHO_FINAIS="$TRABALHO/✅ FINAIS"
ATALHO_PROJETOS="$TRABALHO/🛠️ PROJETOS"
# Nomes de versões anteriores: removidos se sobrarem (só se forem atalhos)
ATALHOS_ANTIGOS=("$TRABALHO/📂 ARQUIVOS BRUTOS" "$TRABALHO/✅ SALVAR EXPORT" "$TRABALHO/🛠️ SALVAR PROJETO")
TIMEOUT=10800
IGNORAR='(/\.[^/]*|\.(crdownload|part|tmp|opdownload|download|aria2))$'
AQUI="$(dirname "$(readlink -f "$0")")"

notificar() {
    command -v notify-send >/dev/null && notify-send -a Organizador "$@"
}

fechar_notificacao() {
    local id
    read -r id 2>/dev/null < "$NOTIFY_FILE"
    rm -f "$NOTIFY_FILE"
    [[ $id =~ ^[0-9]+$ ]] || return 0
    if command -v gdbus >/dev/null; then
        gdbus call --session --dest org.freedesktop.Notifications \
            --object-path /org/freedesktop/Notifications \
            --method org.freedesktop.Notifications.CloseNotification "$id" >/dev/null 2>&1
    elif command -v dbus-send >/dev/null; then
        dbus-send --session --dest=org.freedesktop.Notifications \
            /org/freedesktop/Notifications \
            org.freedesktop.Notifications.CloseNotification "uint32:$id" >/dev/null 2>&1
    fi
}

monitor_vivo() {
    local args
    [ -r "$PID_FILE" ] && read -r MONITOR_PID < "$PID_FILE" || return 1
    [[ $MONITOR_PID =~ ^[0-9]+$ ]] && [ -r "/proc/$MONITOR_PID/cmdline" ] || return 1
    mapfile -d '' -t args < "/proc/$MONITOR_PID/cmdline"
    [[ "${args[*]}" == *organizador.sh* ]]
}

parar_monitor() {
    if monitor_vivo; then
        kill "$MONITOR_PID" 2>/dev/null
        for _ in {1..20}; do
            kill -0 "$MONITOR_PID" 2>/dev/null || break
            sleep 0.05
        done
    fi
    rm -f "$PID_FILE"
}

remover_atalhos() {
    local antigo
    rm -f "$ATALHO_BRUTOS" "$ATALHO_FINAIS" "$ATALHO_PROJETOS"
    for antigo in "${ATALHOS_ANTIGOS[@]}"; do
        [ -L "$antigo" ] && rm -f "$antigo"
    done
}

# Só cria o atalho de pasta se a pasta existir; projeto retomado nunca ganha pastas novas.
atalho() {
    [ -d "$1" ] && ln -snf "$1" "$2"
}

mover() {
    local nome="$1" destino="$DESTINO/$1" hora
    if [ -e "$destino" ]; then
        printf -v hora '%(%H%M%S)T' -1
        if [[ $nome == *.* ]]; then
            destino="$DESTINO/${nome%.*}_$hora.${nome##*.}"
        else
            destino="$DESTINO/${nome}_$hora"
        fi
    fi
    mv -- "$DOWNLOADS/$nome" "$destino" 2>/dev/null
}

# Projeto novo: copia para a 02_Projetos tudo da pasta Modelos cujo nome contém o nome do cliente.
# Caixa, acento e _ - . não importam. Arquivos e pastas inteiras; itens ocultos são ignorados.
copiar_modelos() {
    mkdir -p "$MODELOS" 2>/dev/null
    [ -d "$MODELOS" ] && [ -d "$PROJETO/02_Projetos" ] || return 0
    python3 - "$MODELOS" "$PROJETO/02_Projetos" "$CLIENTE" <<'PY' ||
import re, shutil, sys, unicodedata
from pathlib import Path

def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto).casefold()
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", " ", texto).strip()

origem, destino, cliente = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
chave = f" {normalizar(cliente)} "
falhou = False
for item in sorted(origem.iterdir()):
    if item.name.startswith(".") or chave not in f" {normalizar(item.name)} ":
        continue
    alvo = destino / item.name
    if alvo.exists():
        continue
    try:
        if item.is_dir():
            shutil.copytree(item, alvo, symlinks=True)
        else:
            shutil.copy2(item, alvo)
    except OSError:
        falhou = True
sys.exit(1 if falhou else 0)
PY
        notificar -i dialog-warning "Modelos" "Não consegui copiar todos os modelos."
    return 0
}

monitorar() {
    coproc INOT {
        exec inotifywait -m -q -e close_write -e moved_to \
            --exclude "$IGNORAR" --format %f "$DOWNLOADS" 2>/dev/null
    }
    trap 'kill "$INOT_PID" 2>/dev/null' EXIT

    local arquivo status
    while true; do
        IFS= read -r -t "$TIMEOUT" -u "${INOT[0]}" arquivo
        status=$?
        [ "$status" -ne 0 ] && break
        [ -f "$DOWNLOADS/$arquivo" ] && mover "$arquivo"
    done

    rm -f "$PID_FILE" "$INFO_FILE"
    remover_atalhos
    fechar_notificacao
    if [ "$status" -gt 128 ]; then
        notificar -i process-stop "Monitoramento encerrado" "3 horas sem downloads."
    else
        notificar -i dialog-error "Monitoramento parou" "Erro ao vigiar a pasta de downloads."
    fi
}

parar() {
    if [ -f "$PID_FILE" ] || [ -f "$INFO_FILE" ]; then
        parar_monitor
        fechar_notificacao
        rm -f "$INFO_FILE"
        remover_atalhos
        notificar -i process-stop "Monitoramento parado" "Os downloads ficam na pasta Downloads."
    else
        notificar -i dialog-information "Organizador" "Nenhum projeto ativo."
    fi
}

mkdir -p -m 700 "$ESTADO"

case "${1:-}" in
    1|premier)    CLIENTE="Premier League" ;;
    2|magic)      CLIENTE="Orlando Magic" ;;
    3|jrnba)      CLIENTE="Jr. NBA Brasil" ;;
    0|parar|stop) parar; exit 0 ;;
    *)            notificar -i dialog-error "Argumento inválido" "${1:-}"; exit 1 ;;
esac

if ! command -v inotifywait >/dev/null; then
    notificar -i dialog-error "Falta o inotify-tools" "Veja o README."
    exit 1
fi

DOWNLOADS="$(xdg-user-dir DOWNLOAD 2>/dev/null)"
if [ ! -d "$DOWNLOADS" ] || [ "$DOWNLOADS" = "$HOME" ]; then
    DOWNLOADS="$HOME/Downloads"
fi

if [ -n "$PASTA_INDISPONIVEL" ]; then
    notificar -i dialog-warning "Pasta mãe não encontrada" "Usando ~/Trabalho. A pasta escolhida era: $PASTA_INDISPONIVEL"
fi
mkdir -p "$TRABALHO"
# GNOME usa a janela nativa (GTK4/libadwaita); o resto usa Qt.
# Código 2 = faltam as bibliotecas da janela, então tenta a próxima.
STATUS=2
if [[ ${XDG_CURRENT_DESKTOP:-} == *GNOME* ]]; then
    RESULTADO=$(python3 "$AQUI/organizador_dialog_gtk.py" "$CLIENTE" "$TRABALHO")
    STATUS=$?
fi
if [ "$STATUS" -eq 2 ]; then
    [[ ${XDG_CURRENT_DESKTOP:-} == *GNOME* ]] &&
        notificar -i dialog-warning "Janela nativa indisponível" "Rode o instalar.sh para instalar libadwaita e python-gobject."
    RESULTADO=$(python3 "$AQUI/organizador_dialog.py" "$CLIENTE" "$TRABALHO")
    STATUS=$?
fi
case $STATUS in
    0) ;;
    2|127) notificar -i dialog-error "Faltam bibliotecas da janela" "Rode o instalar.sh de novo."; exit 1 ;;
    *) exit 1 ;;
esac
[ -n "$RESULTADO" ] || exit 0

TIPO="${RESULTADO%%|*}"
VALOR="${RESULTADO#*|}"

case "$TIPO" in
    NOVO)
        printf -v DATA '%(%y-%m-%d)T' -1
        PROJETO="$TRABALHO/$DATA - $CLIENTE - $VALOR"
        mkdir -p "$PROJETO"/{01_Brutos,02_Projetos,03_Exports}
        copiar_modelos
        ;;
    EXISTENTE) PROJETO="$TRABALHO/$VALOR" ;;
    *) exit 0 ;;
esac

# Downloads vão para a 01_Brutos; se ela não existir (projeto antigo), para a raiz do projeto
DESTINO="$PROJETO"
[ -d "$PROJETO/01_Brutos" ] && DESTINO="$PROJETO/01_Brutos"

parar_monitor
fechar_notificacao
remover_atalhos
atalho "$DESTINO" "$ATALHO_BRUTOS"
atalho "$PROJETO/03_Exports" "$ATALHO_FINAIS"
atalho "$PROJETO/02_Projetos" "$ATALHO_PROJETOS"

# Escrita atômica: a bandeja nunca lê o arquivo pela metade
basename "$PROJETO" > "$INFO_FILE.tmp"
mv -f "$INFO_FILE.tmp" "$INFO_FILE"

id=$(notificar -p -t 5000 -i folder "Monitoramento ativo" "$(basename "$PROJETO")")
[ -n "$id" ] && echo "$id" > "$NOTIFY_FILE"

monitorar >/dev/null 2>&1 &
echo $! > "$PID_FILE"
disown
