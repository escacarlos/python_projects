from case import Case
from liste_de_cases import ListeDeCases
from liste_circulaire import ListeCirculaire
from file import File
from typing import Optional

class Joueur:
    def __init__(self, position: "ListeDeCases.Iterateur", nom: str = "default") -> None:
        self.position: ListeDeCases.Iterateur = position
        self.nom: str = nom

    def __str__(self) -> str:
        return f"{self.nom} : {self.position.position_courante()}"


class Resultat:
    def __init__(self, nombre_de_tours: int, nom_gagnant: str = "") -> None:
        self.nombre_de_tours: int = nombre_de_tours
        self.nom: str = nom_gagnant


class JeuSerpentsEtEchelles:
    def __init__(self) -> None:
        self.m_cases: ListeDeCases = ListeDeCases()
        self.m_choix: ListeCirculaire = ListeCirculaire()
        self.m_joueurs: File = File()

    def jouer(self, maximum_de_tours: int) -> Resultat:
        tour_actuel: int = 0
        choix_courante: ListeCirculaire = ListeCirculaire(self.m_choix)

        while tour_actuel < maximum_de_tours - 1:
            tour_actuel += 1
            for _ in range(self.m_joueurs.taille()):
                un_joueur: Joueur = self.m_joueurs.defiler()

                une_couleur: Case.Couleur = choix_courante.element(1)
                choix_courante.enlever_pos(1)
                choix_courante.ajouter_fin(une_couleur)

                decoration_courante: Case.Decoration = Case.Decoration.Aucune

                if un_joueur.position.existe_case_suivante_couleur(une_couleur):
                    un_joueur.position.case_suivante(une_couleur)
                    decoration_courante = un_joueur.position.case_courante().decoration

                if decoration_courante == Case.Decoration.Serpent:
                    une_couleur = choix_courante.element(1)
                    choix_courante.enlever_pos(1)
                    choix_courante.ajouter_fin(une_couleur)

                    if un_joueur.position.existe_case_precedente(une_couleur):
                        un_joueur.position.case_precedente(une_couleur)

                elif decoration_courante == Case.Decoration.Echelle:
                    une_couleur = choix_courante.element(1)
                    choix_courante.enlever_pos(1)
                    choix_courante.ajouter_fin(une_couleur)

                    if un_joueur.position.existe_case_suivante_couleur(une_couleur):
                        un_joueur.position.case_suivante(une_couleur)

                if un_joueur.position.est_a_derniere_case():
                    self.m_joueurs.enfiler(un_joueur)
                    return Resultat(tour_actuel, un_joueur.nom)

                self.m_joueurs.enfiler(un_joueur)

        return Resultat(maximum_de_tours)

    def effacer(self) -> None:
        while self.m_cases.taille() > 0:
            self.m_cases.enlever_case(1)
        while self.m_choix.taille() > 0:
            self.m_choix.enlever_pos(1)
        while self.m_joueurs.taille() > 0:
            self.m_joueurs.defiler()

    def ajouter_case(self, case: Case) -> None:
        self.m_cases.ajouter_case_a_la_fin(case)

    def ajouter_choix(self, couleur: Case.Couleur) -> None:
        self.m_choix.ajouter_fin(couleur)

    def ajouter_joueur(self, joueur: Joueur) -> None:
        self.m_joueurs.enfiler(joueur)

    def premiere_case(self) -> Case:
        return self.m_cases.debut()

    def affiche_resultats(self, gagnant: Resultat) -> None:
        if gagnant.nom:
            print(f"Gagnant : {gagnant.nom}")
        else:
            print("Aucun gagnant")
        print(f"Nombre de tours réalisés : {gagnant.nombre_de_tours}")
        print("Position des joueurs :")
        print(self.m_joueurs)
        print("Plateau de jeu:")
        print(self.m_cases)
        print("Liste de choix:")
        print(self.m_choix)
