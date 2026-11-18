#!/usr/bin/env python3
"""Janela de escolha de projeto para o GNOME (GTK4 + libadwaita).

Imprime "NOVO|nome" ou "EXISTENTE|pasta". Sai com código 2 se faltar
GTK4/libadwaita, e o organizador.sh usa a janela Qt no lugar.
"""
import os
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


class Janela(Adw.ApplicationWindow):
    def __init__(self, app, cliente, projetos, escolha):
        super().__init__(application=app, title="Organizador", default_width=440, resizable=False)
        self.escolha = escolha
        self.termo_filtro = ""
        self._ignorando_texto = False
        self.set_icon_name("folder")

        cancelar = Gtk.Button(label="Cancelar")
        cancelar.connect("clicked", lambda _: self.close())
        confirmar = Gtk.Button(label="Confirmar")
        confirmar.add_css_class("suggested-action")
        confirmar.connect("clicked", lambda _: self.aceitar())

        cabecalho = Adw.HeaderBar(show_start_title_buttons=False, show_end_title_buttons=False)
        cabecalho.set_title_widget(Adw.WindowTitle(title=cliente, subtitle=""))
        cabecalho.pack_start(cancelar)
        cabecalho.pack_end(confirmar)

        self.campo = Adw.EntryRow(title="Nome do projeto ou filtrar existentes")
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
        self.chaves_busca = {}
        for pasta in projetos:
            data, nome = separar_nome(pasta)
            linha = Adw.ActionRow(title=GLib.markup_escape_text(nome), subtitle=GLib.markup_escape_text(data))
            linha.set_activatable(True)
            self.pastas[linha] = pasta
            self.chaves_busca[linha] = normalizar(f"{nome} {data}")
            self.lista.append(linha)
        self.lista.set_filter_func(self.filtrar_linha)
        self.lista.connect("row-selected", self.ao_selecionar)
        self.lista.connect("row-activated", lambda _, __: self.aceitar())

        self.retomar = None
        if projetos:
            rolagem = Gtk.ScrolledWindow(propagate_natural_height=True, max_content_height=280)
            rolagem.set_child(self.lista)
            self.retomar = Adw.PreferencesGroup(title="Retomar projeto")
            self.retomar.add(rolagem)
            corpo.append(self.retomar)

        raiz = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        raiz.append(cabecalho)
        raiz.append(corpo)
        self.set_content(raiz)

        esc = Gtk.EventControllerKey(propagation_phase=Gtk.PropagationPhase.CAPTURE)
        esc.connect("key-pressed", self.ao_tecla_na_janela)
        self.add_controller(esc)
        self.campo.grab_focus()

    def filtrar_linha(self, linha):
        return not self.termo_filtro or self.termo_filtro in self.chaves_busca.get(linha, "")

    def ao_digitar(self, campo):
        if self._ignorando_texto:
            return
        texto = campo.get_text()
        self.termo_filtro = normalizar(texto)
        if texto.strip():
            self.lista.unselect_all()
        self.lista.invalidate_filter()
        if self.retomar is not None:
            alguma_visivel = any(self.filtrar_linha(linha) for linha in self.pastas)
            self.retomar.set_visible(alguma_visivel)

    def ao_selecionar(self, _, linha):
        if linha is not None and self.campo.get_text():
            self._ignorando_texto = True
            self.campo.set_text("")
            self._ignorando_texto = False

    def ao_tecla_no_campo(self, _, tecla, *resto):
        if tecla == Gdk.KEY_Down:
            idx = 0
            while (linha := self.lista.get_row_at_index(idx)) is not None:
                if self.filtrar_linha(linha):
                    self.lista.select_row(linha)
                    linha.grab_focus()
                    return True
                idx += 1
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
    app.get_style_manager().set_color_scheme(Adw.ColorScheme.DEFAULT)
    app.connect("activate", lambda a: Janela(a, cliente, projetos, escolha).present())
    app.run(None)

    if escolha:
        print("|".join(escolha))


if __name__ == "__main__":
    main()
