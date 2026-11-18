# Organizador de projetos

Cria a pasta de cada projeto, move seus downloads para o lugar certo, copia os arquivos modelo do cliente e deixa atalhos de pasta para os brutos, os projetos e os finais. Funciona em qualquer distro Linux e ambiente gráfico (GNOME, KDE, XFCE...).

---

## Como funciona na prática

1. Você aperta um atalho de teclado para o cliente (por exemplo, `Ctrl+1`) ou escolhe o cliente pelo ícone na barra do sistema.
2. Uma janela abre na tela (acompanhando o tema claro ou escuro do seu sistema) para você digitar o nome de um projeto novo ou retomar um antigo.
3. Ao confirmar, o programa cria a estrutura do projeto e passa a vigiar sua pasta de downloads. Tudo o que você baixar vai direto para a pasta de brutos desse projeto.

Todo projeto novo ganha três subpastas dentro da pasta mãe (`~/Trabalho/` por padrão):
* `01_Brutos`: onde os downloads caem sozinhos assim que terminam.
* `02_Projetos`: onde ficam os arquivos de edição (já copiados a partir dos seus modelos).
* `03_Exports`: para salvar os arquivos finalizados.

Enquanto o projeto está ativo, três atalhos de pasta aparecem direto na raiz de `~/Trabalho/` para você não precisar ficar navegando entre subpastas nos programas de edição:

| Atalho de pasta | Leva para | Use para |
| :--- | :--- | :--- |
| `📦 BRUTOS` | `01_Brutos` | Importar os arquivos baixados no Photoshop, Premiere, etc. |
| `🛠️ PROJETOS` | `02_Projetos` | Salvar o arquivo do projeto |
| `✅ FINAIS` | `03_Exports` | Salvar o arquivo exportado/finalizado |

Quando você para o monitoramento, esses três atalhos somem automaticamente.

---

## 1. Instalar

Deixe os 5 arquivos juntos na mesma pasta: `instalar.sh`, `organizador.sh`, `organizador_dialog.py`, `organizador_dialog_gtk.py` e `organizador_tray.py`.

1. Abra essa pasta no gerenciador de arquivos, clique com o botão direito em um espaço vazio e escolha **Abrir no terminal**.
2. Rode o instalador:

   ```bash
   bash instalar.sh
   ```

3. Se faltar algum componente no seu sistema, o instalador mostra o comando da sua distro e pergunta se pode instalar. Responda `s` e digite sua senha.

*(Para atualizar o programa no futuro, basta baixar os arquivos novos e rodar `bash instalar.sh` novamente.)*

### Não apareceu a bolinha na barra? (Apenas GNOME)

O KDE e o XFCE já mostram o ícone de bandeja (a bolinha de status) nativamente. O GNOME, porém, precisa de uma extensão para exibir ícones na barra superior (no Ubuntu ela já vem ativada de fábrica).

Se você usa GNOME e a bolinha não apareceu após a instalação:
1. Instale a extensão pelo terminal:
   * **Arch / CachyOS:** `sudo pacman -S gnome-shell-extension-appindicator`
   * **Ubuntu / Debian:** `sudo apt install gnome-shell-extension-appindicator`
   * **Fedora:** `sudo dnf install gnome-shell-extension-appindicator`
2. Encerre a sessão do usuário (logout) e entre novamente.
3. Ative a extensão:

   ```bash
   gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com
   ```

*(A bolinha é opcional: mesmo sem ela, todos os atalhos de teclado funcionam normalmente.)*

### Instalação manual (opcional)

Caso prefira instalar as dependências por conta própria antes de copiar os arquivos:

| Distro | Comando |
| :--- | :--- |
| Arch / CachyOS | `sudo pacman -S inotify-tools python-pyqt6 libnotify xdg-utils xdg-user-dirs python-gobject libadwaita` |
| Ubuntu / Debian | `sudo apt install inotify-tools python3-pyqt6 libnotify-bin xdg-utils xdg-user-dirs python3-gi gir1.2-adw-1` |
| Fedora | `sudo dnf install inotify-tools python3-pyqt6 libnotify xdg-utils xdg-user-dirs python3-gobject libadwaita` |

*(Os dois últimos pacotes de cada linha servem apenas para a janela nativa no GNOME. No KDE e em outros ambientes, podem ser omitidos.)*

Depois, copie os 4 arquivos `organizador*` para `~/.local/bin/` e dê permissão de execução com `chmod +x ~/.local/bin/organizador*`.

