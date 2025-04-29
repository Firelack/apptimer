import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class RoutineApp(App):
    FILE_PATH = "routines.json"  # Définition du chemin du fichier JSON

    def build(self):
        self.routines = self.charger_routines()  # Charger les routines depuis le fichier
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

        routines_list = list(self.routines.items())  # Convertir en liste ordonnée
        for index, (nom, _) in enumerate(routines_list):
            routine_box = BoxLayout(size_hint_y=None, height=50, spacing=10)

            btn = Button(text=nom, size_hint=(0.7, 1))
            btn.bind(on_press=lambda instance, r=nom: self.set_root_content(self.page_routine(r)))
            routine_box.add_widget(btn)

            up_btn = Button(text="up", size_hint=(0.1, 1))
            up_btn.bind(on_press=lambda instance, i=index: self.deplacer_routine(i, -1))
            routine_box.add_widget(up_btn)

            down_btn = Button(text="dn", size_hint=(0.1, 1))
            down_btn.bind(on_press=lambda instance, i=index: self.deplacer_routine(i, 1))
            routine_box.add_widget(down_btn)

            delete_btn = Button(text="X", size_hint=(0.1, 1))
            delete_btn.bind(on_press=lambda instance, r=nom: self.confirmer_suppression_routine(r))
            routine_box.add_widget(delete_btn)

            routine_layout.add_widget(routine_box)

        scroll.add_widget(routine_layout)
        layout.add_widget(scroll)

        return layout

    def deplacer_routine(self, index, direction):
        routines_list = list(self.routines.items())  # Convertir en liste ordonnée
        new_index = index + direction

        if 0 <= new_index < len(routines_list):
            routines_list[index], routines_list[new_index] = routines_list[new_index], routines_list[index]

            # Reconvertir en dictionnaire (tout en gardant l'ordre)
            self.routines = {nom: data for nom, data in routines_list}

            self.sauvegarder_routines()
            self.set_root_content(self.page_accueil())  # Rafraîchir l'affichage

    def confirmer_suppression_routine(self, nom):
        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        popup_layout.add_widget(Label(text=f"Voulez-vous vraiment supprimer la routine '{nom}' ?"))
        btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        popup = Popup(title="Confirmation", content=popup_layout, size_hint=(0.8, 0.4))

        oui_btn = Button(text="Oui")
        oui_btn.bind(on_press=lambda *args: self.supprimer_routine(nom, popup))
        non_btn = Button(text="Non")
        non_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(oui_btn)
        btn_layout.add_widget(non_btn)
        popup_layout.add_widget(btn_layout)

        popup.open()

    def supprimer_routine(self, nom, popup):
        if nom in self.routines:
            del self.routines[nom]
            self.sauvegarder_routines()  # Sauvegarde après suppression
        popup.dismiss()  # Ferme la fenêtre de confirmation
        self.set_root_content(self.page_accueil())  # Rafraîchit l'affichage

    def page_ajouter_routine(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        
        # Label avec texte agrandi
        label = Label(text="Nom de la routine :", font_size=30)
        layout.add_widget(label)
        
        # Champ de saisie avec hauteur réduite
        routine_name_input = TextInput(size_hint=(1, 0.1))  # Hauteur réduite à 0.1
        layout.add_widget(routine_name_input)

        # Layout pour les boutons
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
            self.routines[nom] = {"nom": nom, "fonctions": []}
            self.sauvegarder_routines()  # Sauvegarder les modifications après ajout
        self.set_root_content(self.page_accueil())

    def page_routine(self, nom):
        routine = self.routines[nom]
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        layout.add_widget(Label(text=f"Routine : {routine['nom']}", font_size=20))
        scroll = ScrollView(size_hint=(1, 0.6))
        exercice_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        exercice_layout.bind(minimum_height=exercice_layout.setter("height"))
        for index, ex in enumerate(routine["fonctions"]):
            ex_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
            if ex["duree"]:
                ex_layout.add_widget(Label(text=f"{ex['nom']} - {ex['repetitions']} rep, {ex['duree']}s", size_hint=(0.5, 1)))
            else:
                ex_layout.add_widget(Label(text=f"{ex['nom']} - {ex['repetitions']} rep, {ex['unites']} unités", size_hint=(0.5, 1)))

            up_btn = Button(text="up", size_hint=(0.1, 1))
            up_btn.bind(on_press=lambda instance, i=index: self.deplacer_exercice(nom, i, -1))
            ex_layout.add_widget(up_btn)

            down_btn = Button(text="dn", size_hint=(0.1, 1))
            down_btn.bind(on_press=lambda instance, i=index: self.deplacer_exercice(nom, i, 1))
            ex_layout.add_widget(down_btn)

            remove_btn = Button(text="X", size_hint=(0.1, 1))
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
    
    def deplacer_exercice(self, routine_nom, index, direction):
        if 0 <= index + direction < len(self.routines[routine_nom]["fonctions"]):
            self.routines[routine_nom]["fonctions"].insert(index + direction, 
                self.routines[routine_nom]["fonctions"].pop(index))
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
        self.remaining_time = self.routines[nom]["fonctions"][0]["duree"] if self.routines[nom]["fonctions"][0]["duree"] else 0

        self.routine_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.timer_label = Label(text="Préparation...", font_size=24)
        self.routine_layout.add_widget(self.timer_label)
        
        self.fait_btn = Button(text="Fait", size_hint=(1, 0.2))
        self.fait_btn.bind(on_press=self.marquer_fait)
        self.fait_btn.disabled = True
        self.routine_layout.add_widget(self.fait_btn)

        self.pause_btn = Button(text="Pause", size_hint=(1, 0.2))
        self.pause_btn.bind(on_press=self.toggle_pause)
        self.routine_layout.add_widget(self.pause_btn)

        # Nouveau bouton pour passer le temps de repos
        self.skip_rest_btn = Button(text="Passer le repos", size_hint=(1, 0.2))
        self.skip_rest_btn.bind(on_press=self.pass_rest_time)
        self.skip_rest_btn.disabled = True  # Ce bouton est désactivé tant qu'on n'est pas en période de repos
        self.routine_layout.add_widget(self.skip_rest_btn)
        
        stop_btn = Button(text="Retour", size_hint=(1, 0.2))
        stop_btn.bind(on_press=lambda *args: self.set_root_content(self.page_routine(nom)))
        self.routine_layout.add_widget(stop_btn)

        self.set_root_content(self.routine_layout)
        Clock.schedule_interval(self.update_routine, 1.0)

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

    def toggle_pause(self, instance):
        self.paused = not self.paused
        instance.text = "Relancer" if self.paused else "Pause"

    def update_routine(self, dt):
        if self.paused:
            return
        if self.current_exercise_index >= len(self.routine["fonctions"]):
            self.timer_label.text = "Routine terminée !"
            Clock.unschedule(self.update_routine)
            return

        exercise = self.routine["fonctions"][self.current_exercise_index]

        if self.is_resting:
            self.skip_rest_btn.disabled = False  # Activer le bouton pour passer le temps de repos
            self.fait_btn.disabled = True  # Désactiver le bouton "Fait" pendant le repos
            if self.remaining_time > 0:
                self.timer_label.text = f"Repos : {self.remaining_time}s"
                self.remaining_time -= 1
            else:
                self.is_resting = False
                self.current_repetition += 1
                if self.current_repetition > exercise["repetitions"]:
                    self.current_exercise_index += 1
                    self.current_repetition = 1
                self.afficher_exercice()
        else:
            if exercise["duree"]:
                if self.remaining_time > 0:
                    self.timer_label.text = f"{exercise['nom']} - Répétition {self.current_repetition}/{exercise['repetitions']} - {self.remaining_time}s"
                    self.remaining_time -= 1
                else:
                    # Vérifier si c'est la dernière répétition du dernier exercice
                    dernier_exercice = self.current_exercise_index == len(self.routine["fonctions"]) - 1
                    derniere_repetition = self.current_repetition == exercise["repetitions"]

                    if not dernier_exercice or not derniere_repetition:
                        self.is_resting = True
                        self.remaining_time = exercise["repos"]
                    else:
                        # Fin de la routine
                        self.timer_label.text = "Routine terminée !"
                        Clock.unschedule(self.update_routine)
            else:
                self.timer_label.text = f"{exercise['nom']} - Répétition {self.current_repetition}/{exercise['repetitions']} - {exercise['unites']} unités"
                self.fait_btn.disabled = False


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

        layout.add_widget(Label(text="Unités : (si pas de durée)"))
        exercice_unites_input = TextInput(size_hint=(1, 0.5))
        layout.add_widget(exercice_unites_input)

        btn_layout = BoxLayout(size_hint=(1, 0.5), spacing=10)
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
            self.routines[routine_nom]["fonctions"].append(exercice)
            self.sauvegarder_routines()  # Sauvegarder après ajout d'un exercice
        self.set_root_content(self.page_routine(routine_nom))

    def charger_routines(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as f:
                return json.load(f)
        return {}

    def sauvegarder_routines(self):
        with open(self.FILE_PATH, 'w') as f:
            json.dump(self.routines, f, indent=4)

    def afficher_exercice(self):
        if self.current_exercise_index >= len(self.routine["fonctions"]):
            self.timer_label.text = "Routine terminée !"
            Clock.unschedule(self.update_routine)
            return

        exercise = self.routine["fonctions"][self.current_exercise_index]
        self.fait_btn.disabled = True

        if exercise["duree"]:
            self.remaining_time = exercise["duree"]
        else:
            self.timer_label.text = f"{exercise['nom']} - Répétition {self.current_repetition}/{exercise['repetitions']} - {exercise['unites']} unités"
            self.fait_btn.disabled = False
    
    def marquer_fait(self, instance):
        self.fait_btn.disabled = True
        if self.current_exercise_index < len(self.routine["fonctions"]) - 1:  # Évite le dernier repos
            self.is_resting = True
            self.remaining_time = self.routine["fonctions"][self.current_exercise_index]["repos"]
        else :
            if self.current_repetition < self.routine["fonctions"][self.current_exercise_index]["repetitions"]:
                self.is_resting = True
                self.remaining_time = self.routine["fonctions"][self.current_exercise_index]["repos"]
            else:
                self.timer_label.text = "Routine terminée !"
                Clock.unschedule(self.update_routine)

# Lancement de l'application
if __name__ == "__main__":
    RoutineApp().run()