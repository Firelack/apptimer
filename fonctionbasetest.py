class Fonction:
    def __init__(self, nom, duree=None, repetitions=1, repos=0, unites=None):
        """
        Initialise une fonction.
        - `nom`: Nom de l'exercice.
        - `duree`: Durée en secondes (None si basé sur unites).
        - `repetitions`: Nombre de fois que l'exercice est répété.
        - `repos`: Temps de repos entre les répétitions (en secondes).
        - `unites`: Nombre d'unités (par exemple, "10 pompes").
        """
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
        - Ignore les exercices basés sur des unités (car pas de timer).
        """
        return sum(
            f.duree * f.repetitions + f.repos * (f.repetitions - 1)
            for f in self.fonctions if f.est_base_sur_timer()
        )

# Création des exercices
f1 = Fonction("pompes", unites=10, repetitions=3, repos=60)
f2 = Fonction("abdos", duree=20, repetitions=4, repos=30)
f3 = Fonction("squats", unites=15, repetitions=2, repos=45)

# Création de la routine
r = Routine("Routine Matinale", [f1, f2])
print(r)

# Ajout d'un exercice
r.ajouter_fonction(f3)
print("\nAprès ajout d'un exercice :")
print(r)

# Calcul de la durée totale
print("\nDurée totale de la routine (excluant les unités) :", r.duree_totale(), "secondes")
