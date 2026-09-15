from liste_circulaire import ListeCirculaire
from typing import Generic, TypeVar

T = TypeVar("T")

class File(Generic[T]):
    def __init__(self) -> None:
        self.liste: ListeCirculaire[T] = ListeCirculaire()

    def enfiler(self, element: T) -> None:
        """Ajoute un élément à la fin de la file."""
        self.liste.ajouter_fin(element)

    def defiler(self) -> T:
        """Supprime et retourne l'élément en tête de la file."""
        if self.taille() < 1:
            raise ValueError("La file est vide")
        ret: T = self.liste.element(1)
        self.liste.enlever_pos(1)
        return ret

    def taille(self) -> int:
        """Retourne la taille de la file."""
        return self.liste.taille()

    def __str__(self) -> str:
        """Affiche les éléments de la file."""
        return str(self.liste)

if __name__ == '__main__':
    from jeu_serpent_et_echelles import Joueur
    from case import Case
    from liste_de_cases import ListeDeCases
    case1 = Case(Case.Couleur.Rouge, Case.Decoration.Aucune)
    case2 = Case(Case.Couleur.Bleu, Case.Decoration.Serpent)
    case3 = Case(Case.Couleur.Jaune, Case.Decoration.Echelle)
    case4 = Case(Case.Couleur.Vert, Case.Decoration.Aucune)
    myList = ListeDeCases()
    myList.ajouter_case_a_la_fin(case1)
    myList.ajouter_case_a_la_fin(case2)
    myList.ajouter_case_a_la_fin(case3)
    myList.ajouter_case_a_la_fin(case4)
    myIter = myList.debut()
    player1 = Joueur(myIter, "player1")
    player2 = Joueur(myIter, "player2")
    player3 = Joueur(myIter, "player3")
    player4 = Joueur(myIter, "player4")
    myFile = File()
    myFile.enfiler(player1)
    myFile.enfiler(player2)
    myFile.enfiler(player3)
    myFile.enfiler(player4)
    print(myFile.taille())
    print(myFile)
    myFile.defiler()
    print(myFile)
