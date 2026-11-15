#!/usr/bin/env python3
"""Janela de escolha de projeto (Qt, usada fora do GNOME).

Imprime "NOVO|nome" ou "EXISTENTE|pasta". Usa o visual nativo do sistema.
"""
import os
import subprocess
import sys
from pathlib import Path

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QApplication, QDialog, QDialogButtonBox, QLabel,
        QLineEdit, QListWidget, QVBoxLayout,
    )
except ImportError:
    sys.exit(2)


def seguir_tema_gnome():
    """Fora do GNOME não faz nada. No GNOME, pede ao Qt o mesmo tema claro/escuro do sistema."""
    if "GNOME" not in os.environ.get("XDG_CURRENT_DESKTOP", ""):
        return
    os.environ.setdefault("QT_WAYLAND_DECORATION", "adwaita")  # usa se qadwaitadecorations estiver instalado


def aplicar_esquema(app):
    if "GNOME" not in os.environ.get("XDG_CURRENT_DESKTOP", ""):
        return
    try:
        saida = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True, text=True, timeout=2,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return
    if hasattr(app.styleHints(), "setColorScheme"):  # Qt 6.8+
        escuro = "prefer-dark" in saida
        app.styleHints().setColorScheme(Qt.ColorScheme.Dark if escuro else Qt.ColorScheme.Light)


class Campo(QLineEdit):
    """Campo de texto onde a seta para baixo passa o foco para a lista."""

    def __init__(self, lista):
        super().__init__()
        self.lista = lista

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key.Key_Down and self.lista.count():
            self.lista.setFocus()
            if self.lista.currentRow() < 0:
                self.lista.setCurrentRow(0)
        else:
            super().keyPressEvent(evento)


def main():
    cliente, trabalho = sys.argv[1], Path(sys.argv[2])
    projetos = sorted(
        (p.name for p in trabalho.iterdir() if p.is_dir() and f" - {cliente} - " in p.name),
        reverse=True,
    )

    seguir_tema_gnome()
    app = QApplication(sys.argv)
    aplicar_esquema(app)
    dialogo = QDialog()
    dialogo.setWindowTitle("Organizador")
    dialogo.setMinimumWidth(440)

    lista = QListWidget()
    lista.addItems(projetos)
    campo = Campo(lista)
    campo.setPlaceholderText("Ex: Jogo 1 vs Celtics")

    titulo = QLabel(f"<b>{cliente}</b>")
    fonte = titulo.font()
    fonte.setPointSizeF(fonte.pointSizeF() * 1.3)
    titulo.setFont(fonte)

    botoes = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    botoes.button(QDialogButtonBox.StandardButton.Ok).setText("Confirmar")
    botoes.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")

    layout = QVBoxLayout(dialogo)
    layout.setSpacing(8)
    layout.addWidget(titulo)
    layout.addWidget(QLabel("Novo projeto:"))
    layout.addWidget(campo)
    if projetos:
        layout.addWidget(QLabel("Ou retome um existente:"))
        layout.addWidget(lista)
    layout.addWidget(botoes)
    lista.setVisible(bool(projetos))

    escolha = []

    def aceitar():
        nome = campo.text().replace("/", "-").replace(":", "-").strip()
        if nome:
            escolha[:] = ["NOVO", nome]
        elif lista.currentItem():
            escolha[:] = ["EXISTENTE", lista.currentItem().text()]
        else:
            return
        dialogo.accept()

    campo.textChanged.connect(lambda texto: texto.strip() and lista.clearSelection())
    lista.itemClicked.connect(lambda _: campo.clear())
    lista.itemDoubleClicked.connect(lambda _: aceitar())
    botoes.accepted.connect(aceitar)
    botoes.rejected.connect(dialogo.reject)

    campo.setFocus()
    dialogo.show()
    dialogo.raise_()
    dialogo.activateWindow()
    if dialogo.exec() and escolha:
        print("|".join(escolha))


if __name__ == "__main__":
    main()
