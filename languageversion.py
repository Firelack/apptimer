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
        self.widgets_list.append(widget)

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 9:  # TAB
            focused = next((i for i, w in enumerate(self.widgets_list) if hasattr(w, "focus") and w.focus), None)
            if focused is not None:
                self.widgets_list[focused].focus = False
                if 'shift' in modifiers:
                    next_index = (focused - 1) % len(self.widgets_list)
                else:
                    next_index = (focused + 1) % len(self.widgets_list)
                self.widgets_list[next_index].focus = True
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
        self.selected = False  # <-- NOUVEAU

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
    FILE_PATH = "routinesV3.json"  # Définition du chemin du fichier JSON
    dictlanguage = {
        "English": 
        {"welcome_page" : "Welcome to this personalized routine application",
         "home_page":"Add a routine",
         "confirmation" : ["Confirmation",
                           "Do you really want to delete the routine ",
                           "Yes","No"],
        "add_routine" : ["Routine name :",
                         "Finish",
                        "Cancel"],
        "routine_page" : ["Routine :","rep","s","units","Start","Add","Back"],
        "start_routine" : ["Preparing...","Done","Pause","Skip rest","Back"],
        "toggle_pause" : ["Resume","Pause"],
        "update_routine" : ["Routine completed !","Rest :","s","Repetition "," units"],
        "change_routine" : ["Add an exercise :","Exercise name :","Duration (seconds) :","Repetitions :",
                            "Rest (seconds) :","Units : (if no duration)", "Add the exercise","Back","Duration/units :"]
                           }, 
        "French": 
        {"welcome_page" : "Bienvenue dans cette application de routine personnalisée",
         "home_page":"Ajouter une routine",
         "confirmation" : ["Confirmation",
                           "Voulez-vous vraiment supprimer la routine ",
                           "Oui","Non"],
        "add_routine" : ["Nom de la routine :",
                         "Terminer",
                         "Annuler"],
        "routine_page" : ["Routine :","rep","s","unités","Lancer","Ajouter","Retour"],
        "start_routine" : ["Préparation...","Fait","Pause","Passer le repos","Retour"],
        "toggle_pause" : ["Relancer","Pause"],
        "update_routine" : ["Routine terminée !","Repos :","s","Répétition "," unités"],
        "change_routine" : ["Ajouter un exercice :","Nom de l'exercice :","Durée (secondes) :","Répétitions :",
                            "Repos (secondes) :","Unités : (si pas de durée)", "Ajouter l'exercice","Retour","Durée/unités :"]
                                                              }
         }#self.dictlanguage[self.current_language]["update_routine"]

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
        content = BoxLayout(orientation="vertical", spacing=10, padding=10, size_hint=(1, 1))

        # --- MENU LANGUE ---
        top_buttons = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=10)

        # Bouton principal qui ouvre le menu déroulant
        main_lang_btn = StyledButton(text=self.routines_data["language"], size_hint=(0.1, 1))
        dropdown = DropDown()

        for lang in ["English", "French"]:
            btn = StyledButton(text=lang, size_hint_y=None, height=44, opacity=1)
            def on_lang_select(btn_instance, dropdown=dropdown):
                selected_lang = btn_instance.text
                self.routines_data["language"] = selected_lang
                self.current_language = selected_lang
                self.sauvegarder_routines()
                main_lang_btn.text = selected_lang
                dropdown.dismiss()
                Clock.schedule_once(lambda dt: self.set_root_content(self.page_accueil()), 0.1)
            btn.bind(on_release=on_lang_select)
            dropdown.add_widget(btn)

        main_lang_btn.bind(on_release=lambda btn: Clock.schedule_once(lambda dt: dropdown.open(btn), 0.01))
        top_buttons.add_widget(main_lang_btn)

        # --- BOUTON "Ajouter une routine" ---
        btn2 = StyledButton(text=self.dictlanguage[self.current_language]["home_page"], size_hint=(0.9, 1))
        btn2.bind(on_press=lambda *args: self.set_root_content(self.page_ajouter_routine()))
        top_buttons.add_widget(btn2)

        content.add_widget(top_buttons)

        # --- Scroll des routines ---
        scroll = ScrollView(size_hint=(1, 0.8))
        routine_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        routine_layout.bind(minimum_height=routine_layout.setter("height"))

        routines_list = list(self.routines.items())
        for index, (nom, _) in enumerate(routines_list):
            routine_box = BoxLayout(size_hint_y=None, height=50, spacing=10)

            btn = StyledButton(text=nom, size_hint=(0.7, 1))
            btn.bind(on_press=lambda instance, r=nom: self.set_root_content(self.page_routine(r)))
            routine_box.add_widget(btn)

            up_btn = StyledButton(text="up", size_hint=(0.1, 1))
            up_btn.bind(on_press=lambda instance, i=index: self.deplacer_routine(i, -1))
            routine_box.add_widget(up_btn)

            down_btn = StyledButton(text="dn", size_hint=(0.1, 1))
            down_btn.bind(on_press=lambda instance, i=index: self.deplacer_routine(i, 1))
            routine_box.add_widget(down_btn)

            delete_btn = StyledButton(text="X", size_hint=(0.1, 1))
            delete_btn.bind(on_press=lambda instance, r=nom: self.confirmer_suppression_routine(r))
            routine_box.add_widget(delete_btn)

            routine_layout.add_widget(routine_box)

        scroll.add_widget(routine_layout)
        content.add_widget(scroll)

        layout.add_widget(content)
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
        popup_layout.add_widget(Label(text=f"{self.dictlanguage[self.current_language]['confirmation'][1]} {nom} ?"))
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
        routine_name_input = MyTextInput(size_hint=(1, None), max_length=30,height=40)
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
        layout = BoxLayout(orientation="vertical", spacing=5, padding=[10, 10, 10, 10])

        # Titre en haut
        title_label = Label(
            text=f"{self.dictlanguage[self.current_language]['routine_page'][0]} {routine['name']}",
            font_size=22,
            size_hint=(1, None),
            height=40
        )
        layout.add_widget(title_label)

        # Petit espace sous le titre
        layout.add_widget(Widget(size_hint=(1, None), height=10))

        # ScrollView contenant les exercices
        scroll = ScrollView(size_hint=(1, 0.70))
        exercice_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8)
        exercice_layout.bind(minimum_height=exercice_layout.setter("height"))

        for index, ex in enumerate(routine["fonctions"]):
            ex_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

            if ex["duration"]:
                ex_layout.add_widget(Label(
                    text=f"{ex['name']} - {ex['repetitions']} {self.dictlanguage[self.current_language]['routine_page'][1]}, {ex['duration']}{self.dictlanguage[self.current_language]['routine_page'][2]}",
                    size_hint=(0.5, 1)
                ))
            else:
                ex_layout.add_widget(Label(
                    text=f"{ex['name']} - {ex['repetitions']} {self.dictlanguage[self.current_language]['routine_page'][1]}, {ex['units']} {self.dictlanguage[self.current_language]['routine_page'][3]}",
                    size_hint=(0.5, 1)
                ))

            up_btn = StyledButton(text="up", size_hint=(0.1, 1))
            up_btn.bind(on_press=lambda instance, i=index: self.deplacer_exercice(nom, i, -1))
            ex_layout.add_widget(up_btn)

            down_btn = StyledButton(text="dn", size_hint=(0.1, 1))
            down_btn.bind(on_press=lambda instance, i=index: self.deplacer_exercice(nom, i, 1))
            ex_layout.add_widget(down_btn)

            remove_btn = StyledButton(text="X", size_hint=(0.1, 1))
            remove_btn.bind(on_press=lambda instance, i=index: self.supprimer_exercice(nom, i))
            ex_layout.add_widget(remove_btn)

            exercice_layout.add_widget(ex_layout)

        scroll.add_widget(exercice_layout)
        layout.add_widget(scroll)

        # Boutons bas de page
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        lancer_btn = StyledButton(text=self.dictlanguage[self.current_language]["routine_page"][4], size_hint=(0.4, None), height=50)
        lancer_btn.bind(on_press=lambda *args: self.lancer_routine(nom))
        modifier_btn = StyledButton(text=self.dictlanguage[self.current_language]["routine_page"][5], size_hint=(0.4, None), height=50)
        modifier_btn.bind(on_press=lambda *args: self.set_root_content(self.page_modifier_routine(nom)))
        retour_btn = StyledButton(text=self.dictlanguage[self.current_language]["routine_page"][6], size_hint=(0.4, None), height=50)
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))

        btn_layout.add_widget(lancer_btn)
        btn_layout.add_widget(modifier_btn)
        btn_layout.add_widget(retour_btn)

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

        self.routine_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.timer_label = Label(text=self.dictlanguage[self.current_language]["start_routine"][0], font_size=24)
        self.routine_layout.add_widget(self.timer_label)
        
        self.fait_btn = StyledButton(text=self.dictlanguage[self.current_language]["start_routine"][1], size_hint=(1, 0.2))
        self.fait_btn.bind(on_press=self.marquer_fait)
        self.fait_btn.disabled = True
        self.routine_layout.add_widget(self.fait_btn)

        self.pause_btn = StyledButton(text=self.dictlanguage[self.current_language]["start_routine"][2], size_hint=(1, 0.2))
        self.pause_btn.bind(on_press=self.toggle_pause)
        self.routine_layout.add_widget(self.pause_btn)

        # Nouveau bouton pour passer le temps de repos
        self.skip_rest_btn = StyledButton(text=self.dictlanguage[self.current_language]["start_routine"][3], size_hint=(1, 0.2))
        self.skip_rest_btn.bind(on_press=self.pass_rest_time)
        self.skip_rest_btn.disabled = True  # Ce bouton est désactivé tant qu'on n'est pas en période de repos
        self.routine_layout.add_widget(self.skip_rest_btn)
        
        stop_btn = StyledButton(text=self.dictlanguage[self.current_language]["start_routine"][4], size_hint=(1, 0.2))
        stop_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))
        self.routine_layout.add_widget(stop_btn)

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
                    self.timer_label.text = f"{exercise['name']} - {self.dictlanguage[self.current_language]['update_routine'][3]} {self.current_repetition}/{exercise['repetitions']} - {self.remaining_time}{self.dictlanguage[self.current_language]['update_routine'][2]}"
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

        # Titre
        content.add_widget(Label(
            text=f"{self.dictlanguage[self.current_language]['change_routine'][0]} {routine['name']}",
            font_size=22,
            size_hint=(1, None),
            height=40
        ))

        def add_field(label_text,length=20):
            content.add_widget(Label(text=label_text, size_hint=(1, None), height=25))
            input_widget = MyTextInput(size_hint=(1, None), max_length=length,height=40)
            content.add_widget(input_widget)
            layout.register_focusable(input_widget)
            return input_widget

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
        if ex_nom.strip():
            exercice = {
                "name": ex_nom.strip(),
                "duration": int(duree) if duree else 0,
                "repetitions": int(repetitions) if repetitions else 1,
                "rest": int(repos) if repos else 0,
                "units": int(unites) if unites else None
            }
            self.routines[routine_nom]["fonctions"].append(exercice)
            self.sauvegarder_routines()
        self.set_root_content(self.page_routine(routine_nom))

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