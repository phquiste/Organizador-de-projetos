# 📁 Guia Passo a Passo: Seu Organizador Automático

Bem-vindo! Este guia foi feito para ajudar você (ou para você lembrar no futuro) a configurar e usar o seu sistema de organização automática de arquivos e pastas no CachyOS / KDE Plasma.

## 🧐 O que esse sistema faz por você?

Quando você trabalha com edição de vídeos e imagens para clientes (*Premier League*, *Orlando Magic*, *Jr. NBA Brasil*), a pior parte é ter que criar pastas, espalhar arquivos e organizar os downloads manualmente.

Com este sistema, ao apertar um atalho no teclado ou clicar na bandeja do sistema:

1. Uma caixinha aparece na tela para você **criar um novo projeto** ou **continuar um projeto antigo**.

2. Ele cria automaticamente a pasta do projeto de acordo com a necessidade do cliente:

   * **Premier League e Jr. NBA Brasil (estrutura completa):**

     * **`01_Brutos/`**: Todos os vídeos e arquivos baixados da internet vão direto para cá **sozinhos** (assim que o download termina, sem atrasos).

     * **`02_Projetos/`**: Onde você salva seus arquivos do Premiere ou Photoshop.

     * **`03_Exports/`**: Onde ficam os vídeos e artes finalizadas.

   * **Orlando Magic (pasta única / geral):**

     * Sem subpastas! Tudo vai direto para a **pasta raiz do projeto** (downloads, arquivos de edição e exports no mesmo lugar).

3. Ele cria os atalhos práticos na sua **Área de trabalho** para você salvar seus arquivos direto no lugar certo com 1 clique dentro dos programas de edição:

   * **Premier League / Jr. NBA Brasil:** Cria `🛠️ SALVAR PROJETO` e `✅ SALVAR EXPORT`.

   * **Orlando Magic:** Cria apenas `✅ SALVAR EXPORT` apontando direto para a pasta geral do projeto.

## 📍 Onde as coisas ficam no computador?

* **O script principal (o "cérebro"):** `~/.local/bin/organizador.sh`

* **O monitor da barra de tarefas:** `~/.local/bin/organizador_tray.py`

* **Onde os projetos são salvos:** Na sua pasta `~/Trabalho/`

## ⚙️ Passo 1: Instalando pela primeira vez (ou se formatar o PC)

Abra o seu terminal (Fish) e siga estes passos simples:

### 1. Instalar os programas necessários

Copie e cole este comando no terminal para garantir que o seu computador tem as ferramentas que o script usa:

```fish
sudo pacman -S inotify-tools python-pyqt6 libnotify
```

### 2. Criar a pasta de programas do usuário

```fish
mkdir -p ~/.local/bin
```

### 3. Copiar e ativar seus arquivos

Coloque o seu arquivo `organizador.sh` e o `organizador_tray.py` dentro da pasta de Downloads e rode no terminal:

```fish
mv ~/Downloads/organizador.sh ~/.local/bin/organizador.sh
mv ~/Downloads/organizador_tray.py ~/.local/bin/organizador_tray.py
chmod +x ~/.local/bin/organizador.sh ~/.local/bin/organizador_tray.py
```

### 4. Iniciar a bandeja automaticamente ao ligar o PC (Opcional)

Para que a bolinha de status apareça perto do relógio sempre que você entrar no KDE Plasma:

```fish
mkdir -p ~/.config/autostart
printf '[Desktop Entry]\nType=Application\nName=Organizador Tray\nExec=/home/phquiste/.local/bin/organizador_tray.py\nX-KDE-autostart-phase=2\n' > ~/.config/autostart/organizador-tray.desktop
```

## ⌨️ Passo 2: Configurando os Atalhos no Teclado (KDE Plasma)

Para abrir o menu dos clientes apertando apenas algumas teclas:

1. Abra o menu iniciar do KDE e procure por **Configurações do Sistema**.

2. Vá em **Teclado** e depois em **Atalhos** (ou digite "Atalhos" na busca).

3. Clique no botão inferior para **Adicionar Novo** ➔ **Comando ou Script...**.

4. Dê um nome (ex: *Organizador - Premier League*) e cole o **Comando Exato** abaixo, definindo um atalho no teclado (como `Meta + 1`):

| Cliente / Ação | Cole este Comando Exato no KDE | Atalho Sugerido | 
| :--- | :--- | :--- | 
| **Premier League** | `/home/phquiste/.local/bin/organizador.sh 1` | `Meta + 1` | 
| **Orlando Magic** | `/home/phquiste/.local/bin/organizador.sh 2` | `Meta + 2` | 
| **Jr. NBA Brasil** | `/home/phquiste/.local/bin/organizador.sh 3` | `Meta + 3` | 
| **Parar Monitor** | `/home/phquiste/.local/bin/organizador.sh parar` | `Meta + 0` | 

## 🟢 Como usar no dia a dia

1. Aperte o atalho do cliente (ex: **Meta + 1** ou **Meta + 2**) **ou** clique com o **botão direito na bolinha cinza** da bandeja do sistema e escolha o cliente.

2. Uma janelinha vai abrir:

   * **Para criar um projeto novo:** Digite o nome dele na caixinha e aperte `Enter`.

   * **Para abrir um projeto antigo:** Use as setas do teclado para baixo (`↓`) para escolher na lista e aperte `Enter`.

3. Pronto! O(s) atalho(s) correspondentes vão aparecer na sua Área de trabalho (`🛠️ SALVAR PROJETO` e `✅ SALVAR EXPORT`, ou apenas `✅ SALVAR EXPORT` no caso do Orlando Magic). Tudo o que você baixar vai direto para o projeto ativo.

## 🛡️ Dúvidas Frequentes (FAQ)

* **O script apaga meus arquivos brutos antigos sozinho?**
  **Não!** Por segurança, o script nunca apaga nada das suas pastas. Você tem controle total e apaga os arquivos manualmente quando quiser liberar espaço.

* **E se eu esquecer o monitor ligado ou reiniciar o PC com um projeto aberto?**
  Fique tranquilo:
  * Se você passar **3 horas** sem baixar absolutamente nada, o monitor se desliga sozinho por segurança e limpa os atalhos da Área de trabalho.
  * Se você reiniciar ou desligar o computador com um projeto ativo, assim que a bandeja iniciar novamente ela detecta que o monitor não está mais rodando e **limpa automaticamente os atalhos órfãos** da Área de trabalho.

* **Como funciona a bolinha na bandeja do sistema?**
  Perto do relógio do KDE, o ícone mostra o estado atual em tempo real:
  * **Quando está ocioso (bolinha cinza):**
    * **Clique direito:** abre o hub enxuto para iniciar um projeto (*Premier League*, *Orlando Magic*, *Jr. NBA Brasil*) ou sair da bandeja.
  * **Quando há um projeto rodando (bolinha verde):**
    * **Clique esquerdo** (ou clique do meio): abre a pasta do projeto ativo direto no Dolphin.
    * **Clique direito:** abre o menu completo com o nome do projeto ativo, **📂 Abrir Pasta do Projeto**, **Trocar Projeto** e **⏹️ Parar Monitoramento**.