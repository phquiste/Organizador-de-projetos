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
    from PyQt6.QtGui import QIcon
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
    os.environ.setdefault("QT_WAYLAND_DECORATION", "adwaita")


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
    if hasattr(app.styleHints(), "setColorScheme"):
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


def ultima_atividade(pasta):
    """Timestamp mais recente entre a pasta do projeto, subpastas e seus arquivos."""
    try:
        mais_recente = pasta.stat().st_mtime
        for raiz, dirs, arqs in os.walk(pasta):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for nome in (*dirs, *arqs):
                if nome.startswith("."):
                    continue
                try:
                    mtime = os.stat(os.path.join(raiz, nome)).st_mtime
                    if mtime > mais_recente:
                        mais_recente = mtime
                except OSError:
                    pass
        return mais_recente
    except OSError:
        return 0.0


def listar_projetos(cliente, trabalho):
    try:
        pastas = [
            p for p in trabalho.iterdir()
            if p.is_dir() and not p.name.startswith(".") and eh_do_cliente(p.name, cliente)
        ]
    except OSError:
        return []
    pastas.sort(key=lambda p: (ultima_atividade(p), p.name), reverse=True)
    return [p.name for p in pastas]


def separar_nome(pasta):
    """Divide 'AA-MM-DD - Cliente - Nome' em (data, nome). Fora desse formato, devolve ('', pasta)."""
    partes = re.split(r"\s+[-–—]\s+", pasta, maxsplit=2)
    return (partes[0], partes[2]) if len(partes) == 3 else ("", pasta)


class Campo(QLineEdit):
    """Campo de texto onde a seta para baixo passa o foco para o primeiro item visível da lista."""

    def __init__(self, lista):
        super().__init__()
        self.lista = lista

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key.Key_Down:
            for row in range(self.lista.count()):
                if not self.lista.item(row).isHidden():
                    self.lista.setFocus()
                    self.lista.setCurrentRow(row)
                    return
        super().keyPressEvent(evento)


def main():
    cliente, trabalho = sys.argv[1], Path(sys.argv[2])
    projetos = listar_projetos(cliente, trabalho)

    seguir_tema_gnome()
    app = QApplication(sys.argv)
    aplicar_esquema(app)
    app.setDesktopFileName("local.organizador.dialogo")
    icone = QIcon.fromTheme("folder", QIcon.fromTheme("inode-directory"))
    app.setWindowIcon(icone)
    dialogo = QDialog()
    dialogo.setWindowIcon(icone)
    dialogo.setWindowTitle(cliente)
    dialogo.setMinimumWidth(440)

    lista = QListWidget()
    for pasta in projetos:
        data, nome = separar_nome(pasta)
        item = QListWidgetItem(f"{nome}\n{data}" if data else nome)
        item.setData(Qt.ItemDataRole.UserRole, pasta)
        item.setData(Qt.ItemDataRole.UserRole + 1, normalizar(f"{nome} {data}"))
        lista.addItem(item)
    campo = Campo(lista)
    campo.setPlaceholderText("Nome do projeto ou filtrar existentes")

    botoes = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    botoes.button(QDialogButtonBox.StandardButton.Ok).setText("Confirmar")
    botoes.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")

    rotulo_retomar = QLabel("Retomar projeto")
    # Sem resultados no filtro, o rótulo e a lista somem, mas continuam reservando o espaço deles:
    # assim o campo de texto e os botões não saem do lugar.
    for widget in (rotulo_retomar, lista):
        politica = widget.sizePolicy()
        politica.setRetainSizeWhenHidden(True)
        widget.setSizePolicy(politica)
    layout = QVBoxLayout(dialogo)
    layout.setSpacing(8)
    layout.addWidget(QLabel("Novo projeto"))
    layout.addWidget(campo)
    if projetos:
        layout.addWidget(rotulo_retomar)
        layout.addWidget(lista)
    layout.addWidget(botoes)
    lista.setVisible(bool(projetos))

    escolha = []

    def filtrar_lista(texto):
        termo = normalizar(texto)
        if termo:
            lista.clearSelection()
        visiveis = 0
        for row in range(lista.count()):
            item = lista.item(row)
            combina = not termo or termo in item.data(Qt.ItemDataRole.UserRole + 1)
            item.setHidden(not combina)
            if combina:
                visiveis += 1
        rotulo_retomar.setVisible(bool(projetos) and visiveis > 0)
        lista.setVisible(bool(projetos) and visiveis > 0)

    def ao_selecionar_lista():
        if lista.selectedItems() and campo.text():
            campo.blockSignals(True)
            campo.clear()
            campo.blockSignals(False)

    def aceitar():
        nome = campo.text().replace("/", "-").replace(":", "-").strip()
        if nome:
            escolha[:] = ["NOVO", nome]
        elif lista.selectedItems():
            escolha[:] = ["EXISTENTE", lista.selectedItems()[0].data(Qt.ItemDataRole.UserRole)]
        else:
            return
        dialogo.accept()

    campo.textChanged.connect(filtrar_lista)
    lista.itemSelectionChanged.connect(ao_selecionar_lista)
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
