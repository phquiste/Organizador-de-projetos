# Organizador de projetos

Cria a pasta de cada projeto, move os downloads para o lugar certo e deixa atalhos para salvar projeto e export. Funciona em qualquer distro e ambiente gráfico (GNOME, KDE, XFCE...).

## O que ele faz

Ao apertar o atalho de um cliente, abre uma janela para criar um projeto novo ou retomar um antigo. No GNOME a janela é nativa (libadwaita, com tema claro/escuro e cor de destaque do sistema). Nos outros ambientes usa o visual nativo do Qt.

- **Premier League e Jr. NBA Brasil:** o projeto ganha `01_Brutos` (downloads, movidos sozinhos assim que terminam), `02_Projetos` e `03_Exports`.
- **Orlando Magic:** pasta única, sem subpastas. Tudo vai para a raiz do projeto.

Os projetos ficam em `~/Trabalho/` (a "pasta mãe"), a menos que você escolha outra (veja **Trocar a pasta mãe**). Enquanto o projeto está ativo, aparecem direto na pasta mãe os atalhos `🛠️ SALVAR PROJETO` e `✅ SALVAR EXPORT` (no Orlando Magic, só o `✅ SALVAR EXPORT`). Eles somem quando o monitor para.

Projeto retomado não é alterado: nenhuma pasta é criada ou recriada. Se a `01_Brutos` não existir mais, os downloads vão para a raiz do projeto. Um atalho só é criado se a pasta de destino existir.

## Instalar

Deixe estes 5 arquivos na mesma pasta: `instalar.sh`, `organizador.sh`, `organizador_dialog.py`, `organizador_dialog_gtk.py` e `organizador_tray.py`.

1. Abra a pasta no gerenciador de arquivos, clique com o botão direito num espaço vazio e escolha **Abrir no terminal**.
2. Rode:

   ```bash
   bash instalar.sh
   ```

3. Se faltar algum programa, o instalador mostra o comando da sua distro e pergunta se pode rodar. Responda `s` e digite sua senha.

O mesmo comando serve para atualizar: rode de novo com os arquivos novos.

Instalação manual, se preferir:

| Distro | Comando |
| :--- | :--- |
| Arch / CachyOS | `sudo pacman -S inotify-tools python-pyqt6 libnotify xdg-utils python-gobject libadwaita` |
| Ubuntu / Debian | `sudo apt install inotify-tools python3-pyqt6 libnotify-bin xdg-utils python3-gi gir1.2-adw-1` |
| Fedora | `sudo dnf install inotify-tools python3-pyqt6 libnotify xdg-utils python3-gobject libadwaita` |

(`python-gobject` e `libadwaita` só são usados no GNOME, para a janela nativa. Em KDE e outros, pode omitir.)

Depois copie os 4 arquivos `organizador*` para `~/.local/bin/` e dê permissão com `chmod +x ~/.local/bin/organizador*`.

## Atalhos de teclado

Use estes comandos exatamente como estão:

| Ação | Comando | GNOME | KDE |
| :--- | :--- | :--- | :--- |
| Premier League | `sh -c '$HOME/.local/bin/organizador.sh 1'` | `Ctrl+Alt+1` | `Meta+1` |
| Orlando Magic | `sh -c '$HOME/.local/bin/organizador.sh 2'` | `Ctrl+Alt+2` | `Meta+2` |
| Jr. NBA Brasil | `sh -c '$HOME/.local/bin/organizador.sh 3'` | `Ctrl+Alt+3` | `Meta+3` |
| Parar | `sh -c '$HOME/.local/bin/organizador.sh parar'` | `Ctrl+Alt+0` | `Meta+0` |

**GNOME:** Configurações → Teclado → Ver e personalizar atalhos → Atalhos personalizados → botão **+**. Preencha o nome, cole o comando e defina as teclas. Evite `Super+número`: o GNOME já usa essas teclas para os apps da barra.

**KDE:** Configurações do Sistema → Atalhos → Adicionar novo → Comando ou script.

**Outros ambientes:** procure em Configurações → Teclado a opção de atalho personalizado.

## Trocar a pasta mãe

Por padrão os projetos ficam em `~/Trabalho`. Para usar outra pasta (um HD externo, por exemplo):

1. Clique na bolinha e escolha **Pasta mãe dos projetos**.
2. Escolha a pasta e confirme.

A escolha vale para todos os projetos seguintes e só muda quando você trocar de novo. Para voltar ao padrão, escolha `~/Trabalho` outra vez.

