#!/usr/bin/env python3
"""Ícone de bandeja do Organizador (GNOME, KDE, XFCE...)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher, QLockFile, QTimer, Qt
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QFileDialog, QMenu, QSystemTrayIcon

ESTADO = Path(f"/tmp/organizador-{os.getuid()}")
INFO_FILE = ESTADO / "projeto"
PID_FILE = ESTADO / "monitor.pid"
NOTIFY_FILE = ESTADO / "notificacao"
LOCK_FILE = ESTADO / "bandeja.lock"
PADRAO = Path.home() / "Trabalho"
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "organizador.conf"
ATALHOS = ("🛠️ SALVAR PROJETO", "✅ SALVAR EXPORT")
CLIENTES = (("Premier League", "1"), ("Orlando Magic", "2"), ("Jr. NBA Brasil", "3"))


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
    for arquivo in (PID_FILE, INFO_FILE, NOTIFY_FILE):
        arquivo.unlink(missing_ok=True)
    for nome in ATALHOS:
        atalho = pasta_mae() / nome
        if atalho.is_symlink():
            atalho.unlink()


def icone_status(cor):
    pixmap = QPixmap(128, 128)
    pixmap.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(pixmap)
    pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
    pintor.setPen(QPen(QColor(cor).darker(130), 6))
    pintor.setBrush(QColor(cor))
    pintor.drawEllipse(16, 16, 96, 96)
    pintor.end()
    return QIcon(pixmap)


def localizar_script():
    candidatos = [Path(__file__).resolve().with_name("organizador.sh")]
    if no_path := shutil.which("organizador.sh"):
        candidatos.append(Path(no_path))
    return next((c for c in candidatos if c.is_file()), None)


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

        # Um único menu, remontado a cada mudança. Trocar de menu com o ícone
        # visível não é repassado pelo GNOME, e o menu ficava desatualizado.
        self.menu = QMenu()
        self.setContextMenu(self.menu)
        self.activated.connect(self.ao_clicar)

        # Observa só a pasta de estado: ela quase nunca muda, então não gasta CPU à toa
        self.observador = QFileSystemWatcher([str(ESTADO)], self)
        self.observador.directoryChanged.connect(self.atualizar)

        self.projeto = self._ler_projeto()
        self._aplicar()

    @staticmethod
    def _ler_projeto():
        try:
            return INFO_FILE.read_text(encoding="utf-8").strip()
        except OSError:
            return ""

    def atualizar(self):
        projeto = self._ler_projeto()
        if projeto != self.projeto:
            self.projeto = projeto
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
        for nome, arg in CLIENTES:
            self._acao(nome, lambda a=arg: self.executar(a))
        self.menu.addSeparator()
        if self.projeto:
            self._acao("Parar monitoramento", lambda: self.executar("parar"), "media-playback-stop")
        self._acao("Pasta mãe dos projetos", self.trocar_pasta, "folder")
        self._acao("Sair da bandeja", QApplication.quit, "application-exit")

    def ao_clicar(self, motivo):
        # No GNOME o clique esquerdo só abre o menu (limitação da extensão)
        gatilhos = (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.MiddleClick)
        if self.projeto and motivo in gatilhos:
            self.abrir_pasta()

    def abrir_pasta(self):
        pasta = pasta_mae() / self.projeto
        if not pasta.is_dir():
            notificar("Pasta não encontrada", str(pasta), "dialog-warning")
            return
        ambiente = {
            k: v for k, v in os.environ.items()
            if k not in ("LD_LIBRARY_PATH", "QT_PLUGIN_PATH", "QML2_IMPORT_PATH")
        }
        subprocess.Popen(["xdg-open", str(pasta)], env=ambiente, start_new_session=True)

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
    # No login a bandeja do desktop pode demorar a carregar: espera antes de avisar
    QTimer.singleShot(15000, avisar_se_sem_bandeja)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
