# from generateur_nombres_aleatoires import GenerateurNombresAleatoires
from case import Case
from jeu_serpent_et_echelles import Joueur, JeuSerpentsEtEchelles
from generateur_nombres_aleatoires import GenerateurNombresAleatoires
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jeu_serpent_et_echelles import Jeu

class GenerateurAleatoireJeuSerpentsEtEchelles:
    def __init__(self, init_nombre_aleatoire: int = 1) -> None:
        self.m_compteur_nom_joueurs: int = 0
        # random.seed(init_nombre_aleatoire)
        self.gen = GenerateurNombresAleatoires(init_nombre_aleatoire)

    def generer(self, jeu: "JeuSerpentsEtEchelles", nombre_cases: int, nombre_de_choix: int, nombre_de_joueurs: int) -> None:
        self.m_compteur_nom_joueurs = 0
        jeu.effacer()
        self.generer_cases(jeu, nombre_cases)
        self.generer_choix(jeu, nombre_de_choix)
        self.generer_joueurs(jeu, nombre_de_joueurs)

    def generer_cases(self, jeu: "JeuSerpentsEtEchelles", nombre_cases: int) -> None:
        for _ in range(nombre_cases):
            nouvelle_case = Case(
                self.choisir_une_couleur_aleatoirement(),
                self.choisir_une_decoration_aleatoirement()
            )
            jeu.ajouter_case(nouvelle_case)

    def choisir_une_couleur_aleatoirement(self) -> Case.Couleur:
        return random.choice(list(Case.Couleur))
        # return Case.Couleur(self.gen.pige() % Case.nombreCouleurs)

    def choisir_une_decoration_aleatoirement(self) -> Case.Decoration:
        return random.choice(list(Case.Decoration))
        # return Case.Decoration(self.gen.pige() % Case.nombreDecorations)

    def generer_choix(self, jeu: "Jeu", nombre_choix: int) -> None:
        for _ in range(nombre_choix):
            jeu.ajouter_choix(self.choisir_une_couleur_aleatoirement())

    def generer_joueurs(self, jeu: "Jeu", nombre_joueurs: int) -> None:
        for _ in range(nombre_joueurs):
            jeu.ajouter_joueur(self.generer_un_joueur_aleatoirement(jeu.premiere_case()))

    def generer_un_joueur_aleatoirement(self, it: Case) -> Joueur:
        return Joueur(it, self.choisir_un_nom_aleatoirement())

    def choisir_un_nom_aleatoirement(self) -> str:
        self.m_compteur_nom_joueurs += 1
        return f"Joueur {self.m_compteur_nom_joueurs}"
