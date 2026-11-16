#!/usr/bin/env python3
"""Janela de escolha de projeto (Qt, usada fora do GNOME).

Imprime "NOVO|nome" ou "EXISTENTE|pasta". Usa o visual nativo do sistema.
"""
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QApplication, QDialog, QDialogButtonBox, QLabel,
        QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout,
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


def normalizar(texto):
    """Minúsculas, sem acentos, e qualquer traço, ponto ou espaço vira um espaço só."""
    texto = unicodedata.normalize("NFKD", texto).casefold()
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", " ", texto).strip()


def eh_do_cliente(pasta, cliente):
    """True se o nome do cliente vem logo depois da data. Caixa, acento e tipo de traço não importam."""
    nome = re.sub(r"^(\d+ ){1,3}", "", normalizar(pasta))
    return (nome + " ").startswith(normalizar(cliente) + " ")


def listar_projetos(cliente, trabalho):
    pastas = (
        p.name for p in trabalho.iterdir()
        if p.is_dir() and not p.name.startswith(".") and eh_do_cliente(p.name, cliente)
    )
    return sorted(pastas, reverse=True)


def separar_nome(pasta):
    """Divide 'AA-MM-DD - Cliente - Nome' em (data, nome). Fora desse formato, devolve ('', pasta)."""
    partes = re.split(r"\s+[-–—]\s+", pasta, maxsplit=2)
    return (partes[0], partes[2]) if len(partes) == 3 else ("", pasta)


class Campo(QLineEdit):
    """Campo de texto onde a seta para baixo passa o foco para a lista."""

    def __init__(self, lista):
        super().__init__()
        self.lista = lista

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key.Key_Down and self.lista.count():
            self.lista.setFocus()
            self.lista.setCurrentRow(0)
        else:
            super().keyPressEvent(evento)


def main():
    cliente, trabalho = sys.argv[1], Path(sys.argv[2])
    projetos = listar_projetos(cliente, trabalho)

    seguir_tema_gnome()
    app = QApplication(sys.argv)
    aplicar_esquema(app)
    dialogo = QDialog()
    dialogo.setWindowTitle(cliente)
    dialogo.setMinimumWidth(440)

    lista = QListWidget()
    for pasta in projetos:
        data, nome = separar_nome(pasta)
        item = QListWidgetItem(f"{nome}\n{data}" if data else nome)
        item.setData(Qt.ItemDataRole.UserRole, pasta)
        lista.addItem(item)
    campo = Campo(lista)
    campo.setPlaceholderText("Nome do projeto")

    botoes = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    botoes.button(QDialogButtonBox.StandardButton.Ok).setText("Confirmar")
    botoes.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")

    layout = QVBoxLayout(dialogo)
    layout.setSpacing(8)
    layout.addWidget(QLabel("Novo projeto"))
    layout.addWidget(campo)
    if projetos:
        layout.addWidget(QLabel("Retomar projeto"))
        layout.addWidget(lista)
    layout.addWidget(botoes)
    lista.setVisible(bool(projetos))

    escolha = []

    def aceitar():
        nome = campo.text().replace("/", "-").replace(":", "-").strip()
        if nome:
            escolha[:] = ["NOVO", nome]
        elif lista.selectedItems():
            escolha[:] = ["EXISTENTE", lista.selectedItems()[0].data(Qt.ItemDataRole.UserRole)]
        else:
            return
        dialogo.accept()

    campo.textChanged.connect(lambda texto: texto.strip() and lista.clearSelection())
    lista.itemSelectionChanged.connect(lambda: lista.selectedItems() and campo.clear())
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
