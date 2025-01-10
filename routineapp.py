from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


class RoutineApp(App):
    def build(self):
        self.routines = {}
        return self.root

    def on_start(self):
        # Initialise les routines et met à jour la liste des routines dans le fichier .kv
        self.update_routine_list()

    def set_root_content(self, new_content):
        """Remplace le contenu principal par un nouveau widget."""
        self.root.clear_widgets()
        self.root.add_widget(new_content)

    def page_ajouter_routine(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        layout.add_widget(Label(text="Nom de la routine :"))
        routine_name_input = TextInput(size_hint=(1, 0.2))
        layout.add_widget(routine_name_input)

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
        self.update_routine_list()

    def update_routine_list(self):
        routine_list = self.root.ids.routine_list
        routine_list.clear_widgets()

        for nom in self.routines:
            btn = Button(text=nom, size_hint=(1, None), height=40)
            btn.bind(on_press=lambda instance, r=nom: self.set_root_content(self.page_routine(r)))
            routine_list.add_widget(btn)

    def page_routine(self, nom):
        # Implémente la logique de la page routine
        pass


# Lancement de l'application
if __name__ == "__main__":
    RoutineApp().run()
