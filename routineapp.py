from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock


class RoutineApp(App):
    def build(self):
        self.routines = {}
        self.root = BoxLayout()
        self.set_root_content(self.page_bienvenue())
        return self.root

    def set_root_content(self, new_content):
        self.root.clear_widgets()
        self.root.add_widget(new_content)

    def page_bienvenue(self):
        layout = BoxLayout(orientation="vertical", padding=10)
        label = Label(text="Bienvenue dans cette application de routine personnalisée",
                      font_size=24, halign="center", valign="middle")
        label.bind(size=label.setter('text_size'))
        layout.add_widget(label)
        layout.bind(on_touch_down=lambda *args: self.set_root_content(self.page_accueil()))
        return layout

    def page_accueil(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        add_btn = Button(text="Ajouter une routine", size_hint=(1, 0.1))
        add_btn.bind(on_press=lambda *args: self.set_root_content(self.page_ajouter_routine()))
        layout.add_widget(add_btn)

        scroll = ScrollView(size_hint=(1, 0.8))
        routine_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        routine_layout.bind(minimum_height=routine_layout.setter("height"))
        for nom in self.routines:
            routine_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
            btn = Button(text=nom, size_hint=(0.7, 1))
            btn.bind(on_press=lambda instance, r=nom: self.set_root_content(self.page_routine(r)))
            routine_box.add_widget(btn)

            delete_btn = Button(text="Supprimer", size_hint=(0.3, 1))
            delete_btn.bind(on_press=lambda instance, r=nom: self.confirmer_suppression_routine(r))
            routine_box.add_widget(delete_btn)

            routine_layout.add_widget(routine_box)
        scroll.add_widget(routine_layout)
        layout.add_widget(scroll)

        return layout

    def confirmer_suppression_routine(self, nom):
        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        popup_layout.add_widget(Label(text=f"Voulez-vous vraiment supprimer la routine '{nom}' ?"))
        btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        oui_btn = Button(text="Oui")
        oui_btn.bind(on_press=lambda *args: self.supprimer_routine(nom))
        non_btn = Button(text="Non")
        non_btn.bind(on_press=lambda *args: popup.dismiss())

        btn_layout.add_widget(oui_btn)
        btn_layout.add_widget(non_btn)
        popup_layout.add_widget(btn_layout)

        popup = Popup(title="Confirmation", content=popup_layout, size_hint=(0.8, 0.4))
        popup.open()

    def supprimer_routine(self, nom):
        del self.routines[nom]
        self.set_root_content(self.page_accueil())

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
        self.set_root_content(self.page_accueil())

    def page_routine(self, nom):
        routine = self.routines[nom]
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        layout.add_widget(Label(text=f"Routine : {routine['nom']}", font_size=20))
        scroll = ScrollView(size_hint=(1, 0.6))
        exercice_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        exercice_layout.bind(minimum_height=exercice_layout.setter("height"))
        for index, ex in enumerate(routine["exercices"]):
            ex_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
            ex_layout.add_widget(Label(text=str(ex), size_hint=(0.8, 1)))
            remove_btn = Button(text="Supprimer", size_hint=(0.2, 1))
            remove_btn.bind(on_press=lambda instance, i=index: self.supprimer_exercice(nom, i))
            ex_layout.add_widget(remove_btn)
            exercice_layout.add_widget(ex_layout)
        scroll.add_widget(exercice_layout)
        layout.add_widget(scroll)

        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        lancer_btn = Button(text="Lancer", size_hint=(0.4, None), height=50)
        lancer_btn.bind(on_press=lambda *args: self.lancer_routine(nom))
        modifier_btn = Button(text="Modifier", size_hint=(0.4, None), height=50)
        modifier_btn.bind(on_press=lambda *args: self.set_root_content(self.page_modifier_routine(nom)))
        retour_btn = Button(text="Retour", size_hint=(0.4, None), height=50)
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_accueil()))
        btn_layout.add_widget(lancer_btn)
        btn_layout.add_widget(modifier_btn)
        btn_layout.add_widget(retour_btn)
        layout.add_widget(btn_layout)

        return layout

    def supprimer_exercice(self, routine_nom, index):
        del self.routines[routine_nom]["exercices"][index]
        self.set_root_content(self.page_routine(routine_nom))


    def lancer_routine(self, nom):
        routine = self.routines[nom]
        self.current_exercise_index = 0
        self.current_repetition = 1
        self.remaining_time = 0
        self.is_resting = False

        self.routine_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.timer_label = Label(text="Préparation...", font_size=24)
        self.routine_layout.add_widget(self.timer_label)

        stop_btn = Button(text="Arrêter", size_hint=(1, 0.2))
        stop_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))
        self.routine_layout.add_widget(stop_btn)

        self.set_root_content(self.routine_layout)
        Clock.schedule_interval(lambda dt: self.update_routine(routine), 1)
    
    def update_routine(self, routine):
        # Si tous les exercices sont terminés
        if self.current_exercise_index >= len(routine["exercices"]):
            self.timer_label.text = "Routine terminée !"
            Clock.unschedule(self.update_routine)
            return

        # Récupération de l'exercice en cours
        exercise = routine["exercices"][self.current_exercise_index]

        # Gestion de l'état de repos
        if self.is_resting:
            if self.remaining_time > 0:
                self.timer_label.text = f"Repos : {self.remaining_time}s"
                self.remaining_time -= 1
            else:
                # Fin du repos, passage à la répétition suivante
                self.is_resting = False
                self.current_repetition += 1
                if self.current_repetition > exercise["repetitions"]:
                    # Si toutes les répétitions sont terminées, passer à l'exercice suivant
                    self.current_exercise_index += 1
                    self.current_repetition = 1
                self.remaining_time = exercise["duree"]  # Initialiser le temps de l'exercice
        else:
            # Gestion de l'exercice
            if self.remaining_time > 0:
                self.timer_label.text = f"{exercise['nom']} - Répétition {self.current_repetition}/{exercise['repetitions']} - Temps restant : {self.remaining_time}s"
                self.remaining_time -= 1
            else:
                # Fin de l'exercice, passage au repos
                self.is_resting = True
                self.remaining_time = exercise["repos"]  # Initialiser le temps de repos
                if self.remaining_time == 0:
                    # Si aucun temps de repos, passer immédiatement à la répétition suivante
                    self.is_resting = False
                    self.current_repetition += 1
                    if self.current_repetition > exercise["repetitions"]:
                        self.current_exercise_index += 1
                        self.current_repetition = 1
                    self.remaining_time = exercise["duree"]


    def page_modifier_routine(self, nom):
        routine = self.routines[nom]
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        layout.add_widget(Label(text=f"Modifier la routine : {routine['nom']}", font_size=20))

        layout.add_widget(Label(text="Nom de l'exercice :"))
        exercice_name_input = TextInput(size_hint=(1, 0.5))
        layout.add_widget(exercice_name_input)

        layout.add_widget(Label(text="Durée (secondes) :"))
        exercice_duree_input = TextInput(size_hint=(1, 0.5))
        layout.add_widget(exercice_duree_input)

        layout.add_widget(Label(text="Répétitions :"))
        exercice_reps_input = TextInput(size_hint=(1, 0.5))
        layout.add_widget(exercice_reps_input)

        layout.add_widget(Label(text="Repos (secondes) :"))
        exercice_repos_input = TextInput(size_hint=(1, 0.5))
        layout.add_widget(exercice_repos_input)

        layout.add_widget(Label(text="Unités :"))
        exercice_unites_input = TextInput(size_hint=(1, 0.5))
        layout.add_widget(exercice_unites_input)

        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        ajouter_btn = Button(text="Ajouter exercice")
        ajouter_btn.bind(on_press=lambda *args: self.ajouter_exercice(
            nom,
            exercice_name_input.text,
            exercice_duree_input.text,
            exercice_reps_input.text,
            exercice_repos_input.text,
            exercice_unites_input.text
        ))
        retour_btn = Button(text="Retour")
        retour_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))
        btn_layout.add_widget(ajouter_btn)
        btn_layout.add_widget(retour_btn)

        layout.add_widget(btn_layout)
        return layout

    def ajouter_exercice(self, routine_nom, ex_nom, duree, repetitions, repos, unites):
        if ex_nom.strip():
            exercice = {
                "nom": ex_nom.strip(),
                "duree": int(duree) if duree else 0,
                "repetitions": int(repetitions) if repetitions else 1,
                "repos": int(repos) if repos else 0,
                "unites": int(unites) if unites else None
            }
            self.routines[routine_nom]["exercices"].append(exercice)
        self.set_root_content(self.page_routine(routine_nom))


# Lancement de l'application
if __name__ == "__main__":
    RoutineApp().run()