- Só dá para trocar com o monitoramento parado. Com um projeto ativo, o programa avisa e pede para parar antes.
- Projetos antigos continuam na pasta anterior. A lista "Retomar projeto" mostra só os da pasta mãe atual.
- Se a pasta escolhida sumir (HD desconectado, por exemplo), o programa avisa e usa `~/Trabalho` até ela voltar.

## Bandeja no GNOME

O GNOME não mostra ícones de bandeja sem uma extensão (o Ubuntu já vem com ela). Se a bolinha não aparecer:

1. Instale a extensão:
   - Arch / CachyOS: `sudo pacman -S gnome-shell-extension-appindicator`
   - Ubuntu / Debian: `sudo apt install gnome-shell-extension-appindicator`
   - Fedora: `sudo dnf install gnome-shell-extension-appindicator`
2. Saia da sessão e entre de novo.
3. Ative:

   ```bash
   gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com
   ```

No GNOME o clique esquerdo na bolinha abre o menu, e a pasta do projeto abre por **Abrir pasta do projeto**. No KDE o clique esquerdo já abre a pasta. A bandeja é opcional: os atalhos de teclado funcionam sem ela.

## Uso

1. Aperte o atalho do cliente, ou clique na bolinha e escolha o cliente.
2. Digite o nome de um projeto novo e aperte `Enter`, ou use `↓` para escolher um antigo e aperte `Enter`.
3. Tudo que você baixar vai para o projeto ativo.

Bolinha cinza: nenhum projeto ativo. Verde: projeto ativo.

## Perguntas

**Ele apaga arquivos?** Nunca. Só move downloads e cria ou remove os atalhos.

**E se eu esquecer o monitor ligado?** Sem downloads por 3 horas ele desliga sozinho e remove os atalhos. Se o PC reiniciar com um projeto ativo, a bandeja limpa os atalhos que sobraram (só links, nunca arquivos).

**Qual pasta de downloads ele vigia?** A configurada no sistema, mesmo em outro idioma.

**Quais arquivos ele ignora?** Downloads incompletos (`.crdownload`, `.part`, `.tmp`, `.opdownload`, `.download`, `.aria2`) e arquivos ocultos.

## Onde ficam os arquivos

Tudo que o programa coloca no seu computador, para você saber onde está cada coisa.

| Onde | Arquivo | Para que serve |
| :--- | :--- | :--- |
| `~/.local/bin/` | `organizador.sh` | Cria o projeto e move os downloads |
| `~/.local/bin/` | `organizador_dialog.py` | Janela de escolha de projeto (KDE e outros) |
| `~/.local/bin/` | `organizador_dialog_gtk.py` | Janela de escolha de projeto (GNOME) |
| `~/.local/bin/` | `organizador_tray.py` | A bolinha da bandeja |
| `~/.config/autostart/` | `organizador-tray.desktop` | Faz a bolinha abrir sozinha ao ligar o PC |
| `~/.local/share/applications/` | `local.organizador.dialogo.desktop` | Dá nome e ícone à janela no GNOME (só estético) |
| `/tmp/organizador-<número>/` | `monitor.pid`, `projeto`, `notificacao`, `bandeja.lock` | Bilhetes temporários entre as peças. Somem ao reiniciar o PC |
| `~/.config/` | `organizador.conf` | Guarda a pasta mãe escolhida. Só existe se você trocar a pasta |
| Pasta mãe (`~/Trabalho/` por padrão) | `🛠️ SALVAR PROJETO`, `✅ SALVAR EXPORT` | Atalhos que só existem enquanto um projeto está ativo |

Fora disso:

- **Seus projetos** (as pastas dentro de `~/Trabalho/`) são o seu trabalho, não arquivos do programa. Nunca são apagados.
- **Na pasta de onde você instalou** ficam o `instalar.sh`, o `README.md` e as cópias originais dos arquivos. Depois de instalar dá para apagar, mas guarde se quiser reinstalar ou atualizar.
- **Programas do sistema** instalados pelo `instalar.sh` (como `inotify-tools` e `python-pyqt6`) ficam no sistema, não em pastas suas. No GNOME, a extensão AppIndicator também fica no sistema.

## Desinstalar

1. Pare o monitoramento e feche a bolinha (menu da bolinha → **Parar monitoramento**, depois **Sair da bandeja**).
2. Rode no terminal:

   ```bash
   rm ~/.local/bin/organizador*
   rm ~/.config/autostart/organizador-tray.desktop
   rm ~/.local/share/applications/local.organizador.dialogo.desktop
   rm -f ~/.config/organizador.conf
   rm -rf /tmp/organizador-*
   ```

Seus projetos continuam na pasta mãe. Se sobrar algum atalho `🛠️ SALVAR PROJETO` ou `✅ SALVAR EXPORT` nela, pode apagar: são só links.
