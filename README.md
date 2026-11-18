# Organizador de projetos

Cria a pasta de cada projeto, move os downloads para o lugar certo, copia os modelos do cliente e deixa atalhos de pasta para os brutos, os projetos e os finais. Funciona em qualquer distro e ambiente gráfico (GNOME, KDE, XFCE...).

## O que ele faz

Ao apertar o atalho de teclado de um cliente, abre uma janela para criar um projeto novo ou retomar um antigo. No GNOME a janela é nativa (libadwaita, com tema claro/escuro e cor de destaque do sistema). Nos outros ambientes usa o visual nativo do Qt.

Todo projeto novo, de qualquer cliente, ganha as mesmas três subpastas: `01_Brutos` (downloads, movidos sozinhos assim que terminam), `02_Projetos` e `03_Exports`.

Os projetos ficam em `~/Trabalho/` (a "pasta mãe"), a menos que você escolha outra (veja **Trocar a pasta mãe**). Enquanto o projeto está ativo, aparecem direto na pasta mãe três atalhos de pasta:

| Atalho de pasta | Leva para | Use para |
| :--- | :--- | :--- |
| `📦 BRUTOS` | `01_Brutos`, onde os downloads caem | Indicar os brutos no Photoshop e em outros programas |
| `✅ FINAIS` | `03_Exports` | Salvar o export |
| `🛠️ PROJETOS` | `02_Projetos` | Salvar o projeto |

Os atalhos de pasta somem quando o monitor para.

Projeto retomado não é alterado: nenhuma pasta é criada ou recriada. Se a `01_Brutos` não existir mais, os downloads vão para a raiz do projeto. Um atalho de pasta só é criado se a pasta de destino existir.

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

Use estes comandos exatamente como estão, **sem aspas e sem `sh -c`**. Eles servem no GNOME e no KDE. Troque `SEU_USUARIO` pelo seu nome de usuário (o `instalar.sh` mostra os comandos já prontos no final, é só copiar):

| Ação | Comando | Tecla |
| :--- | :--- | :--- |
| Premier League | `/home/SEU_USUARIO/.local/bin/organizador.sh 1` | `Ctrl+1` |
| Orlando Magic | `/home/SEU_USUARIO/.local/bin/organizador.sh 2` | `Ctrl+2` |
| Jr. NBA Brasil | `/home/SEU_USUARIO/.local/bin/organizador.sh 3` | `Ctrl+3` |
| Parar | `/home/SEU_USUARIO/.local/bin/organizador.sh parar` | `Ctrl+'` (apóstrofo) |

As teclas são as mesmas no GNOME e no KDE. Atenção: `Ctrl+número` também é usado por navegadores (trocar de aba) e por alguns programas. Como o atalho é global, ele vale em qualquer lugar e pode tomar essas teclas. Se isso atrapalhar, troque por `Ctrl+Alt+1`, `2`, `3` e `0`.

Por que o caminho completo: GNOME e KDE não interpretam `$HOME`, `~` nem aspas do mesmo jeito que o terminal. O caminho completo é lido igual nos dois.

**GNOME:** Configurações → Teclado → Ver e personalizar atalhos → Atalhos personalizados → botão **+**. Preencha o nome, cole o comando e defina as teclas.

**KDE:** Configurações do Sistema → Atalhos → Adicionar novo → Comando ou script. Cole o comando e defina as teclas.

**Outros ambientes:** procure em Configurações → Teclado a opção de atalho personalizado.

## Uso

1. Aperte o atalho de teclado do cliente, ou clique na bolinha e escolha o cliente.
2. Digite o nome de um projeto novo e aperte `Enter`, ou use `↓` para escolher um antigo e aperte `Enter`.
3. Tudo que você baixar vai para o projeto ativo. Para salvar e importar arquivos, use os atalhos de pasta da pasta mãe: `📦 BRUTOS`, `✅ FINAIS` e `🛠️ PROJETOS`.

Bolinha cinza: nenhum projeto ativo. Verde: projeto ativo.

## Modelos de projeto

Dentro da pasta mãe existe uma pasta chamada `Modelos` (`~/Trabalho/Modelos` por padrão). Coloque nela os seus projetos modelo, de qualquer programa (`.psd`, `.fcproj` etc.), em arquivos ou em pastas inteiras.

Ao criar um projeto **novo**, o programa copia para a `02_Projetos` os modelos cujo nome contém o nome do cliente: `Premier League`, `Orlando Magic` ou `Jr. NBA Brasil`. Maiúsculas, acentos e os caracteres `_`, `-` e `.` não importam, então `Premier_League.fcproj` serve para a Premier League. Se mais de um modelo combinar, todos são copiados, com o nome original e sem mudar o conteúdo.

