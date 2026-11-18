# Organizador de projetos

Cria a pasta de cada projeto, move os downloads para o lugar certo, copia os modelos do cliente e deixa atalhos de pasta para os brutos, os projetos e os finais. Funciona em qualquer distro e ambiente gráfico (GNOME, KDE, XFCE...).

## O que ele faz

Ao apertar o atalho de teclado de um cliente, abre uma janela para criar um projeto novo ou retomar um antigo. No GNOME a janela é nativa (libadwaita, com tema claro/escuro e cor de destaque do sistema). Nos outros ambientes usa o visual nativo do Qt.

Os clientes são as subpastas da pasta `Modelos` (veja **Clientes e modelos de projeto**). Por padrão: Premier League, Orlando Magic e Jr. NBA Brasil.

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

O mesmo comando serve para atualizar: rode de novo com os arquivos novos. Para desinstalar, veja **Desinstalar**.

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

O número do atalho é o número que vem no começo da pasta do cliente em `Modelos` (`1 - Premier League` é o 1). Para um cliente novo, cadastre mais um atalho com o número dele, por exemplo `/home/SEU_USUARIO/.local/bin/organizador.sh 4` na tecla `Ctrl+4`. O programa não consegue criar atalhos de teclado sozinho. Clientes sem número na pasta aparecem só no menu da bolinha.

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

## Clientes e modelos de projeto

Dentro da pasta mãe existe uma pasta chamada `Modelos` (`~/Trabalho/Modelos` por padrão). Ela tem **uma subpasta por cliente**, e essa lista de subpastas é a lista de clientes do programa. Os modelos de projeto de cada cliente ficam dentro da pasta dele:

```
Modelos/
├── 1 - Premier League/
│   ├── Capa.psd
│   └── Projeto base.fcproj
├── 2 - Orlando Magic/
│   └── Post.psd
└── 3 - Jr. NBA Brasil/
```

**Clientes:**
- O número no começo do nome da pasta (o `1` de `1 - Premier League`) é o número do atalho de teclado e define a ordem no menu da bolinha. O número não aparece no menu nem nos nomes dos projetos, que ficam `26-11-18 - Premier League - Jogo 1`.
- Cliente novo: crie uma pasta nova em `Modelos` com o próximo número (por exemplo `4 - Brighton`). Ele aparece na bolinha em instantes. Para ter atalho de teclado, cadastre também o atalho dele (veja **Atalhos de teclado**).
- Uma pasta sem número também vale como cliente, mas aparece só no menu da bolinha, depois das numeradas.
- Não repita número: só a primeira pasta com aquele número recebe o atalho. Não mude o número de um cliente que já tem atalho de teclado, senão a tecla passa a abrir outro cliente.
- Se a `Modelos` ainda não tiver nenhuma pasta de cliente, as 3 padrão (Premier League, Orlando Magic e Jr. NBA Brasil) são criadas.

**Modelos:**
- Ao criar um projeto **novo**, tudo que está na pasta do cliente é copiado para a `02_Projetos` do projeto. O que estiver solto direto na `Modelos`, fora de uma pasta de cliente, é ignorado.
- Cada arquivo copiado recebe o nome do projeto, mantendo a extensão: `Capa.psd` vira `26-11-18 - Premier League - Jogo 1.psd`. Se houver mais de um arquivo do mesmo tipo (dois `.psd`, por exemplo), cada um recebe o nome do projeto seguido do nome original: `26-11-18 - Premier League - Jogo 1 - Capa.psd`.
- Pastas são copiadas inteiras e mantêm o nome original. Itens com nome começando por ponto (ocultos) são ignorados.
- O conteúdo dos arquivos não é alterado. Se o programa guarda o nome do projeto dentro do arquivo (o FilmCraft, por exemplo), esse nome continua o do modelo.
- Projeto retomado nunca recebe modelos, e o programa nunca altera nem apaga nada na `Modelos`.

**Cuidados:**
- Se você renomear a pasta de um cliente depois, os projetos antigos dele deixam de aparecer em "Retomar projeto", porque essa lista procura pelo nome do cliente. As pastas dos projetos antigos não mudam.
- Apagar a pasta de um cliente apaga os modelos que estão nela. Os projetos já criados ficam intactos.

