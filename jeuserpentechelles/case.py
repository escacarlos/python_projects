from enum import Enum

class Case:
    class Couleur(Enum):
        Rouge: int = 0
        Vert: int = 1
        Bleu: int = 2
        Jaune: int = 3

    class Decoration(Enum):
        Aucune: int = 0
        Serpent: int = 1
        Echelle: int = 2

    nombreCouleurs: int = 4
    nombreDecorations: int = 3

    def __init__(self, couleur: "Case.Couleur" = Couleur.Bleu, decoration: "Case.Decoration" = Decoration.Aucune) -> None:
        self.couleur: Case.Couleur = couleur
        self.decoration: Case.Decoration = decoration

    def __str__(self) -> str:
        return f"({self.couleur.name}, {self.decoration_en_lettre()})"
    
    def decoration_en_lettre(self) -> str:
        return {
            Case.Decoration.Serpent: "S",
            Case.Decoration.Echelle: "E",
        }.get(self.decoration, "A")
