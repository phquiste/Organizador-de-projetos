#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher, QLockFile, Qt
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

TMP_DIR = "/tmp"
INFO_FILE = "/tmp/projeto_ativo.txt"
PID_FILE = "/tmp/monitor_downloads.pid"
NOTIFY_ID_FILE = "/tmp/notify_id.txt"
LOCK_FILE = "/tmp/organizador_tray.lock"
TRABALHO_DIR = Path.home() / "Trabalho"
SCRIPT_PATH = Path.home() / ".local/bin/organizador.sh"

CLIENTES = (
    ("Premier League", "1"),
    ("Orlando Magic", "2"),
    ("Jr. NBA Brasil", "3"),
)


def obter_desktop_dir() -> Path:
    try:
        res = subprocess.run(
            ["xdg-user-dir", "DESKTOP"],
            capture_output=True,
            text=True,
            check=False,
        )
        caminho = Path(res.stdout.strip())
        if res.stdout.strip() and caminho.is_dir():
            return caminho
    except OSError:
        pass

    for candidato in (Path.home() / "Área de trabalho", Path.home() / "Desktop"):
        if candidato.is_dir():
            return candidato
    return Path.home() / "Desktop"


def limpar_estado_orfao():
    pid_path = Path(PID_FILE)
    monitor_vivo = False

    if pid_path.is_file():
        try:
            pid = pid_path.read_text(encoding="utf-8").strip()
            cmdline = Path(f"/proc/{pid}/cmdline")
            if pid.isdigit() and cmdline.is_file():
                conteudo = cmdline.read_bytes()
                if b"organizador.sh" in conteudo:
                    monitor_vivo = True
        except OSError:
            pass

    if not monitor_vivo:
        for arq in (PID_FILE, INFO_FILE, NOTIFY_ID_FILE):
            Path(arq).unlink(missing_ok=True)

        desktop = obter_desktop_dir()
        for atalho in ("🛠️ SALVAR PROJETO", "✅ SALVAR EXPORT"):
            caminho_atalho = desktop / atalho
            if caminho_atalho.is_symlink() or caminho_atalho.exists():
                caminho_atalho.unlink(missing_ok=True)


def criar_icone_status(cor_hex: str) -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 4))
    painter.setBrush(QColor(cor_hex))
    painter.drawEllipse(8, 8, 48, 48)
    painter.end()

    return QIcon(pixmap)


class TrayMonitor(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.projeto_atual: str | None = None
        self.icon_ocioso = criar_icone_status("#6c757d")
        self.icon_ativo = criar_icone_status("#28a745")

        action_sair = QAction("Sair da Bandeja", self)
        action_sair.triggered.connect(QApplication.quit)

        # Menu Ativo
        self.menu_ativo = QMenu()
        self.action_status = QAction("", self)
        self.action_status.setEnabled(False)
        self.menu_ativo.addAction(self.action_status)

        action_abrir = QAction("📂 Abrir Pasta do Projeto", self)
        action_abrir.triggered.connect(self.abrir_pasta_projeto)
        self.menu_ativo.addAction(action_abrir)

        self.menu_ativo.addSeparator()
        self._popular_clientes(self.menu_ativo.addMenu("Trocar Projeto"))
        self.menu_ativo.addSeparator()

        action_parar = QAction("⏹️ Parar Monitoramento", self)
        action_parar.triggered.connect(self.parar_projeto)
        self.menu_ativo.addAction(action_parar)
        self.menu_ativo.addAction(action_sair)

        # Menu Ocioso
        self.menu_ocioso = QMenu()
        self._popular_clientes(self.menu_ocioso)
        self.menu_ocioso.addSeparator()
        self.menu_ocioso.addAction(action_sair)

        self.activated.connect(self.ao_clicar_icone)

        self.watcher = QFileSystemWatcher(self)
        self.watcher.directoryChanged.connect(self.ao_mudar_tmp)
        self.watcher.fileChanged.connect(self.atualizar_estado)
        self._configurar_watcher()

        self.atualizar_estado()

    def _popular_clientes(self, menu: QMenu):
        for nome, arg in CLIENTES:
            act = QAction(nome, self)
            act.triggered.connect(lambda _, a=arg: self.executar_script(a))
            menu.addAction(act)

    def _configurar_watcher(self):
        if os.path.exists(INFO_FILE):
            if TMP_DIR in self.watcher.directories():
                self.watcher.removePath(TMP_DIR)
            if INFO_FILE not in self.watcher.files():
                self.watcher.addPath(INFO_FILE)
        else:
            if TMP_DIR not in self.watcher.directories():
                self.watcher.addPath(TMP_DIR)

    def ao_mudar_tmp(self):
        if os.path.exists(INFO_FILE):
            self.atualizar_estado()

    def atualizar_estado(self):
        self._configurar_watcher()

        nome_projeto = ""
        if os.path.exists(INFO_FILE):
            try:
                nome_projeto = Path(INFO_FILE).read_text(encoding="utf-8").strip()
            except OSError:
                nome_projeto = ""

        if nome_projeto:
            if nome_projeto != self.projeto_atual:
                self.projeto_atual = nome_projeto
                self.setIcon(self.icon_ativo)
                self.setToolTip(f"Ativo: {nome_projeto} (Clique para abrir)")
                self.action_status.setText(f"🟢 {nome_projeto}")
                self.setContextMenu(self.menu_ativo)
            return

        if self.projeto_atual is not None or self.contextMenu() is not self.menu_ocioso:
            self.projeto_atual = None
            self.setIcon(self.icon_ocioso)
            self.setToolTip("Organizador: Ocioso (Clique direito para iniciar)")
            self.setContextMenu(self.menu_ocioso)

    def ao_clicar_icone(self, reason: QSystemTrayIcon.ActivationReason):
        if self.projeto_atual and reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.MiddleClick,
        ):
            self.abrir_pasta_projeto()

    def abrir_pasta_projeto(self):
        if not self.projeto_atual:
            return

        caminho = TRABALHO_DIR / self.projeto_atual
        if not caminho.is_dir():
            subprocess.Popen(
                ["notify-send", "-a", "Organizador", "Pasta não encontrada", str(caminho)],
                start_new_session=True,
            )
            return

        env = os.environ.copy()
        for var in ("LD_LIBRARY_PATH", "QT_PLUGIN_PATH", "QML2_IMPORT_PATH"):
            env.pop(var, None)

        gerenciador = "dolphin" if shutil.which("dolphin") else "xdg-open"
        subprocess.Popen([gerenciador, str(caminho)], env=env, start_new_session=True)

    def executar_script(self, arg: str):
        if SCRIPT_PATH.is_file():
            subprocess.Popen([str(SCRIPT_PATH), arg], start_new_session=True)

    def parar_projeto(self):
        self.executar_script("parar")


def main():
    lock = QLockFile(LOCK_FILE)
    lock.setStaleLockTime(0)
    if not lock.tryLock(100):
        sys.exit(0)

    limpar_estado_orfao()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray = TrayMonitor()
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