---

## 2. Configurar os atalhos de teclado

O programa não consegue criar atalhos de teclado sozinho. Ao terminar a instalação, o terminal já mostra os comandos prontos para copiar (trocando `SEU_USUARIO` pelo seu usuário):

| Ação | Comando | Sugestão de tecla |
| :--- | :--- | :--- |
| Premier League | `/home/SEU_USUARIO/.local/bin/organizador.sh 1` | `Ctrl+1` |
| Orlando Magic | `/home/SEU_USUARIO/.local/bin/organizador.sh 2` | `Ctrl+2` |
| Jr. NBA Brasil | `/home/SEU_USUARIO/.local/bin/organizador.sh 3` | `Ctrl+3` |
| Parar monitoramento | `/home/SEU_USUARIO/.local/bin/organizador.sh parar` | `Ctrl+'` (apóstrofo) |

Use os comandos **sem aspas e sem `sh -c`**, e sempre com o caminho completo (`/home/...`), pois GNOME e KDE não interpretam `~` ou `$HOME` nos atalhos.

* **GNOME:** Configurações → Teclado → Ver e personalizar atalhos → Atalhos personalizados → botão **+**.
* **KDE:** Configurações do Sistema → Atalhos → Adicionar novo → Comando ou script.
* **Outros ambientes:** procure por atalhos personalizados nas configurações de teclado.

**Dica:** Atalhos como `Ctrl+1` também são usados por navegadores para trocar de aba. Como o atalho do sistema tem prioridade em qualquer janela, se isso atrapalhar seu uso, prefira combinações como `Ctrl+Alt+1`, `Ctrl+Alt+2`, `Ctrl+Alt+3` e `Ctrl+Alt+0`.

---

## 3. Usar no dia a dia

1. **Iniciar:** Aperte o atalho do cliente (ou clique na bolinha e escolha o cliente).
2. **Escolher projeto:** Digite um nome para criar um projeto novo e aperte `Enter`, ou selecione um projeto antigo na lista abaixo (usando a seta `↓` ou o mouse).
   * *Nota:* Ao retomar um projeto antigo, nenhuma pasta ou modelo é recriado. Se a `01_Brutos` tiver sido apagada nele, os downloads vão para a pasta raiz do projeto.
3. **Baixar arquivos:** Qualquer download concluído vai direto para `01_Brutos`. Se você baixar um arquivo com o mesmo nome de outro que já existe lá, o programa não sobrescreve o antigo — adiciona a hora no nome (ex.: `foto_143022.jpg`).
4. **Baixou algo errado?** Clique na bolinha e escolha **Desfazer último** para devolver o arquivo recém-movido de volta para a pasta `Downloads`.
5. **Encerrar:** Aperte o atalho de parar ou clique em **Parar monitoramento** no menu da bolinha.

**Cores da bolinha:**
* **Cinza:** ocioso (downloads ficam na pasta `Downloads` normal).
* **Verde:** projeto ativo (downloads vão para o projeto).

*(No GNOME, o clique esquerdo na bolinha abre o menu. No KDE, o clique esquerdo abre direto a pasta do projeto ativo.)*

---

## 4. Personalizar clientes, modelos e pasta mãe

### Adicionar clientes e arquivos modelo

Dentro de `~/Trabalho/` existe a pasta `Modelos` (você pode abri-la direto pelo menu da bolinha em **Abrir pasta Modelos**). Cada subpasta dentro dela representa um cliente:

```text
Modelos/
├── 1 - Premier League/
│   ├── Capa.psd
│   └── Projeto base.fcproj
├── 2 - Orlando Magic/
│   └── Post.psd
└── 3 - Jr. NBA Brasil/
```

* **Novo cliente:** Crie uma pasta em `Modelos` seguindo a numeração (ex.: `4 - Brighton`). Ela aparece na hora no menu da bolinha. Para ter atalho de teclado, cadastre o comando correspondente (`.../organizador.sh 4`). Pastas sem número também funcionam, mas aparecem apenas no menu da bolinha.
* **Evite repetir números ou renomear clientes antigos:** Apenas a primeira pasta com um número responde ao atalho. Além disso, se você renomear a pasta de um cliente depois, os projetos antigos dele deixam de aparecer na lista "Retomar projeto" (embora continuem salvos no disco).
* **Como os modelos são copiados:** Ao criar um projeto **novo**, tudo o que está dentro da pasta do cliente vai para `02_Projetos`.
  * Arquivos únicos de cada extensão ganham o nome do projeto (`Capa.psd` vira `26-11-18 - Premier League - Jogo 1.psd`).
  * Se houver mais de um arquivo da mesma extensão (dois `.psd`, por exemplo), o nome original é mantido no final (`26-11-18 - Premier League - Jogo 1 - Capa.psd`).
  * Subpastas são copiadas inteiras com o nome original. Arquivos ocultos (começando com `.`) na pasta do cliente são ignorados.

