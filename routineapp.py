import os
import json
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty

# Désactiver le mode multitouch par défaut (clic droit qui font des points rouges)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

def resource_path(relative_path):
    try:
        # PyInstaller extrait dans un dossier temporaire
        base_path = sys._MEIPASS
    except AttributeError:
        # En exécution normale
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AutoResizeLabel(Label):
    # Optionnel : tu peux définir des propriétés comme un texte par défaut
    text_property = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._on_size)  # Reagir au changement de taille du parent

    def _on_size(self, instance, value):
        # Met à jour la taille du texte en fonction de la taille du parent
        self.text_size = (self.parent.width - 20, None)  # 20 pour laisser une marge
        self.texture_update()  # Recalcule la texture du label pour qu'il s'affiche correctement

    def on_parent(self, instance, parent):
        # Cette fonction est appelée quand le label est ajouté à un parent
        if parent:
            self._on_size(parent, parent.size)  # Ajuste immédiatement la taille

class MyTextInput(TextInput):
    def __init__(self, max_length=50, **kwargs):  # Ajout du paramètre max_length
        super().__init__(**kwargs)
        self.max_length = max_length  # Définir la longueur maximale
        self.size_hint_x = 0.7
        self.size_hint_y = None
        self.height = 40
        self.pos_hint = {'center_x': 0.5}
        self.background_color = (0.7, 0.7, 0.7, 0.6)  # Couleur de fond initiale
        self.foreground_color = (1, 1, 1, 1)

        self.halign = 'center'  # Centrage horizontal
        self.valign = 'middle'  # Centrage vertical
        self.multiline=False

        self.bind(size=self.update_padding, text=self.update_padding)
        self.update_padding()

        # Ajout de l'écouteur pour l'événement 'on_focus'
        self.bind(on_focus=self.on_focus)

    def update_padding(self, *args):
        self.padding = [10, (self.height - self.line_height) / 2]  # [horizontal, vertical]

    def on_focus(self, instance, value):
        """Change la couleur de fond lorsque le TextInput reçoit ou perd le focus."""
        if value:  # Quand le TextInput est sélectionné (focus)
            self.background_color = (0.7, 0.7, 0.7, 1)  # Moins opaque (opacité 1)
        else:  # Quand le TextInput perd le focus
            self.background_color = (0.7, 0.7, 0.7, 0.6)  # Opacité 0.6

    def insert_text(self, substring, from_undo=False):
        """Limite la saisie de texte selon le max_length."""
        if len(self.text) < self.max_length or substring == "":
            super().insert_text(substring, from_undo=from_undo)
            
class FocusableForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widgets_list = []
        Window.bind(on_key_down=self._on_key_down)

    def register_focusable(self, widget):
        """Enregistre les widgets qui peuvent être sélectionnés via TAB."""
        self.widgets_list.append(widget)

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 9:  # TAB
            # Filtrer les widgets activés uniquement
            enabled_widgets = [w for w in self.widgets_list if hasattr(w, 'focus') and getattr(w, 'disabled', False) is False]
            
            # Si aucun widget de formulaire n'est focalisé, on se concentre sur le premier bouton activé
            focused = next((i for i, w in enumerate(enabled_widgets) if hasattr(w, "focus") and w.focus), None)

            if focused is None:  # Aucune focus sur un widget, donc se concentrer sur le premier bouton
                # Chercher le premier bouton dans la liste activée
                first_button = next((w for w in enabled_widgets if isinstance(w, Button)), None)
                if first_button:
                    first_button.focus = True
                return True

            if focused is not None:
                # Si un widget est focalisé, on bascule le focus à l'autre widget
                enabled_widgets[focused].focus = False
                if 'shift' in modifiers:
                    next_index = (focused - 1) % len(enabled_widgets)
                else:
                    next_index = (focused + 1) % len(enabled_widgets)
                enabled_widgets[next_index].focus = True
                return True

        elif key == 13:  # ENTER
            focused_btn = next((w for w in self.widgets_list if isinstance(w, Button) and w.focus), None)
            if focused_btn:
                focused_btn.trigger_action(duration=0)
                return True

        return False

class HoverBehavior:
    hovered = BooleanProperty(False)
    border_point= None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return  # Widget pas affiché
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        self.hovered = inside
        self.on_hover(inside)

    def on_hover(self, hovered):
        pass  # À surcharger si besoin

class StyledButton(FocusBehavior, HoverBehavior, Button):
    def __init__(self, opacity=0.6, **kwargs):
        super().__init__(**kwargs)
        self.opacity_normal = opacity
        self.opacity_focus = 1.0
        self.opacity_hover = 0.85
        self.selected = False
        

        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            self.bg_color = Color(0.7, 0.7, 0.7, self.opacity_normal)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[30])
            self.border_color = Color(0, 0, 0, 1)
            self.border_line = Line(width=1.5)

        self.bind(pos=self.update_graphics, size=self.update_graphics,
                  focus=self.on_focus, hovered=self.on_hover)

    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (
            self.x, self.y, self.width, self.height, 30
        )

    def on_focus(self, instance, value):
        self.update_opacity()

    def on_hover(self, *args):
        self.update_opacity()

    def update_opacity(self):
        if self.selected:  # <-- Priorité au bouton sélectionné
            self.bg_color.a = self.opacity_focus
        elif self.focus:
            self.bg_color.a = self.opacity_focus
        elif self.hovered:
            self.bg_color.a = self.opacity_hover
        else:
            self.bg_color.a = self.opacity_normal

