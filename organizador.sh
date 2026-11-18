#!/usr/bin/env bash
# Uso: organizador.sh {número do cliente | nome do cliente | parar | listar | modelos}
# Cria o projeto do cliente na pasta mãe (~/Trabalho por padrão), copia os modelos
# e move os downloads para a 01_Brutos do projeto ativo.
# Os clientes são as subpastas da pasta Modelos (ex.: "1 - Premier League").

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
# Pasta "Modelos" dentro da pasta mãe: uma subpasta por cliente, com os modelos de projeto dele.
# O número no começo do nome ("1 - Nome") é o número do atalho de teclado; sem número, o cliente
# só aparece no menu da bandeja. Se não houver nenhuma subpasta, usa (e cria) esta lista padrão.
MODELOS="$TRABALHO/Modelos"
CLIENTES_PADRAO=("1 - Premier League" "2 - Orlando Magic" "3 - Jr. NBA Brasil")
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

# Preenche CLI_ARGS (número do atalho, ou o nome se não tiver), CLI_NOMES e CLI_PASTAS com os
# clientes: as subpastas de Modelos, numeradas primeiro (1, 2, 10...) e depois as sem número.
# Sem nenhuma subpasta, usa a lista padrão (sem criar nada).
carregar_clientes() {
    CLI_ARGS=(); CLI_NOMES=(); CLI_PASTAS=()
    local pasta nome num
    local -a achadas=()
    local -A usados=()
    local padrao='^([0-9]{1,4})[[:space:]]+(-|–|—)[[:space:]]+(.+)$'
    if [ -d "$MODELOS" ]; then
        while IFS= read -r -d '' pasta; do
            achadas+=("${pasta##*/}")
        done < <(find "$MODELOS" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 | LC_ALL=C sort -z -V)
    fi
    [ "${#achadas[@]}" -gt 0 ] || achadas=("${CLIENTES_PADRAO[@]}")
    for pasta in "${achadas[@]}"; do
        nome="$pasta"; num=""
        if [[ $pasta =~ $padrao ]]; then
            num=$((10#${BASH_REMATCH[1]}))
            nome="${BASH_REMATCH[3]}"
            # O 0 é reservado (parar); número repetido só vale para a primeira pasta
            if [ "$num" -eq 0 ] || [ -n "${usados[$num]:-}" ]; then num=""; else usados[$num]=1; fi
        fi
        CLI_ARGS+=("${num:-$nome}"); CLI_NOMES+=("$nome"); CLI_PASTAS+=("$pasta")
    done
}

# Uma linha por cliente: argumento, tab, nome (usado pela bandeja e pelo instalar.sh)
listar_clientes() {
    local i
    carregar_clientes
    for i in "${!CLI_ARGS[@]}"; do
        printf '%s\t%s\n' "${CLI_ARGS[i]}" "${CLI_NOMES[i]}"
    done
}

# Garante a pasta Modelos e, se ela não tem nenhum cliente, cria as pastas da lista padrão.
preparar_modelos() {
    local pasta
    mkdir -p "$MODELOS" 2>/dev/null || return 1
    if [ -z "$(find "$MODELOS" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print -quit)" ]; then
        for pasta in "${CLIENTES_PADRAO[@]}"; do
            mkdir -p "$MODELOS/$pasta"
        done
    fi
}

# Projeto novo: copia para a 02_Projetos tudo que está na pasta do cliente em Modelos.
# O arquivo recebe o nome do projeto (se houver mais de um do mesmo tipo, o nome do projeto
# seguido do nome original). Pastas mantêm o nome. Itens ocultos são ignorados.
copiar_modelos() {
    local origem="$MODELOS/$PASTA_CLIENTE"
    [ -d "$origem" ] && [ -d "$PROJETO/02_Projetos" ] || return 0
    python3 - "$origem" "$PROJETO/02_Projetos" "$(basename "$PROJETO")" <<'PY' ||
import shutil, sys
from collections import Counter
from pathlib import Path

origem, destino, projeto = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
itens = [i for i in sorted(origem.iterdir()) if not i.name.startswith(".")]
tipos = Counter(i.suffix.casefold() for i in itens if not i.is_dir())
falhou = False
for item in itens:
    if item.is_dir():
        nome = item.name
    elif tipos[item.suffix.casefold()] == 1:
        nome = projeto + item.suffix
    else:
        nome = f"{projeto} - {item.stem}{item.suffix}"
    alvo = destino / nome
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
    0|parar|stop) parar; exit 0 ;;
    listar)       listar_clientes; exit 0 ;;
    modelos)      preparar_modelos && echo "$MODELOS"; exit ;;
    "")           notificar -i dialog-error "Argumento inválido" "Informe o número ou o nome do cliente."; exit 1 ;;
esac

# Acha o cliente pelo número (ou pelo nome) entre as pastas de Modelos
carregar_clientes
ARG="$1"
[[ $ARG =~ ^[0-9]{1,4}$ ]] && ARG=$((10#$ARG))
CLIENTE=""
for i in "${!CLI_ARGS[@]}"; do
    if [ "${CLI_ARGS[i]}" = "$ARG" ] || [ "${CLI_NOMES[i]}" = "$1" ]; then
        CLIENTE="${CLI_NOMES[i]}"
        PASTA_CLIENTE="${CLI_PASTAS[i]}"
        break
    fi
done
if [ -z "$CLIENTE" ]; then
    notificar -i dialog-error "Cliente não encontrado" "$1 (veja as pastas em $MODELOS)"
    exit 1
fi

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
        preparar_modelos
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
