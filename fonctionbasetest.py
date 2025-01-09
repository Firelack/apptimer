import time
import json
import os

class Fonction:
    def __init__(self, nom, duree=None, repetitions=1, repos=0, unites=None, dureetot=None):
        self.nom = nom
        if duree is not None and duree < 0:
            raise ValueError("La durée doit être positive.")
        if repetitions < 0 or repos < 0:
            raise ValueError("Les répétitions et le repos doivent être positifs.")
        if unites is not None and unites < 0:
            raise ValueError("Le nombre d'unités doit être positif.")
        
        self.duree = duree
        self.repetitions = repetitions
        self.repos = repos
        self.unites = unites
        
        # Calculer dureetot à l'initialisation
        self.dureetot = self.duree * self.repetitions + self.repos * (self.repetitions - 1)
    
    def __str__(self):
        if self.unites is not None:
            return f"{self.nom} : {self.unites} unités, {self.repetitions} répétitions, {self.repos}s de repos"
        else:
            return f"{self.nom} : {self.duree}s, {self.repetitions} répétitions, {self.repos}s de repos"

    def est_base_sur_timer(self):
        """Retourne True si l'exercice est basé sur un timer, False si basé sur des unités."""
        return self.unites is None


class Routine:
    def __init__(self, nom, liste_fonctions=[]):
        self.nom = nom
        self.fonctions = liste_fonctions
    
    def __str__(self):
        return f"{self.nom} :\n" + "\n".join([str(f) for f in self.fonctions])
    
    def ajouter_fonction(self, fonction):
        self.fonctions.append(fonction)
    
    def retirer_fonction(self, fonction):
        self.fonctions.remove(fonction)
    
    def duree_totale(self):
        """
        Calcule la durée totale de la routine.
        - Ignore la durée des exercices basés sur des unités, mais prend en compte le temps de repos.
        """
        total = 0
        for f in self.fonctions:
            total += f.dureetot
        return total

    
    def executer(self):
        """
        Exécute chaque exercice de la routine.
        - Si l'exercice est basé sur un timer, lance un décompte.
        - Si basé sur des unités, attend une confirmation manuelle.
        """
        print(f"Début de la routine : {self.nom}")
        for index, fonction in enumerate(self.fonctions, start=1):
            print(f"\nExercice {index}/{len(self.fonctions)} : {fonction.nom}")
            
            for repetition in range(1, fonction.repetitions + 1):
                if fonction.est_base_sur_timer():
                    print(f"  Répétition {repetition}/{fonction.repetitions} : {fonction.duree} secondes")
                    self._lancer_timer(fonction.duree)
                else:
                    print(f"  Répétition {repetition}/{fonction.repetitions} : {fonction.unites} unités")
                    input("  Appuyez sur Entrée lorsque terminé.")
                
                # Repos entre les répétitions (sauf après la dernière)
                if repetition < fonction.repetitions:
                    print(f"  Temps de repos : {fonction.repos} secondes")
                    self._lancer_timer(fonction.repos)
        
        print("\nRoutine terminée !")

    def _lancer_timer(self, duree):
        """Affiche un décompte pour le timer."""
        for i in range(duree, 0, -1):
            print(f"  {i}...", end="\r")
            time.sleep(1)
        print("  Temps écoulé !")

# Sauvegarde les routines dans un fichier JSON
def sauvegarder_routines(routines, fichier="routines.json"):
    with open(fichier, "w") as f:
        json.dump(routines, f, default=lambda o: o.__dict__, indent=4)

# Charge les routines depuis un fichier JSON
def charger_routines():
    # Vérifier si le fichier existe
    if not os.path.exists('routines.json'):
        return {}  # Si le fichier n'existe pas, retourner un dictionnaire vide
    
    with open('routines.json', 'r') as file:
        data = json.load(file)
    
    routines = {}
    for nom, details in data.items():
        fonctions = [Fonction(**f) for f in details["fonctions"]]  # Crée des objets Fonction sans 'dureetot'
        routines[nom] = Routine(nom, fonctions)
    
    return routines


def menu_principal():
    routines = charger_routines()  # Charger les routines existantes au démarrage
    routine_active = None  # Routine actuellement sélectionnée

    while True:
        print("\nMenu principal :")
        print("1. Créer une routine")
        print("2. Sélectionner une routine")
        print("3. Quitter")
        choix = input("Choix : ")

        if choix == "1":
            # Créer une nouvelle routine
            nom = input("Nom de la nouvelle routine : ")
            if nom in routines:
                print("Une routine avec ce nom existe déjà.")
            else:
                routines[nom] = Routine(nom)
                print(f"Routine '{nom}' créée !")
                sauvegarder_routines(routines)  # Sauvegarder après création

        elif choix == "2":
            # Sélectionner une routine existante
            if not routines:
                print("Aucune routine disponible. Créez-en une d'abord.")
            else:
                print("Routines disponibles :")
                for nom in routines:
                    print(f"- {nom}")
                nom = input("Nom de la routine à sélectionner : ")
                if nom in routines:
                    routine_active = routines[nom]
                    print(f"Routine '{nom}' sélectionnée.")
                    menu_gestion(routine_active, routines)  # Passer au menu de gestion
                else:
                    print("Routine non trouvée.")

        else:
            print("Au revoir !")
            sauvegarder_routines(routines)  # Sauvegarder avant de quitter
            break

def menu_gestion(routine, routines):
    while True:
        print(f"\nGestion de la routine : {routine.nom}")
        print("1. Ajouter un exercice")
        print("2. Retirer un exercice")
        print("3. Afficher la durée totale de la routine")
        print("4. Exécuter la routine")
        print("5. Revenir au menu principal")
        choix = input("Choix : ")

        if choix == "1":
            # Ajouter un exercice
            nom = input("Nom de l'exercice : ")
            duree = int(input("Durée en secondes (0 si basé sur un nombre d'unités) : "))
            unites = int(input("Nombre d'unités (0 si basé sur un timer) : "))
            repetitions = int(input("Nombre de répétitions : "))
            repos = int(input("Temps de repos (en secondes) : "))
            fonction = Fonction(nom, duree, repetitions, repos, unites)
            routine.ajouter_fonction(fonction)
            print("Exercice ajouté !")
            sauvegarder_routines(routines)  # Sauvegarder après ajout

        elif choix == "2":
            # Retirer un exercice
            nom = input("Nom de l'exercice à retirer : ")
            exercice = next((f for f in routine.fonctions if f.nom == nom), None)
            if exercice:
                routine.retirer_fonction(exercice)
                print("Exercice retiré !")
                sauvegarder_routines(routines)  # Sauvegarder après retrait
            else:
                print("Exercice non trouvé.")

        elif choix == "3":
            # Afficher la durée totale
            print("Durée totale de la routine :", routine.duree_totale(), "secondes")

        elif choix == "4":
            # Exécuter la routine
            routine.executer()

        else:
            # Revenir au menu principal
            print("Retour au menu principal.")
            break

# Appel du menu principal pour lancer le programme
menu_principal()


#Le temps de repos n'est pas sur la derniere repetition, mais si ce n'est pas le dernier exercice, il y a un temps de repos dans l'execution et dans la duréetot
#Il faudrait rename le fichier