- Só entram os itens que ficam direto dentro da `Modelos`. Pastas são copiadas inteiras. Itens com nome começando por ponto (ocultos) são ignorados.
- Projeto retomado nunca recebe modelos.
- O programa nunca altera nem apaga nada na `Modelos`.
- Para abrir a pasta: clique na bolinha e escolha **Abrir pasta Modelos**. Se ela ainda não existir, é criada na hora.
- Se você trocar a pasta mãe, vale a `Modelos` da pasta nova (ela é criada lá). Leve seus modelos junto.

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

## Perguntas

**Ele apaga arquivos?** Nunca. Só move os downloads, copia os modelos e cria ou remove os atalhos de pasta.

**E se eu esquecer o monitor ligado?** Sem downloads por 3 horas ele desliga sozinho e remove os atalhos de pasta. Se o PC reiniciar com um projeto ativo, a bandeja limpa os atalhos de pasta que sobraram (só links, nunca arquivos).

**Qual pasta de downloads ele vigia?** A configurada no sistema, mesmo em outro idioma.

**Por que um projeto não aparece em "Retomar projeto"?** A lista mostra as pastas da pasta mãe cujo nome começa com a data e, logo depois, o nome do cliente (por exemplo `26-11-14 - Premier League - Jogo 1`). Letra maiúscula ou minúscula, acento, tipo de traço e espaço a mais não importam. Se o nome do cliente estiver em outro lugar, ou a pasta estiver fora da pasta mãe, ela não aparece.

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
| Pasta mãe (`~/Trabalho/` por padrão) | `📦 BRUTOS`, `✅ FINAIS`, `🛠️ PROJETOS` | Atalhos de pasta que só existem enquanto um projeto está ativo |
| Pasta mãe (`~/Trabalho/` por padrão) | `Modelos/` | Seus modelos de projeto. É você quem coloca os arquivos |

Fora disso:

- **Seus projetos e a pasta `Modelos`** (dentro de `~/Trabalho/`) são o seu trabalho, não arquivos do programa. Nunca são apagados.
- **Na pasta de onde você instalou** ficam o `instalar.sh`, o `README.md` e as cópias originais dos arquivos. Depois de instalar dá para apagar, mas guarde se quiser reinstalar ou atualizar.
- **Programas do sistema** instalados pelo `instalar.sh` (como `inotify-tools` e `python-pyqt6`) ficam no sistema, não em pastas suas. No GNOME, a extensão AppIndicator também fica no sistema.

## Desinstalar

1. Pare o monitoramento e feche a bolinha. Pelo menu da bolinha: **Parar monitoramento** e depois **Sair da bandeja**. Se a bolinha não aparece (GNOME sem a extensão), rode no terminal:

   ```bash
   ~/.local/bin/organizador.sh parar
   pkill -f organizador_tray.py
   ```

2. Apague os arquivos do programa. Rode no terminal:

   ```bash
   rm ~/.local/bin/organizador*
   rm ~/.config/autostart/organizador-tray.desktop
   rm ~/.local/share/applications/local.organizador.dialogo.desktop
   rm -f ~/.config/organizador.conf
   rm -rf /tmp/organizador-*
   ```

3. Apague os atalhos de teclado que você criou (`Ctrl+1`, `Ctrl+2`, `Ctrl+3` e `Ctrl+'`). O programa não consegue removê-los, e eles ficariam apontando para um arquivo que não existe mais. Apague pelas configurações de teclado, no mesmo lugar onde você os criou. No KDE, não apague os arquivos `.desktop` soltos: apague pelo menu de atalhos, que o KDE limpa o resto.

4. Opcional: os programas que o `instalar.sh` pediu ao sistema (`inotify-tools`, `python-pyqt6` e, no GNOME, `libadwaita`, `python-gobject` e a extensão AppIndicator) ficam instalados. Outros programas costumam usar alguns deles, então só remova se tiver certeza, pelo gerenciador de pacotes da sua distro.

Seus projetos e a pasta `Modelos` continuam na pasta mãe. Se sobrar algum atalho de pasta (`📦 BRUTOS`, `✅ FINAIS` ou `🛠️ PROJETOS`, ou os nomes antigos `📂 ARQUIVOS BRUTOS`, `✅ SALVAR EXPORT` e `🛠️ SALVAR PROJETO`) nela, pode apagar: são só links.