### Trocar a pasta mãe (`~/Trabalho`)

Se quiser salvar seus projetos em outro local (como um HD externo):

1. Pare qualquer monitoramento ativo.
2. Clique na bolinha e escolha **Pasta mãe dos projetos**.
3. Selecione a nova pasta e confirme.

A pasta nova terá sua própria pasta `Modelos` e sua própria lista de projetos recentes. Se a pasta escolhida ficar indisponível (ex.: HD desconectado), o programa avisa e usa `~/Trabalho` até ela voltar.

---

## Perguntas frequentes

**Ele apaga algum arquivo meu?**
Nunca. O programa apenas move downloads concluídos, copia modelos e cria ou remove os três atalhos de pasta.

**E se eu esquecer o monitoramento ligado?**
Se ficar 3 horas sem nenhum download, ele desliga sozinho e remove os atalhos de pasta. Se você reiniciar o PC com um projeto ativo, a bandeja limpa os atalhos que sobraram na próxima vez que iniciar (apenas os links, nunca suas pastas).

**Qual pasta de downloads ele vigia?**
A pasta de downloads padrão configurada no seu sistema, independente do idioma (`Downloads`, `Transferências`, etc.).

**Quais arquivos ele ignora?**
Downloads ainda em andamento (`.crdownload`, `.part`, `.tmp`, `.opdownload`, `.download`, `.aria2`) e arquivos ocultos. Ele espera o navegador concluir o download antes de mover.

---

## Onde ficam os arquivos do programa

| Onde | Arquivo | Para que serve |
| :--- | :--- | :--- |
| `~/.local/bin/` | `organizador.sh` | Motor principal que cria projetos e move downloads |
| `~/.local/bin/` | `organizador_dialog.py` | Janela de escolha de projeto (KDE e outros) |
| `~/.local/bin/` | `organizador_dialog_gtk.py` | Janela de escolha de projeto (GNOME) |
| `~/.local/bin/` | `organizador_tray.py` | Ícone e menu da bandeja |
| `~/.config/autostart/` | `organizador-tray.desktop` | Inicia a bandeja automaticamente ao ligar o PC |
| `~/.local/share/applications/` | `local.organizador.dialogo.desktop` | Define nome e ícone da janela no GNOME |
| `/tmp/organizador-<ID>/` | `monitor.pid`, `projeto`, `notificacao`, `ultimo_movido`, `bandeja.lock` | Arquivos temporários de controle (somem ao reiniciar) |
| `~/.config/` | `organizador.conf` | Guarda o caminho da pasta mãe, caso você tenha trocado |
| Pasta mãe (`~/Trabalho/`) | `📦 BRUTOS`, `✅ FINAIS`, `🛠️ PROJETOS` | Atalhos temporários enquanto há um projeto ativo |
| Pasta mãe (`~/Trabalho/`) | `Modelos/` | Subpastas dos clientes com seus arquivos modelo |

---

## Desinstalar

1. Abra o terminal na pasta onde estão os arquivos de instalação (botão direito em um espaço vazio → **Abrir no terminal**).
2. Rode:

   ```bash
   bash instalar.sh desinstalar
   ```

3. Responda `s` para confirmar.

O desinstalador para o monitoramento, fecha a bolinha e remove todos os arquivos do programa, o início automático e as configurações. Seus projetos e a pasta `Modelos` não são tocados.

**Limpeza manual opcional:**
* Apague os atalhos de teclado que você criou (`Ctrl+1`, `Ctrl+2`, etc.) nas configurações de teclado do sistema.
* Caso tenha removido os arquivos sem usar o script, basta parar o monitoramento, sair da bandeja e apagar `~/.local/bin/organizador*`, `~/.config/autostart/organizador-tray.desktop`, `~/.local/share/applications/local.organizador.dialogo.desktop` e `~/.config/organizador.conf`.