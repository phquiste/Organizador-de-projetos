#!/usr/bin/env python3
"""Janela de escolha de projeto para o GNOME (GTK4 + libadwaita).

Imprime "NOVO|nome" ou "EXISTENTE|pasta". Sai com código 2 se faltar
GTK4/libadwaita, e o organizador.sh usa a janela Qt no lugar.
"""
import re
import sys
import unicodedata
from pathlib import Path

try:
    import gi
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gdk", "4.0")
    gi.require_version("Adw", "1")
    from gi.repository import Adw, Gdk, Gio, GLib, Gtk
    if not hasattr(Adw, "EntryRow"):
        raise ImportError
except (ImportError, ValueError):
    sys.exit(2)


APP_ID = "local.organizador.dialogo"


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


class Janela(Adw.ApplicationWindow):
    def __init__(self, app, cliente, projetos, escolha):
        super().__init__(application=app, title="Organizador", default_width=440, resizable=False)
        self.escolha = escolha

        cancelar = Gtk.Button(label="Cancelar")
        cancelar.connect("clicked", lambda _: self.close())
        confirmar = Gtk.Button(label="Confirmar")
        confirmar.add_css_class("suggested-action")
        confirmar.connect("clicked", lambda _: self.aceitar())

        cabecalho = Adw.HeaderBar(show_start_title_buttons=False, show_end_title_buttons=False)
        cabecalho.set_title_widget(Adw.WindowTitle(title=cliente, subtitle=""))
        cabecalho.pack_start(cancelar)
        cabecalho.pack_end(confirmar)

        self.campo = Adw.EntryRow(title="Nome do projeto")
        self.campo.connect("entry-activated", lambda _: self.aceitar())
        self.campo.connect("changed", self.ao_digitar)
        teclas = Gtk.EventControllerKey(propagation_phase=Gtk.PropagationPhase.CAPTURE)
        teclas.connect("key-pressed", self.ao_tecla_no_campo)
        self.campo.add_controller(teclas)

        novo = Adw.PreferencesGroup(title="Novo projeto")
        novo.add(self.campo)

        corpo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        for lado in ("top", "bottom", "start", "end"):
            getattr(corpo, f"set_margin_{lado}")(18)
        corpo.append(novo)

        self.lista = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.lista.add_css_class("boxed-list")
        self.pastas = {}
        for pasta in projetos:
            data, nome = separar_nome(pasta)
            linha = Adw.ActionRow(title=GLib.markup_escape_text(nome), subtitle=GLib.markup_escape_text(data))
            linha.set_activatable(True)
            self.pastas[linha] = pasta
            self.lista.append(linha)
        self.lista.connect("row-selected", self.ao_selecionar)
        self.lista.connect("row-activated", lambda _, __: self.aceitar())

        if projetos:
            rolagem = Gtk.ScrolledWindow(propagate_natural_height=True, max_content_height=280)
            rolagem.set_child(self.lista)
            retomar = Adw.PreferencesGroup(title="Retomar projeto")
            retomar.add(rolagem)
            corpo.append(retomar)

        raiz = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        raiz.append(cabecalho)
        raiz.append(corpo)
        self.set_content(raiz)

        esc = Gtk.EventControllerKey(propagation_phase=Gtk.PropagationPhase.CAPTURE)
        esc.connect("key-pressed", self.ao_tecla_na_janela)
        self.add_controller(esc)
        self.campo.grab_focus()

    def ao_digitar(self, campo):
        if campo.get_text().strip():
            self.lista.unselect_all()

    def ao_selecionar(self, _, linha):
        if linha is not None:
            self.campo.set_text("")

    def ao_tecla_no_campo(self, _, tecla, *resto):
        primeira = self.lista.get_row_at_index(0)
        if tecla == Gdk.KEY_Down and primeira is not None:
            self.lista.select_row(primeira)
            primeira.grab_focus()
            return True
        return False

    def ao_tecla_na_janela(self, _, tecla, *resto):
        if tecla == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def aceitar(self):
        nome = self.campo.get_text().replace("/", "-").replace(":", "-").strip()
        linha = self.lista.get_selected_row()
        if nome:
            self.escolha[:] = ["NOVO", nome]
        elif linha is not None:
            self.escolha[:] = ["EXISTENTE", self.pastas[linha]]
        else:
            return
        self.close()


def main():
    cliente, trabalho = sys.argv[1], Path(sys.argv[2])
    projetos = listar_projetos(cliente, trabalho)
    escolha = []

    app = Adw.Application(application_id=APP_ID, flags=Gio.ApplicationFlags.NON_UNIQUE)
    # Segue o tema do sistema (claro/escuro) e a cor de destaque do GNOME
    app.get_style_manager().set_color_scheme(Adw.ColorScheme.DEFAULT)
    app.connect("activate", lambda a: Janela(a, cliente, projetos, escolha).present())
    app.run(None)

    if escolha:
        print("|".join(escolha))


if __name__ == "__main__":
    main()
