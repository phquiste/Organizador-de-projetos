#!/usr/bin/env python3
"""Ícone de bandeja do Organizador (GNOME, KDE, XFCE...)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher, QLockFile, QTimer, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QFileDialog, QMenu, QSystemTrayIcon

ESTADO = Path(f"/tmp/organizador-{os.getuid()}")
INFO_FILE = ESTADO / "projeto"
PID_FILE = ESTADO / "monitor.pid"
NOTIFY_FILE = ESTADO / "notificacao"
UNDO_FILE = ESTADO / "ultimo_movido"
LOCK_FILE = ESTADO / "bandeja.lock"
PADRAO = Path.home() / "Trabalho"
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "organizador.conf"
ATALHOS = ("📦 BRUTOS", "✅ FINAIS", "🛠️ PROJETOS")
ATALHOS_ANTIGOS = ("📂 ARQUIVOS BRUTOS", "✅ SALVAR EXPORT", "🛠️ SALVAR PROJETO")


def notificar(titulo, texto="", icone="dialog-information"):
    try:
        subprocess.Popen(
            ["notify-send", "-a", "Organizador", "-i", icone, titulo, texto],
            start_new_session=True,
        )
    except OSError:
        pass


def pasta_mae():
    """Pasta mãe dos projetos: a escolhida no menu, ou ~/Trabalho se não houver (ou sumiu)."""
    try:
        texto = CONFIG.read_text(encoding="utf-8").strip()
    except OSError:
        return PADRAO
    return Path(texto) if texto and Path(texto).is_dir() else PADRAO


def monitor_vivo():
    try:
        pid = PID_FILE.read_text().strip()
        return pid.isdigit() and b"organizador.sh" in Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return False


def limpar_estado_orfao():
    if monitor_vivo():
        return
    for arquivo in (PID_FILE, INFO_FILE, NOTIFY_FILE, UNDO_FILE):
        arquivo.unlink(missing_ok=True)
    for nome in ATALHOS + ATALHOS_ANTIGOS:
        atalho = pasta_mae() / nome
        if atalho.is_symlink():
            atalho.unlink()


def abrir_no_gerenciador(pasta):
    ambiente = {
        k: v for k, v in os.environ.items()
        if k not in ("LD_LIBRARY_PATH", "QT_PLUGIN_PATH", "QML2_IMPORT_PATH")
    }
    subprocess.Popen(["xdg-open", str(pasta)], env=ambiente, start_new_session=True)


def icone_status(cor):
    pixmap = QPixmap(128, 128)
    pixmap.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(pixmap)
    pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
    pintor.setPen(QPen(QColor(cor).darker(130), 4))
    pintor.setBrush(QColor(cor))
    pintor.drawEllipse(2, 2, 124, 124)
    pintor.end()
    return QIcon(pixmap)


def localizar_script():
    candidatos = [Path(__file__).resolve().with_name("organizador.sh")]
    if no_path := shutil.which("organizador.sh"):
        candidatos.append(Path(no_path))
    return next((c for c in candidatos if c.is_file()), None)


def ler_clientes():
    """Clientes [(argumento, nome)], na ordem do menu. Quem lê as pastas de Modelos é o organizador.sh."""
    script = localizar_script()
    if script is None:
        return []
    try:
        saida = subprocess.run([str(script), "listar"], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    clientes = []
    for linha in saida.splitlines():
        arg, _, nome = linha.partition("\t")
        if arg and nome:
            clientes.append((arg, nome))
    return clientes


def avisar_se_sem_bandeja():
    if not QSystemTrayIcon.isSystemTrayAvailable():
        notificar(
            "Bandeja indisponível",
            "No GNOME, ative a extensão AppIndicator. Os atalhos de teclado continuam funcionando.",
            "dialog-warning",
        )


class Bandeja(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.icone_ocioso = icone_status("#8b949e")
        self.icone_ativo = icone_status("#2ea44f")

        self.menu = QMenu()
        self.setContextMenu(self.menu)
        self.activated.connect(self.ao_clicar)

        self.observador = QFileSystemWatcher([str(ESTADO)], self)
        self.observador.directoryChanged.connect(self.ao_mudar_pasta)
        self.timer_clientes = QTimer(self)
        self.timer_clientes.setSingleShot(True)
        self.timer_clientes.setInterval(500)
        self.timer_clientes.timeout.connect(self.atualizar_clientes)

        self.projeto = self._ler_projeto()
        self.tem_desfazer = self._ler_desfazer()
        self.clientes = ler_clientes()
        self._vigiar_pastas()
        self._aplicar()

    def _vigiar_pastas(self):
        desejadas = {str(ESTADO)} | {str(p) for p in (pasta_mae(), pasta_mae() / "Modelos") if p.is_dir()}
        atuais = set(self.observador.directories())
        if atuais - desejadas:
            self.observador.removePaths(list(atuais - desejadas))
        if desejadas - atuais:
            self.observador.addPaths(list(desejadas - atuais))

    def ao_mudar_pasta(self, caminho):
        if caminho == str(ESTADO):
            self.atualizar()
        else:
            self.timer_clientes.start()

    def atualizar_clientes(self):
        self._vigiar_pastas()
        clientes = ler_clientes()
        if clientes != self.clientes:
            self.clientes = clientes
            self._aplicar()

    @staticmethod
    def _ler_projeto():
        try:
            return INFO_FILE.read_text(encoding="utf-8").strip()
        except OSError:
            return ""

    @staticmethod
    def _ler_desfazer():
        if not monitor_vivo():
            return False
        try:
            destino, _, _ = UNDO_FILE.read_text(encoding="utf-8").strip().partition("\t")
            return bool(destino) and Path(destino).exists()
        except OSError:
            return False

    def atualizar(self):
        projeto = self._ler_projeto()
        tem_desfazer = self._ler_desfazer()
        if projeto != self.projeto or tem_desfazer != self.tem_desfazer:
            self.projeto = projeto
            self.tem_desfazer = tem_desfazer
            self._aplicar()

    def _acao(self, texto, funcao, icone=None, ativa=True):
        acao = self.menu.addAction(texto)
        if icone:
            acao.setIcon(QIcon.fromTheme(icone))
        acao.setEnabled(ativa)
        acao.triggered.connect(lambda _=False: funcao())
        return acao

    def _aplicar(self):
        self.menu.clear()
        if self.projeto:
            self.setIcon(self.icone_ativo)
            self.setToolTip(self.projeto)
            self._acao(f"●  {self.projeto}", lambda: None, ativa=False)
            self._acao("Abrir pasta do projeto", self.abrir_pasta, "folder-open")
            self.menu.addSeparator()
            self._acao("Trocar para:", lambda: None, ativa=False)
        else:
            self.setIcon(self.icone_ocioso)
            self.setToolTip("Organizador: ocioso")

        for arg, nome in self.clientes:
            self._acao(nome, lambda a=arg: self.executar(a))

        self.menu.addSeparator()

        if self.projeto:
            self._acao("Parar monitoramento", lambda: self.executar("parar"), "media-playback-stop")
            if self.tem_desfazer:
                self._acao("Desfazer último", lambda: self.executar("desfazer"), "edit-undo")
            self.menu.addSeparator()

        self._acao("Abrir pasta Modelos", self.abrir_modelos, "folder-open")
        self._acao("Pasta mãe dos projetos", self.trocar_pasta, "folder")
        self._acao("Sair da bandeja", QApplication.quit, "application-exit")

    def ao_clicar(self, motivo):
        gatilhos = (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.MiddleClick)
        if self.projeto and motivo in gatilhos:
            self.abrir_pasta()

    def abrir_pasta(self):
        pasta = pasta_mae() / self.projeto
        if not pasta.is_dir():
            notificar("Pasta não encontrada", str(pasta), "dialog-warning")
            return
        abrir_no_gerenciador(pasta)

    def abrir_modelos(self):
        script = localizar_script()
        if script is None:
            notificar("organizador.sh não encontrado", "Rode o instalar.sh de novo.", "dialog-error")
            return
        try:
            saida = subprocess.run([str(script), "modelos"], capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            saida = ""
        pasta = Path(saida) if saida else None
        if pasta is None or not pasta.is_dir():
            notificar("Não consegui criar a pasta Modelos", str(pasta_mae() / "Modelos"), "dialog-error")
            return
        abrir_no_gerenciador(pasta)

    def trocar_pasta(self):
        if self.projeto:
            notificar(
                "Pare o monitoramento antes",
                'Há um projeto ativo. Use "Parar monitoramento" e troque a pasta depois.',
                "dialog-warning",
            )
            return
        atual = pasta_mae()
        escolhida = QFileDialog.getExistingDirectory(None, "Pasta mãe dos projetos", str(atual))
        if not escolhida or Path(escolhida) == atual:
            return
        try:
            CONFIG.parent.mkdir(parents=True, exist_ok=True)
            CONFIG.write_text(escolhida + "\n", encoding="utf-8")
        except OSError:
            notificar("Não consegui salvar a pasta", str(CONFIG), "dialog-error")
            return
        notificar("Pasta mãe alterada", escolhida, "folder")
        self.atualizar_clientes()

    def executar(self, arg):
        script = localizar_script()
        if script is None:
            notificar("organizador.sh não encontrado", "Rode o instalar.sh de novo.", "dialog-error")
            return
        subprocess.Popen([str(script), arg], start_new_session=True)


def main():
    ESTADO.mkdir(mode=0o700, exist_ok=True)
    trava = QLockFile(str(LOCK_FILE))
    trava.setStaleLockTime(0)
    if not trava.tryLock(100):
        return

    limpar_estado_orfao()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    bandeja = Bandeja()
    bandeja.show()
    QTimer.singleShot(15000, avisar_se_sem_bandeja)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