Para abrir a `Modelos`: clique na bolinha e escolha **Abrir pasta Modelos**. Se ela ainda não existir, é criada na hora, já com as pastas dos clientes padrão.

## Trocar a pasta mãe

Por padrão os projetos ficam em `~/Trabalho`. Para usar outra pasta (um HD externo, por exemplo):

1. Clique na bolinha e escolha **Pasta mãe dos projetos**.
2. Escolha a pasta e confirme.

A escolha vale para todos os projetos seguintes e só muda quando você trocar de novo. Para voltar ao padrão, escolha `~/Trabalho` outra vez.

- Só dá para trocar com o monitoramento parado. Com um projeto ativo, o programa avisa e pede para parar antes.
- Os clientes e os modelos ficam na pasta `Modelos` da pasta mãe. Ao trocar de pasta mãe, vale a lista de clientes da pasta nova (se ela ainda não tiver nenhum cliente, as pastas padrão são criadas ali quando você abrir a `Modelos` ou criar um projeto).
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

**Como adiciono um cliente?** Crie uma pasta nova dentro de `Modelos`, com o próximo número (por exemplo `4 - Brighton`). Veja **Clientes e modelos de projeto**.

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
| Pasta mãe (`~/Trabalho/` por padrão) | `Modelos/` | Uma pasta por cliente, com os modelos de projeto dele. É você quem coloca os arquivos |

Fora disso:

- **Seus projetos e a pasta `Modelos`** (dentro de `~/Trabalho/`) são o seu trabalho, não arquivos do programa. Nunca são apagados.
- **Na pasta de onde você instalou** ficam o `instalar.sh`, o `README.md` e as cópias originais dos arquivos. Depois de instalar dá para apagar, mas guarde se quiser reinstalar ou atualizar.
- **Programas do sistema** instalados pelo `instalar.sh` (como `inotify-tools` e `python-pyqt6`) ficam no sistema, não em pastas suas. No GNOME, a extensão AppIndicator também fica no sistema.

## Desinstalar

1. Abra o terminal na pasta onde estão os arquivos de instalação (botão direito num espaço vazio → **Abrir no terminal**).
2. Rode:

   ```bash
   bash instalar.sh desinstalar
   ```

3. Responda `s` quando ele perguntar.

Ele para o monitoramento, fecha a bolinha e apaga os arquivos do programa, o início automático, a configuração da pasta mãe e os arquivos temporários. Seus projetos e a pasta `Modelos` continuam na pasta mãe.

O que ele **não** consegue apagar, e você faz na mão:
- **Os atalhos de teclado que você criou** (`Ctrl+1`, `Ctrl+2`, `Ctrl+3`, `Ctrl+'` e os de clientes novos). Apague pelas configurações de teclado, no mesmo lugar onde você os criou. No KDE, apague pelo menu de atalhos, não pelos arquivos `.desktop` soltos, que o KDE limpa o resto.
- **Os programas que o `instalar.sh` pediu ao sistema** (`inotify-tools`, `python-pyqt6` e, no GNOME, `libadwaita`, `python-gobject` e a extensão AppIndicator). Outros programas costumam usar alguns deles, então só remova se tiver certeza, pelo gerenciador de pacotes da sua distro.
- **Algum atalho de pasta que tenha sobrado** (`📦 BRUTOS`, `✅ FINAIS` ou `🛠️ PROJETOS`, ou os nomes antigos `📂 ARQUIVOS BRUTOS`, `✅ SALVAR EXPORT` e `🛠️ SALVAR PROJETO`) na pasta mãe. Pode apagar: são só links.

Se você não tem mais a pasta de instalação, apague na mão. Pare o monitoramento e feche a bolinha (menu da bolinha → **Parar monitoramento**, depois **Sair da bandeja**), e rode no terminal:

```bash
rm ~/.local/bin/organizador*
rm ~/.config/autostart/organizador-tray.desktop
rm ~/.local/share/applications/local.organizador.dialogo.desktop
rm -f ~/.config/organizador.conf
rm -rf /tmp/organizador-$UID
```
