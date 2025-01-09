from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

class RoutineApp(App):
    def build(self):
        # Stocker les routines
        self.routines = {}

        # Page de bienvenue
        return self.page_bienvenue()
    
    def set_root_content(self, new_content):
        """
        Remplace le contenu de la fenêtre principale avec un nouveau widget.
        """
        self.root.clear_widgets()
        self.root.add_widget(new_content)

    def page_bienvenue(self):
        layout = BoxLayout(orientation="vertical", padding=10)
        label = Label(text="Bienvenue dans cette application de routine personnalisée",
                    font_size=24, halign="center", valign="middle")
        label.bind(size=label.setter('text_size'))
        layout.add_widget(label)

        # Remplacer le contenu au clic
        layout.bind(on_touch_down=lambda *args: self.set_root_content(self.page_accueil()))
        return layout

    def page_accueil(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Bouton pour ajouter une routine
        add_btn = Button(text="Ajouter une routine", size_hint=(1, 0.1))
        add_btn.bind(on_press=lambda *args: self.set_root_content(self.page_ajouter_routine()))
        layout.add_widget(add_btn)

        # Liste des routines existantes
        scroll = ScrollView(size_hint=(1, 0.8))
        routine_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        routine_layout.bind(minimum_height=routine_layout.setter("height"))
        for nom in self.routines:
            btn = Button(text=nom, size_hint_y=None, height=40)
            btn.bind(on_press=lambda instance, r=nom: self.set_root_content(self.page_routine(r)))
            routine_layout.add_widget(btn)
        scroll.add_widget(routine_layout)
        layout.add_widget(scroll)

        return layout

    def page_ajouter_routine(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Champ pour le nom de la routine
        layout.add_widget(Label(text="Nom de la routine :"))
        routine_name_input = TextInput(size_hint=(1, 0.1))
        layout.add_widget(routine_name_input)

        # Boutons pour terminer ou annuler
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        terminer_btn = Button(text="Terminer")
        terminer_btn.bind(on_press=lambda *args: self.ajouter_routine(routine_name_input.text))
        annuler_btn = Button(text="Annuler")
        annuler_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))
        btn_layout.add_widget(terminer_btn)
        btn_layout.add_widget(annuler_btn)

        layout.add_widget(btn_layout)
        return layout

    def ajouter_routine(self, nom):
        if nom.strip():
            self.routines[nom] = {"nom": nom, "exercices": []}
        self.set_root_content(self.page_accueil())

    def page_routine(self, nom):
        routine = self.routines[nom]
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Affichage des exercices
        layout.add_widget(Label(text=f"Routine : {routine['nom']}", font_size=20))
        scroll = ScrollView(size_hint=(1, 0.6))
        exercice_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        exercice_layout.bind(minimum_height=exercice_layout.setter("height"))
        for ex in routine["exercices"]:
            exercice_layout.add_widget(Label(text=str(ex), size_hint_y=None, height=30))
        scroll.add_widget(exercice_layout)
        layout.add_widget(scroll)

        # Boutons
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        modifier_btn = Button(text="Modifier")
        lancer_btn = Button(text="Lancer")
        retour_btn = Button(text="Retour")
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))
        btn_layout.add_widget(modifier_btn)
        btn_layout.add_widget(lancer_btn)
        btn_layout.add_widget(retour_btn)
        layout.add_widget(btn_layout)

        return layout

# Lancement de l'application
if __name__ == "__main__":
    RoutineApp().run()
