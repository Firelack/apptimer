class Routine : 
    def __init__(self, nom, liste_fonctions=[]): 
        self.nom = nom
        self.fonction = liste_fonctions
    def __str__(self): 
        return f"{self.nom} :\n" + "\n".join([str(f) for f in self.fonction])
    def ajouter_fonction(self, fonction): 
        self.fonction.append(fonction)
    def retirer_fonction(self, fonction): 
        self.fonction.remove(fonction)
    def duree_totale(self):
        return sum(f.duree * f.repetitions + f.repos * (f.repetitions - 1) for f in self.fonction)


class Fonction : 
    def __init__(self, nom, duree, repetitions, repos): 
        self.nom = nom
        if duree < 0 or repetitions < 0 or repos < 0:
            raise ValueError("Les valeurs doivent être positives.")
        self.duree = duree
        self.repetitions = repetitions
        self.repos = repos
    def __str__(self): 
        return str(self.nom) + " : " + str(self.duree) + "s, " + str(self.repetitions) + " répétitions, " + str(self.repos) + "s de repos"
    
# Test
f1 = Fonction("pompes", 30, 3, 60)
f2 = Fonction("abdos", 20, 4, 30)
r = Routine("routine1", [f1, f2])
print(r)
f3 = Fonction("squats", 40, 3, 60)
r.ajouter_fonction(f3)
print(r)
r.retirer_fonction(f2)
print(r)
    