class RoutineApp(App):
    FILE_PATH = "necessary/routinesV3.json"  # Définition du chemin du fichier JSON

    with open("necessary/language.json", 'r', encoding='utf-8') as f:
        dictlanguage = json.load(f)

    def build(self):
        self.routines_data = self.charger_routines()
        self.routines = self.routines_data.get("routines", {})
        self.current_language = self.routines_data["language"]

        self.root = FloatLayout()
        self.background_image = Image(allow_stretch=True, keep_ratio=False)
        self.root.add_widget(self.background_image)

        self.content_container = BoxLayout()
        self.root.add_widget(self.content_container)

        # Affichage selon "premiere_fois"
        if self.routines_data.get("first_time", True):
            self.set_root_content(self.page_bienvenue())
            self.routines_data["first_time"] = False
            self.sauvegarder_routines()
        else:
            self.set_root_content(self.page_accueil())

        Window.bind(size=self.update_background_image)
        self.update_background_image()
        Window.bind(size=self.update_lang_button_text)
        Window.bind(size=lambda *args: self.update_dropdown_language_buttons())

        return self.root

    def set_root_content(self, new_content):
        self.content_container.clear_widgets()
        self.content_container.add_widget(new_content)

    def page_bienvenue(self):
        layout = FloatLayout()

        # Texte de bienvenue
        box = BoxLayout(orientation="vertical", padding=10)
        label = Label(text=self.dictlanguage[self.current_language]["welcome_page"],
                    font_size=24, halign="center", valign="middle")
        label.bind(size=label.setter('text_size'))
        box.add_widget(label)
        layout.add_widget(box)

        # Gestion du changement de page au clic
        layout.bind(on_touch_down=lambda *args: self.set_root_content(self.page_accueil()))

        return layout

    def update_background_image(self, *args):
        if Window.height > Window.width:
            self.background_image.source = resource_path('images/fondportraitbienvenue.jpg')
        else:
            self.background_image.source = resource_path('images/fondpaysagebienvenue.png')

    def update_lang_button_text(self, *args):
        lang = self.routines_data["language"]
        if Window.width < Window.height:
            self.main_lang_btn.text = lang[:2]
        else:
            self.main_lang_btn.text = lang

    def update_dropdown_language_buttons(self):
        if not hasattr(self, 'dropdown_buttons'):
            return
        for btn in self.dropdown_buttons:
            lang = btn.full_text
            if Window.width < Window.height:
                btn.text = lang[:2]
            else:
                btn.text = lang

    def adjust_button_text(self, text):
        words = text.split()
        if len(words) > 2 and Window.width < Window.height:  # Mode portrait
            return ' '.join(words[:2])
        return text
    
    def on_window_resize(self, instance, width, height):
        if hasattr(self, "routine_buttons"):
            for btn, nom in self.routine_buttons:
                btn.text = self.adjust_button_text(nom)
    
    def changer_langue(self, langue):
        # Charger les données JSON
        with open(self.FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Modifier la langue
        data["language"] = langue

        # Sauvegarder le fichier
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.current_language = langue  # Met à jour la langue active
        self.set_root_content(self.page_accueil())  # Recharge linterface
        
    def page_accueil(self):
        layout = FloatLayout()

        # Contenu principal (routines et boutons)
        content = FocusableForm(orientation="vertical", spacing=10, padding=10, size_hint=(1, 1))

        # --- MENU LANGUE ---
        top_buttons = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=10)

        # Bouton principal qui ouvre le menu déroulant
        self.main_lang_btn = StyledButton(text="", size_hint=(0.1, 1))
        self.update_lang_button_text()  # Appliquer le bon texte selon orientation

        dropdown = DropDown()
        self.dropdown_buttons = []  # Stocke les boutons du menu déroulant

        for lang in self.dictlanguage:
            btn = StyledButton(text="", size_hint_y=None, height=44, opacity=1)
            btn.full_text = lang

            def on_lang_select(btn_instance, dropdown=dropdown):
                selected_lang = btn_instance.full_text
                self.routines_data["language"] = selected_lang
                self.current_language = selected_lang
                self.sauvegarder_routines()
                self.update_lang_button_text()
                self.update_dropdown_language_buttons()
                dropdown.dismiss()
                Clock.schedule_once(lambda dt: self.set_root_content(self.page_accueil()), 0.1)

            btn.bind(on_release=on_lang_select)
            dropdown.add_widget(btn)
            self.dropdown_buttons.append(btn)

        self.update_dropdown_language_buttons()
        self.main_lang_btn.bind(on_release=lambda btn: Clock.schedule_once(lambda dt: dropdown.open(btn), 0.01))
        top_buttons.add_widget(self.main_lang_btn)

        # --- BOUTON "Ajouter une routine" ---
        btn2 = StyledButton(text=self.dictlanguage[self.current_language]["home_page"], size_hint=(0.9, 1))
        btn2.bind(on_press=lambda *args: self.set_root_content(self.page_ajouter_routine()))
        top_buttons.add_widget(btn2)

        content.add_widget(top_buttons)

        # --- Scroll des routines ---
        scroll = ScrollView(size_hint=(1, 0.8))
        routine_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        routine_layout.bind(minimum_height=routine_layout.setter("height"))

        # -- Liste des boutons stockés pour le resize
        self.routine_buttons = []

        routines_list = list(self.routines.items())
        for index, (nom, _) in enumerate(routines_list):
            routine_box = BoxLayout(size_hint_y=None, height=50, spacing=10)

            btn = StyledButton(text=self.adjust_button_text(nom), size_hint=(0.7, 1))
            btn.bind(on_press=lambda instance, r=nom: self.set_root_content(self.page_routine(r)))
            routine_box.add_widget(btn)
            content.register_focusable(btn)

            # Stocker bouton + nom pour redimensionnement
            self.routine_buttons.append((btn, nom))

            up_btn = StyledButton(text="↑", font_name="necessary/arial.ttf", size_hint=(0.1, 1))
            up_btn.bind(on_press=lambda instance, i=index: self.deplacer_routine(i, -1))
            routine_box.add_widget(up_btn)

            down_btn = StyledButton(text="↓", font_name="necessary/arial.ttf", size_hint=(0.1, 1))
            down_btn.bind(on_press=lambda instance, i=index: self.deplacer_routine(i, 1))
            routine_box.add_widget(down_btn)

            delete_btn = StyledButton(text="X", size_hint=(0.1, 1))
            delete_btn.bind(on_press=lambda instance, r=nom: self.confirmer_suppression_routine(r))
            routine_box.add_widget(delete_btn)

            routine_layout.add_widget(routine_box)

        scroll.add_widget(routine_layout)
        content.add_widget(scroll)

        layout.add_widget(content)

        # Enregistrer les boutons pour la navigation "Tab"
        content.register_focusable(self.main_lang_btn)
        content.register_focusable(btn2)

        # 🔁 Réagir au redimensionnement de la fenêtre
        Window.unbind(on_resize=self.on_window_resize)
        Window.bind(on_resize=self.on_window_resize)

        return layout

    def deplacer_routine(self, index, direction):
        routines_list = list(self.routines.items())
        new_index = index + direction
        if 0 <= new_index < len(routines_list):
            routines_list[index], routines_list[new_index] = routines_list[new_index], routines_list[index]
            self.routines = {nom: data for nom, data in routines_list}
            self.sauvegarder_routines()
            self.set_root_content(self.page_accueil())

    def confirmer_suppression_routine(self, nom):
        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        popup_layout.add_widget(AutoResizeLabel(text=f"{self.dictlanguage[self.current_language]['confirmation'][1]} {nom} ?",halign="center", valign="middle", font_size=20))
        btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        popup = Popup(title=self.dictlanguage[self.current_language]["confirmation"][0], content=popup_layout, size_hint=(0.8, 0.4))

        oui_btn = StyledButton(text=self.dictlanguage[self.current_language]["confirmation"][2])
        oui_btn.bind(on_press=lambda *args: self.supprimer_routine(nom, popup))
        non_btn = StyledButton(text=self.dictlanguage[self.current_language]["confirmation"][3])
        non_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(oui_btn)
        btn_layout.add_widget(non_btn)
        popup_layout.add_widget(btn_layout)

        popup.open()

    def supprimer_routine(self, nom, popup):
        if nom in self.routines:
            del self.routines[nom]
            self.sauvegarder_routines()
        popup.dismiss()
        self.set_root_content(self.page_accueil())

    def page_ajouter_routine(self):
        # Utiliser FocusableForm comme conteneur principal
        layout = FocusableForm(orientation="vertical", spacing=10, padding=10)

        # Espace vide en haut (10% de l'écran)
        layout.add_widget(Widget(size_hint=(1, 0.1)))

        # Label centré horizontalement
        label = Label(
            text=self.dictlanguage[self.current_language]["add_routine"][0],
            font_size=30,
            size_hint=(1, None),
            height=40,
            halign="center",
            valign="middle"
        )
        label.bind(size=label.setter('text_size'))  # Nécessaire pour centrer le texte
        layout.add_widget(label)

        # Champ de saisie juste en dessous du label
        routine_name_input = MyTextInput(size_hint=(1, None), max_length=20,height=40)
        layout.register_focusable(routine_name_input)  # Enregistrer le champ de texte pour qu'il soit focusable
        layout.add_widget(routine_name_input)

        # Espace vide pour pousser les boutons vers le bas
        layout.add_widget(Widget())  # Prend tout l'espace restant au milieu

        # Boutons en bas (20% de hauteur)
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        
        terminer_btn = StyledButton(text=self.dictlanguage[self.current_language]["add_routine"][1])
        layout.register_focusable(terminer_btn)  # Enregistrer le bouton pour qu'il soit focusable
        terminer_btn.bind(on_press=lambda *args: self.ajouter_routine(routine_name_input.text))
        
        annuler_btn = StyledButton(text=self.dictlanguage[self.current_language]["add_routine"][2])
        layout.register_focusable(annuler_btn)  # Enregistrer l'autre bouton pour qu'il soit focusable
        annuler_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))

        btn_layout.add_widget(terminer_btn)
        btn_layout.add_widget(annuler_btn)

        layout.add_widget(btn_layout)

        return layout

    def ajouter_routine(self, nom):
        if nom.strip():
            self.routines[nom] = {"name": nom, "fonctions": []}
            self.sauvegarder_routines()
        self.set_root_content(self.page_accueil())
        
    def page_routine(self, nom):
        routine = self.routines[nom]
        layout = FocusableForm(orientation="vertical", spacing=5, padding=[10, 10, 10, 10])
        layout.add_widget(Widget(size_hint=(1, None), height=10))

        # Titre centré avec AutoResizeLabel
        title_label = AutoResizeLabel(
            text=f"{self.dictlanguage[self.current_language]['routine_page'][0]} {routine['name']}",
            font_size=22,
            size_hint=(1, None),
            height=40,
            halign="center",
            valign="middle",
        )
        title_label.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (value[0] - 20, None))
        )
        layout.add_widget(title_label)

        layout.add_widget(Widget(size_hint=(1, None), height=10))

        # ScrollView contenant les exercices
        scroll = ScrollView(size_hint=(1, 0.70))
        exercice_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=20, padding=[0, 5])
        exercice_layout.bind(minimum_height=exercice_layout.setter("height"))

        for index, ex in enumerate(routine["fonctions"]):
            ex_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)

            if ex["duration"]:
                texte = (
                    f"{ex['name']}\n"
                    f"{ex['repetitions']} {self.dictlanguage[self.current_language]['routine_page'][1]}, "
                    f"{ex['duration']}{self.dictlanguage[self.current_language]['routine_page'][2]}"
                )
            else:
                texte = (
                    f"{ex['name']}\n"
                    f"{ex['repetitions']} {self.dictlanguage[self.current_language]['routine_page'][1]}, "
                    f"{ex['units']} {self.dictlanguage[self.current_language]['routine_page'][3]}"
                )

            label = Label(
                text=texte,
                size_hint=(0.5, 1),
                halign="center",
                valign="middle"
            )
            label.bind(
                size=lambda instance, value: setattr(instance, 'text_size', value)
            )

            ex_layout.add_widget(label)

            # Boutons pour chaque exercice
            up_btn = StyledButton(text="↑", font_name="necessary/arial.ttf", size_hint=(0.1, 1))
            up_btn.bind(on_press=lambda instance, i=index: self.deplacer_exercice(nom, i, -1))
            layout.register_focusable(up_btn)
            ex_layout.add_widget(up_btn)

            down_btn = StyledButton(text="↓", font_name="necessary/arial.ttf", size_hint=(0.1, 1))
            down_btn.bind(on_press=lambda instance, i=index: self.deplacer_exercice(nom, i, 1))
            layout.register_focusable(down_btn)
            ex_layout.add_widget(down_btn)

            modify_btn = StyledButton(text="\N{pencil}", font_name='necessary/SegoeUIEmoji.TTF', size_hint=(0.1, 1))
            modify_btn.bind(on_press=lambda instance, i=index: self.set_root_content(self.page_modifier_exercice(nom, i)))
            layout.register_focusable(modify_btn)
            ex_layout.add_widget(modify_btn)

            exercice_layout.add_widget(ex_layout)

        scroll.add_widget(exercice_layout)
        layout.add_widget(scroll)

        # Boutons bas de page
        ligne1 = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        add_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["routine_page"][5],  # "Add"
            size_hint=(0.5, 1)
        )
        add_btn.bind(on_press=lambda *args: self.set_root_content(self.page_modifier_routine(nom)))
        layout.register_focusable(add_btn)

        rename_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["routine_page"][7],  # "Rename"
            size_hint=(0.5, 1)
        )
        rename_btn.bind(on_press=lambda *args: self.set_root_content(self.page_renommer_routine(nom)))
        layout.register_focusable(rename_btn)

        ligne1.add_widget(add_btn)
        ligne1.add_widget(rename_btn)
        layout.add_widget(ligne1)

        # Deuxième ligne : Lancer et Retour
        ligne2 = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        has_exercices = len(routine["fonctions"]) > 0
        lancer_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["routine_page"][4],  # "Start"
            size_hint=(0.5, 1),
            disabled=not has_exercices
        )
        lancer_btn.bind(on_press=lambda *args: self.lancer_routine(nom))
        layout.register_focusable(lancer_btn)

        retour_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["routine_page"][6],  # "Back"
            size_hint=(0.5, 1)
        )
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))
        layout.register_focusable(retour_btn)

        ligne2.add_widget(lancer_btn)
        ligne2.add_widget(retour_btn)
        layout.add_widget(ligne2)

        return layout

    def page_renommer_routine(self, nom):
        layout = FocusableForm(orientation="vertical", spacing=10, padding=10)

        # Espace vide en haut (10%)
        layout.add_widget(Widget(size_hint=(1, 0.1)))

        # Titre centré
        label = Label(
            text=self.dictlanguage[self.current_language].get("rename_routine", "Rename the routine"),
            font_size=30,
            size_hint=(1, None),
            height=40,
            halign="center",
            valign="middle"
        )
        label.bind(size=label.setter('text_size'))
        layout.add_widget(label)

        # Champ de texte
        routine_name_input = MyTextInput(
            text=self.routines[nom]["name"],
            size_hint=(1, None),
            height=40,
            max_length=20
        )
        layout.register_focusable(routine_name_input)
        layout.add_widget(routine_name_input)

        # Espace pour pousser les boutons vers le bas
        layout.add_widget(Widget())

        # Boutons (20% de hauteur)
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)

        valider_btn = StyledButton(text=self.dictlanguage[self.current_language].get("confirm", "Confirm"))
        layout.register_focusable(valider_btn)
        retour_btn = StyledButton(text=self.dictlanguage[self.current_language]["routine_page"][6])  # "Back"
        layout.register_focusable(retour_btn)

        def valider_renommage(instance):
            nouveau_nom = routine_name_input.text.strip()
            if nouveau_nom and nouveau_nom != nom and nouveau_nom not in self.routines:
                # Conserver l’ordre
                nouvelles_routines = {}
                for k, v in self.routines.items():
                    if k == nom:
                        nouvelles_routines[nouveau_nom] = v
                        nouvelles_routines[nouveau_nom]["name"] = nouveau_nom
                    else:
                        nouvelles_routines[k] = v
                self.routines = nouvelles_routines
                self.routines_data["routines"] = self.routines
                self.sauvegarder_routines()
                self.set_root_content(self.page_routine(nouveau_nom))
            else:
                self.set_root_content(self.page_routine(nom))  # Pas de renommage si nom invalide

        valider_btn.bind(on_press=valider_renommage)
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))

        btn_layout.add_widget(valider_btn)
        btn_layout.add_widget(retour_btn)

        layout.add_widget(btn_layout)

        return layout

    def page_modifier_exercice(self, nom, index):
        routine = self.routines[nom]
        ex = routine["fonctions"][index]
        layout = FocusableForm(orientation="vertical", spacing=5, padding=[10, 10, 10, 10])

        scroll = ScrollView(size_hint=(1, 0.85))
        content = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(Widget(size_hint=(1, None), height=20))
        content.add_widget(AutoResizeLabel(
            text=f"{self.dictlanguage[self.current_language]['change_routine'][19]} {ex['name']}",  # Nouveau texte à ajouter dans ton dictionnaire de langue
            font_size=22,
            size_hint=(1, None),
            height=40,
            halign="center"
        ))

        def add_field(label_text, default_text="", length=20):
            content.add_widget(Label(text=label_text, size_hint=(1, None), height=25))
            input_widget = MyTextInput(text=default_text, size_hint=(1, None), max_length=length, height=40)
            content.add_widget(input_widget)
            layout.register_focusable(input_widget)
            return input_widget

        content.add_widget(Widget(size_hint=(1, None), height=10))

        exercice_name_input = add_field(self.dictlanguage[self.current_language]["change_routine"][1], ex["name"])

        is_duration = "duration" in ex and ex["duration"]
        valeur_init = ex["duration"] if is_duration else ex.get("units", "")
        exercice_valeur_input = add_field(self.dictlanguage[self.current_language]["change_routine"][8], str(valeur_init), 5)

        selected_type = {"value": "duration" if is_duration else "unit"}

        def update_type(new_type):
            selected_type["value"] = new_type
            duree_btn.selected = (new_type == "duration")
            unite_btn.selected = (new_type == "unit")
            duree_btn.update_opacity()
            unite_btn.update_opacity()

        type_btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        duree_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][2],
            size_hint=(0.5, None), height=40
        )
        unite_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][5],
            size_hint=(0.5, None), height=40
        )

        update_type(selected_type["value"])

        duree_btn.bind(on_press=lambda btn: update_type("duration"))
        unite_btn.bind(on_press=lambda btn: update_type("unit"))

        type_btn_layout.add_widget(duree_btn)
        type_btn_layout.add_widget(unite_btn)

        content.add_widget(type_btn_layout)
        layout.register_focusable(duree_btn)
        layout.register_focusable(unite_btn)

        exercice_reps_input = add_field(self.dictlanguage[self.current_language]["change_routine"][3], str(ex.get("repetitions", "")), 4)
        exercice_repos_input = add_field(self.dictlanguage[self.current_language]["change_routine"][4], str(ex.get("rest", "")), 4)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        enregistrer_btn = StyledButton(text=self.dictlanguage[self.current_language]["change_routine"][20], size_hint=(0.45, None), height=50)

        enregistrer_btn.bind(on_press=lambda *args: self.enregistrer_modification_exercice(
            nom, index,
            exercice_name_input.text,
            exercice_valeur_input.text if selected_type["value"] == "duration" else "",
            exercice_reps_input.text,
            exercice_repos_input.text,
            exercice_valeur_input.text if selected_type["value"] == "unit" else ""
        ))

        retour_btn = StyledButton(text=self.dictlanguage[self.current_language]["change_routine"][7], size_hint=(0.45, None), height=50)
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))

        remove_btn = StyledButton(text="X", size_hint=(0.1, None), height=50)
        remove_btn.bind(on_press=lambda instance, i=index: self.supprimer_exercice(nom, i))

        layout.register_focusable(enregistrer_btn)
        layout.register_focusable(retour_btn)
        layout.register_focusable(remove_btn)

        btn_layout.add_widget(enregistrer_btn)
        btn_layout.add_widget(retour_btn)
        btn_layout.add_widget(remove_btn)
        layout.add_widget(btn_layout)

        return layout

    def deplacer_exercice(self, routine_nom, index, direction):
        exercices = self.routines[routine_nom]["fonctions"]
        if 0 <= index + direction < len(exercices):
            exercices.insert(index + direction, exercices.pop(index))
            self.sauvegarder_routines()
            self.set_root_content(self.page_routine(routine_nom))

    def supprimer_exercice(self, routine_nom, index):
        del self.routines[routine_nom]["fonctions"][index]
        self.sauvegarder_routines()
        self.set_root_content(self.page_routine(routine_nom))

    def lancer_routine(self, nom):
        self.paused = False
        self.routine = self.routines[nom]
        self.current_exercise_index = 0
        self.current_repetition = 1
        self.is_resting = False
        self.remaining_time = self.routines[nom]["fonctions"][0]["duration"] if self.routines[nom]["fonctions"][0]["duration"] else 0

        self.routine_layout = FocusableForm(orientation="vertical", spacing=10, padding=10)  # Utiliser FocusableForm ici
        self.timer_label = AutoResizeLabel(text=self.dictlanguage[self.current_language]["start_routine"][0], font_size=24,
            halign='center',valign='middle')
        self.routine_layout.add_widget(self.timer_label)

        # Enregistrer les boutons comme focusables dans FocusableForm
        self.fait_btn = StyledButton(text=self.dictlanguage[self.current_language]["start_routine"][1], size_hint=(1, 0.2))
        self.fait_btn.bind(on_press=self.marquer_fait)
        self.fait_btn.disabled = True
        self.routine_layout.add_widget(self.fait_btn)
        self.routine_layout.register_focusable(self.fait_btn)  # Ajouter à la gestion du focus

        self.pause_btn = StyledButton(text=self.dictlanguage[self.current_language]["start_routine"][2], size_hint=(1, 0.2))
        self.pause_btn.bind(on_press=self.toggle_pause)
        self.routine_layout.add_widget(self.pause_btn)
        self.routine_layout.register_focusable(self.pause_btn)  # Ajouter à la gestion du focus

        # Nouveau bouton pour passer le temps de repos
        self.skip_rest_btn = StyledButton(text=self.dictlanguage[self.current_language]["start_routine"][3], size_hint=(1, 0.2))
        self.skip_rest_btn.bind(on_press=self.pass_rest_time)
        self.skip_rest_btn.disabled = True  # Ce bouton est désactivé tant qu'on n'est pas en période de repos
        self.routine_layout.add_widget(self.skip_rest_btn)
        self.routine_layout.register_focusable(self.skip_rest_btn)  # Ajouter à la gestion du focus

        stop_btn = StyledButton(text=self.dictlanguage[self.current_language]["start_routine"][4], size_hint=(1, 0.2))
        stop_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))
        self.routine_layout.add_widget(stop_btn)
        self.routine_layout.register_focusable(stop_btn)  # Ajouter à la gestion du focus

        self.set_root_content(self.routine_layout)
        Clock.schedule_interval(self.update_routine, 1.0)

    def toggle_pause(self, instance):
        self.paused = not self.paused
        instance.text = self.dictlanguage[self.current_language]["toggle_pause"][0] if self.paused else self.dictlanguage[self.current_language]["toggle_pause"][1]

    def pass_rest_time(self, instance):
        # Passer directement le temps de repos
        self.is_resting = False
        self.remaining_time = 0
        self.skip_rest_btn.disabled = True  # Désactiver le bouton après l'avoir utilisé

        # Passer à l'exercice suivant
        self.current_repetition += 1
        if self.current_repetition > self.routine["fonctions"][self.current_exercise_index]["repetitions"]:
            self.current_exercise_index += 1
            self.current_repetition = 1
        self.afficher_exercice()

    def update_routine(self, dt):
        if self.paused:
            return
        if self.current_exercise_index >= len(self.routine["fonctions"]):
            self.timer_label.text = self.dictlanguage[self.current_language]["update_routine"][0]
            Clock.unschedule(self.update_routine)
            return

        exercise = self.routine["fonctions"][self.current_exercise_index]

        if self.is_resting:
            self.skip_rest_btn.disabled = False  # Activer le bouton pour passer le temps de repos
            self.fait_btn.disabled = True  # Désactiver le bouton "Fait" pendant le repos
            if self.remaining_time > 0:
                self.timer_label.text = f"{self.dictlanguage[self.current_language]['update_routine'][1]} {self.remaining_time}{self.dictlanguage[self.current_language]['update_routine'][2]}"
                self.remaining_time -= 1
            else:
                self.is_resting = False
                self.current_repetition += 1
                if self.current_repetition > exercise["repetitions"]:
                    self.current_exercise_index += 1
                    self.current_repetition = 1
                self.afficher_exercice()
        else:
            if exercise["duration"]:
                if self.remaining_time > 0:
                    self.timer_label.text = f"{exercise['name']}\n{self.dictlanguage[self.current_language]['update_routine'][3]} {self.current_repetition}/{exercise['repetitions']} - {self.remaining_time}{self.dictlanguage[self.current_language]['update_routine'][2]}"
                    self.remaining_time -= 1
                else:
                    # Vérifier si c'est la dernière répétition du dernier exercice
                    dernier_exercice = self.current_exercise_index == len(self.routine["fonctions"]) - 1
                    derniere_repetition = self.current_repetition == exercise["repetitions"]

                    if not dernier_exercice or not derniere_repetition:
                        self.is_resting = True
                        self.remaining_time = exercise["rest"]
                    else:
                        # Fin de la routine
                        self.timer_label.text = self.dictlanguage[self.current_language]["update_routine"][0]
                        Clock.unschedule(self.update_routine)
            else:
                self.timer_label.text = f"{exercise['name']} - {self.dictlanguage[self.current_language]['update_routine'][3]} {self.current_repetition}/{exercise['repetitions']} - {exercise['units']} {self.dictlanguage[self.current_language]['update_routine'][4]}"
                self.fait_btn.disabled = False

    def page_modifier_routine(self, nom):
        routine = self.routines[nom]
        layout = FocusableForm(orientation="vertical", spacing=5, padding=[10, 10, 10, 10])

        scroll = ScrollView(size_hint=(1, 0.85))
        content = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        # Espacement au-dessus du titre pour descendre tout le formulaire
        content.add_widget(Widget(size_hint=(1, None), height=20))

        # Titre
        content.add_widget(AutoResizeLabel(
            text=f"{self.dictlanguage[self.current_language]['change_routine'][0]} {routine['name']}",
            font_size=22,
            size_hint=(1, None),
            height=40,
            halign="center",  # Centrer le texte horizontalement
            ))

        def add_field(label_text,length=20):
            content.add_widget(Label(text=label_text, size_hint=(1, None), height=25))
            input_widget = MyTextInput(size_hint=(1, None), max_length=length,height=40)
            content.add_widget(input_widget)
            layout.register_focusable(input_widget)
            return input_widget
        
        content.add_widget(Widget(size_hint=(1, None), height=10))

        exercice_name_input = add_field(self.dictlanguage[self.current_language]["change_routine"][1])

        # === Champ "Valeur" (Durée ou Unités) en 2e position ===
        content.add_widget(Label(text=self.dictlanguage[self.current_language]["change_routine"][8], size_hint=(1, None), height=25))
        exercice_valeur_input = MyTextInput(size_hint=(1, None),max_length=5, height=40)
        content.add_widget(exercice_valeur_input)
        layout.register_focusable(exercice_valeur_input)

        selected_type = {"value": "duration"}

        def update_type(new_type):
            selected_type["value"] = new_type
            duree_btn.selected = (new_type == "duration")
            unite_btn.selected = (new_type == "unit")
            duree_btn.update_opacity()
            unite_btn.update_opacity()


        type_btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        duree_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][2],
            size_hint=(0.5, None),
            height=40
        )
        unite_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][5],
            size_hint=(0.5, None),
            height=40
        )

        update_type("duration")

        duree_btn.bind(on_press=lambda btn: update_type("duration"))
        unite_btn.bind(on_press=lambda btn: update_type("unit"))

        type_btn_layout.add_widget(duree_btn)
        type_btn_layout.add_widget(unite_btn)

        content.add_widget(type_btn_layout)
        layout.register_focusable(duree_btn)
        layout.register_focusable(unite_btn)

        exercice_reps_input = add_field(self.dictlanguage[self.current_language]["change_routine"][3],4)
        exercice_repos_input = add_field(self.dictlanguage[self.current_language]["change_routine"][4],4)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        ajouter_btn = StyledButton(text=self.dictlanguage[self.current_language]["change_routine"][6], size_hint=(0.5, None), height=50)

        ajouter_btn.bind(on_press=lambda *args: self.ajouter_exercice(
            nom,
            exercice_name_input.text,
            exercice_valeur_input.text if selected_type["value"] == "duration" else "",
            exercice_reps_input.text,
            exercice_repos_input.text,
            exercice_valeur_input.text if selected_type["value"] == "unit" else ""
        ))

        layout.register_focusable(ajouter_btn)

        retour_btn = StyledButton(text=self.dictlanguage[self.current_language]["change_routine"][7], size_hint=(0.5, None), height=50)
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))
        layout.register_focusable(retour_btn)

        btn_layout.add_widget(ajouter_btn)
        btn_layout.add_widget(retour_btn)
        layout.add_widget(btn_layout)

        return layout

    def ajouter_exercice(self, routine_nom, ex_nom, duree, repetitions, repos, unites):
        errors = []

        # Vérifie si le nom est vide
        if not ex_nom.strip():
            errors.append(self.dictlanguage[self.current_language]["change_routine"][9])  # Nom vide

        # Vérifie durée et unités : au moins un des deux doit être présent et valide
        duree_val = None
        unites_val = None
        duree_ok = False
        unites_ok = False

        # Vérification de la durée
        if duree:
            try:
                duree_val = int(duree)
                if duree_val > 0:
                    duree_ok = True
                else:
                    errors.append(self.dictlanguage[self.current_language]["change_routine"][10])  # Durée ≤ 0
            except (ValueError, TypeError):
                errors.append(self.dictlanguage[self.current_language]["change_routine"][14])  # Durée invalide (texte, etc.)

        # Vérification des unités
        if unites:
            try:
                unites_val = int(unites)
                unites_ok = True
            except (ValueError, TypeError):
                errors.append(self.dictlanguage[self.current_language]["change_routine"][13])  # Unités invalides

        if not duree and not unites:
            errors.append(self.dictlanguage[self.current_language]["change_routine"][17])  # "Aucune durée/unités spécifiée"

        # Vérification des répétitions
        try:
            repetitions_val = int(repetitions)
            if repetitions_val <= 0:
                errors.append(self.dictlanguage[self.current_language]["change_routine"][11])
        except (ValueError, TypeError):
            errors.append(self.dictlanguage[self.current_language]["change_routine"][15])  # Répétitions invalides

        # Vérification du repos
        try:
            repos_val = int(repos)
            if repos_val < 0:
                errors.append(self.dictlanguage[self.current_language]["change_routine"][12])
        except (ValueError, TypeError):
            errors.append(self.dictlanguage[self.current_language]["change_routine"][16])  # Repos invalide

        # Si aucune erreur, on ajoute l'exercice
        if not errors:
            exercice = {
                "name": ex_nom.strip(),
                "duration": duree_val if duree_ok else 0,
                "repetitions": repetitions_val,
                "rest": repos_val,
                "units": unites_val if unites_ok else None
            }
            self.routines[routine_nom]["fonctions"].append(exercice)
            self.sauvegarder_routines()
            self.set_root_content(self.page_routine(routine_nom))
        else:
            if len(errors) >= 3:
                error_message = self.dictlanguage[self.current_language]["change_routine"][18]
            else:
                error_message = "\n".join(errors)
            self.show_error_popup(error_message, routine_nom)

    def enregistrer_modification_exercice(self, routine_nom, index, ex_nom, duree, repetitions, repos, unites):
        errors = []

        if not ex_nom.strip():
            errors.append(self.dictlanguage[self.current_language]["change_routine"][9])  # Nom vide

        duree_val = None
        unites_val = None
        duree_ok = False
        unites_ok = False

        if duree:
            try:
                duree_val = int(duree)
                if duree_val > 0:
                    duree_ok = True
                else:
                    errors.append(self.dictlanguage[self.current_language]["change_routine"][10])  # Durée ≤ 0
            except (ValueError, TypeError):
                errors.append(self.dictlanguage[self.current_language]["change_routine"][14])  # Durée invalide

        if unites:
            try:
                unites_val = int(unites)
                unites_ok = True
            except (ValueError, TypeError):
                errors.append(self.dictlanguage[self.current_language]["change_routine"][13])  # Unités invalides

        if not duree and not unites:
            errors.append(self.dictlanguage[self.current_language]["change_routine"][17])  # Aucune durée/unité

        try:
            repetitions_val = int(repetitions)
            if repetitions_val <= 0:
                errors.append(self.dictlanguage[self.current_language]["change_routine"][11])  # Répétitions ≤ 0
        except (ValueError, TypeError):
            errors.append(self.dictlanguage[self.current_language]["change_routine"][15])  # Répétitions invalides

        try:
            repos_val = int(repos)
            if repos_val < 0:
                errors.append(self.dictlanguage[self.current_language]["change_routine"][12])  # Repos négatif
        except (ValueError, TypeError):
            errors.append(self.dictlanguage[self.current_language]["change_routine"][16])  # Repos invalide

        if not errors:
            exercice = {
                "name": ex_nom.strip(),
                "duration": duree_val if duree_ok else 0,
                "repetitions": repetitions_val,
                "rest": repos_val,
                "units": unites_val if unites_ok else None
            }
            self.routines[routine_nom]["fonctions"][index] = exercice
            self.sauvegarder_routines()
            self.set_root_content(self.page_routine(routine_nom))
        else:
            if len(errors) >= 3:
                error_message = self.dictlanguage[self.current_language]["change_routine"][18]
            else:
                error_message = "\n".join(errors)
            self.show_error_popup(error_message, routine_nom)


    def show_error_popup(self, error_message, routine_nom):
        """Affiche un message d'erreur sous forme de popup avec un bouton 'Retour'."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Label centré verticalement et horizontalement
        label_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 1))
        label = AutoResizeLabel(
            text=error_message,
            font_size=20,
            halign='center',
            valign='middle'
        )
        # Important : force le label à recalculer le placement de son texte
        label.bind(size=lambda *x: label.setter('text_size')(label, label.size))

        label_container.add_widget(label)
        content.add_widget(label_container)

        # Bouton retour
        retour_btn = StyledButton(
            text=self.dictlanguage[self.current_language]["change_routine"][7],  # "Retour"
            size_hint=(1, None),
            height=50
        )

        popup = Popup(
            title="Erreur",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        retour_btn.bind(on_press=lambda *args: popup.dismiss())
        content.add_widget(retour_btn)

        popup.open()


    def charger_routines(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as f:
                return json.load(f)
        return {"first_time": True, "language":"English", "routines": {}}

    def sauvegarder_routines(self):
        self.routines_data["routines"] = self.routines
        with open(self.FILE_PATH, 'w') as f:
            json.dump(self.routines_data, f, indent=4)


    def afficher_exercice(self):
        if self.current_exercise_index >= len(self.routine["fonctions"]):
            self.timer_label.text = self.dictlanguage[self.current_language]["update_routine"][0]
            Clock.unschedule(self.update_routine)
            return

        exercise = self.routine["fonctions"][self.current_exercise_index]
        self.fait_btn.disabled = True

        if exercise["duration"]:
            self.remaining_time = exercise["duration"]
        else:
            self.timer_label.text = f"{exercise['name']} - {self.dictlanguage[self.current_language]['update_routine'][3]} {self.current_repetition}/{exercise['repetitions']} - {exercise['units']} {self.dictlanguage[self.current_language]['update_routine'][4]}"
            self.fait_btn.disabled = False
    
    def marquer_fait(self, instance):
        self.fait_btn.disabled = True
        if self.current_exercise_index < len(self.routine["fonctions"]) - 1:  # Évite le dernier repos
            self.is_resting = True
            self.remaining_time = self.routine["fonctions"][self.current_exercise_index]["rest"]
        else :
            if self.current_repetition < self.routine["fonctions"][self.current_exercise_index]["repetitions"]:
                self.is_resting = True
                self.remaining_time = self.routine["fonctions"][self.current_exercise_index]["rest"]
            else:
                self.timer_label.text = self.dictlanguage[self.current_language]["update_routine"][0]
                Clock.unschedule(self.update_routine)

# Lancement de l'application    
if __name__ == "__main__":
    RoutineApp().run()