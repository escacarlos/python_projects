# Auteurs: Équipe IFT-1004

from tp3.Partie1.piece import Piece
from tp3.Partie1.position import Position


class Damier:
    """Plateau de jeu d'un jeu de dames. Contient un ensemble de pièces positionnées à une certaine position
    sur le plateau.

    Attributes:
        cases (dict): Dictionnaire dont une clé représente une Position, et une valeur correspond à la Piece
            positionnée à cet endroit sur le plateau. Notez bien qu'une case vide (sans pièce blanche ou noire)
            correspond à l'absence de clé la position de cette case dans le dictionnaire.

        n_lignes (int): Le nombre de lignes du plateau. La valeur est 8 (constante).
        n_colonnes (int): Le nombre de colonnes du plateau. La valeur est 8 (constante).

    """

    def __init__(self):
        """Constructeur du Damier. Initialise un damier initial de 8 lignes par 8 colonnes.

        """
        self.n_lignes = 8
        self.n_colonnes = 8

        self.cases = {
            Position(7, 0): Piece("blanc", "pion"),
            Position(7, 2): Piece("blanc", "pion"),
            Position(7, 4): Piece("blanc", "pion"),
            Position(7, 6): Piece("blanc", "pion"),
            Position(6, 1): Piece("blanc", "pion"),
            Position(6, 3): Piece("blanc", "pion"),
            Position(6, 5): Piece("blanc", "pion"),
            Position(6, 7): Piece("blanc", "pion"),
            Position(5, 0): Piece("blanc", "pion"),
            Position(5, 2): Piece("blanc", "pion"),
            Position(5, 4): Piece("blanc", "pion"),
            Position(5, 6): Piece("blanc", "pion"),
            Position(2, 1): Piece("noir", "pion"),
            Position(2, 3): Piece("noir", "pion"),
            Position(2, 5): Piece("noir", "pion"),
            Position(2, 7): Piece("noir", "pion"),
            Position(1, 0): Piece("noir", "pion"),
            Position(1, 2): Piece("noir", "pion"),
            Position(1, 4): Piece("noir", "pion"),
            Position(1, 6): Piece("noir", "pion"),
            Position(0, 1): Piece("noir", "pion"),
            Position(0, 3): Piece("noir", "pion"),
            Position(0, 5): Piece("noir", "pion"),
            Position(0, 7): Piece("noir", "pion"),
        }
        
    """         self.cases = {

            Position(5, 0): Piece("blanc", "pion"),
            Position(5, 6): Piece("blanc", "pion"),
            Position(4, 1): Piece("noir", "pion"),
            Position(4, 3): Piece("noir", "pion"),
            Position(4, 5): Piece("noir", "pion"),
            Position(4, 7): Piece("noir", "pion"),
            

        } # Pièces test pour certaines fonctions """

    def recuperer_piece_a_position(self, position):
        """Récupère une pièce dans le damier à partir d'une position.

        Args:
            position (Position): La position où récupérer la pièce.

        Returns:
            La pièce (de type Piece) à la position reçue en argument, ou None si aucune pièce n'était à cette position.

        """
        if position not in self.cases:
            return None

        return self.cases[position]

    def position_est_dans_damier(self, position):
        """Vérifie si les coordonnées d'une position sont dans les bornes du damier (entre 0 inclusivement et le nombre
        de lignes/colonnes, exclusement.

        Args:
            position (Position): La position à valider.

        Returns:
            bool: True si la position est dans les bornes, False autrement.

        """
        return 0 <= position.ligne < self.n_lignes and 0 <= position.colonne < self.n_colonnes

    def piece_peut_se_deplacer_vers(self, position_piece, position_cible):
        """Cette méthode détermine si une pièce (à la position reçue) peut se déplacer à une certaine position cible.
        On parle ici d'un déplacement standard (et non une prise).

        Une pièce doit être positionnée à la position_piece reçue en argument (retourner False autrement).

        Une pièce de type pion ne peut qu'avancer en diagonale (vers le haut pour une pièce blanche, vers le bas pour
        une pièce noire). Une pièce de type dame peut avancer sur n'importe quelle diagonale, peu importe sa couleur.
        Une pièce ne peut pas se déplacer sur une case déjà occupée par une autre pièce. Une pièce ne peut pas se
        déplacer à l'extérieur du damier.

        Args:
            position_piece (Position): La position de la pièce source du déplacement.
            position_cible (Position): La position cible du déplacement.

        Returns:
            bool: True si la pièce peut se déplacer à la position cible, False autrement.

        """
        if self.position_est_dans_damier(position_cible):
            piece_a_deplacer = self.recuperer_piece_a_position(position_piece)
            if piece_a_deplacer:
                if position_cible not in self.cases:
                    if piece_a_deplacer.est_dame():
                        if position_cible in position_piece.quatre_positions_diagonales():
                            return True
                    if piece_a_deplacer.est_noire():
                        if position_cible in position_piece.positions_diagonales_bas():
                            return True
                    if piece_a_deplacer.est_blanche():
                        if position_cible in position_piece.positions_diagonales_haut():
                            return True
        return False

    def piece_peut_sauter_vers(self, position_piece, position_cible):
        """Cette méthode détermine si une pièce (à la position reçue) peut sauter vers une certaine position cible.
        On parle ici d'un déplacement qui "mange" une pièce adverse.

        Une pièce doit être positionnée à la position_piece reçue en argument (retourner False autrement).

        Une pièce ne peut que sauter de deux cases en diagonale. N'importe quel type de pièce (pion ou dame) peut sauter
        vers l'avant ou vers l'arrière. Une pièce ne peut pas sauter vers une case qui est déjà occupée par une autre
        pièce. Une pièce ne peut faire un saut que si elle saute par dessus une pièce de couleur adverse.

        Args:
            position_piece (Position): La position de la pièce source du saut.
            position_cible (Position): La position cible du saut.

        Returns:
            bool: True si la pièce peut sauter vers la position cible, False autrement.

        """
        if self.position_est_dans_damier(position_cible):
            piece_a_deplacer = self.recuperer_piece_a_position(position_piece)
            if piece_a_deplacer is not None:
                if position_cible not in self.cases:
                    if position_cible in position_piece.quatre_positions_sauts():
                        position_manger_ligne = position_cible.ligne - position_piece.ligne
                        position_manger_colonne = position_cible.colonne - position_piece.colonne
                        if position_manger_ligne == 2:
                            position_manger_ligne = position_cible.ligne - 1
                        else:
                            position_manger_ligne = position_cible.ligne + 1
                        if position_manger_colonne == 2:
                            position_manger_colonne = position_cible.colonne - 1
                        else:
                            position_manger_colonne = position_cible.colonne + 1
                        piece_a_manger = self.recuperer_piece_a_position(Position(position_manger_ligne,position_manger_colonne))
                        if piece_a_manger is not None:
                            if piece_a_manger.couleur != piece_a_deplacer.couleur:
                                return True
        return False

    def piece_peut_se_deplacer(self, position_piece):
        """Vérifie si une pièce à une certaine position a la possibilité de se déplacer (sans faire de saut).

        ATTENTION: N'oubliez pas qu'étant donné une position, il existe une méthode dans la classe Position retournant
        les positions des quatre déplacements possibles.

        Args:
            position_piece (Position): La position source.

        Returns:
            bool: True si une pièce est à la position reçue et celle-ci peut se déplacer, False autrement.

        """
        deplacement_possible = []
        deplacement_possible_verifier = []
        piece_a_verifier = self.recuperer_piece_a_position(position_piece)
        if piece_a_verifier.est_dame():
            deplacement_possible = position_piece.quatre_positions_diagonales()
        elif piece_a_verifier.est_blanche():
            deplacement_possible = position_piece.positions_diagonales_haut()
        elif piece_a_verifier.est_noire():
            deplacement_possible = position_piece.positions_diagonales_bas()
        for i in deplacement_possible:
            if i not in self.cases:
                deplacement_possible_verifier.append(i)
        for j in deplacement_possible_verifier:
            if self.position_est_dans_damier(j) is True:
                return True
        return False

    def piece_peut_faire_une_prise(self, position_piece):
        """Vérifie si une pièce à une certaine position a la possibilité de faire une prise.

        Warning:
            N'oubliez pas qu'étant donné une position, il existe une méthode dans la classe Position retournant
            les positions des quatre sauts possibles.

        Args:
            position_piece (Position): La position source.

        Returns:
            bool: True si une pièce est à la position reçue et celle-ci peut faire une prise. False autrement.

        """
        possibilite_de_saut = position_piece.quatre_positions_sauts()
        saut = []
        saut_possible = []
        saut_possible_verif = []
        for i in possibilite_de_saut:
            if i not in self.cases:
                saut.append(i)
        for j in saut:
            if self.position_est_dans_damier(j) is True:
                saut_possible.append(j)
        for k in saut_possible:
            k_ligne = k.ligne - position_piece.ligne
            k_colonne = k.colonne - position_piece.colonne
            if k_ligne == 2:
                k_ligne = k.ligne - 1
            else:
                k_ligne = k.ligne + 1
            if k_colonne == 2:
                k_colonne = k.colonne - 1
            else:
                k_colonne = k.colonne + 1
            piece_a_manger = self.recuperer_piece_a_position(Position(k_ligne, k_colonne))
            if piece_a_manger is not None:
                if piece_a_manger.couleur != (self.recuperer_piece_a_position(position_piece)).couleur:
                    saut_possible_verif.append(k)
        if len(saut_possible_verif) > 0:
            return True
        else:
            return False

    def piece_de_couleur_peut_se_deplacer(self, couleur):
        """Vérifie si n'importe quelle pièce d'une certaine couleur reçue en argument a la possibilité de se déplacer
        vers une case adjacente (sans saut).

        ATTENTION: Réutilisez les méthodes déjà programmées!

        Args:
            couleur (str): La couleur à vérifier.

        Returns:
            bool: True si une pièce de la couleur reçue peut faire un déplacement standard, False autrement.
        """
        listecases = list(self.cases)
        for i in listecases:
            # print(i)
            if (self.cases[i]).couleur == couleur:
                if self.piece_peut_se_deplacer(i) is True:
                    return True
        return False

    def piece_de_couleur_peut_faire_une_prise(self, couleur):
        """Vérifie si n'importe quelle pièce d'une certaine couleur reçue en argument a la possibilité de faire un
        saut, c'est à dire vérifie s'il existe une pièce d'une certaine couleur qui a la possibilité de prendre une
        pièce adverse.

        ATTENTION: Réutilisez les méthodes déjà programmées!

        Args:
            couleur (str): La couleur à vérifier.

        Returns:
            bool: True si une pièce de la couleur reçue peut faire un saut (une prise), False autrement.
        """
        listecases = list(self.cases)
        for i in listecases:
            # print(i)
            if (self.cases[i]).couleur == couleur:
                if self.piece_peut_faire_une_prise(i) is True:
                    return True
        return False
    
    def deplacer(self, position_source, position_cible):
        """Effectue le déplacement sur le damier. Si le déplacement est valide, on doit mettre à jour le dictionnaire
        self.cases, en déplaçant la pièce à sa nouvelle position (et possiblement en supprimant une pièce adverse qui a
        été prise).

        Cette méthode doit également:
        - Promouvoir un pion en dame si celui-ci atteint l'autre extrémité du plateau.
        - Retourner un message indiquant "ok", "prise" ou "erreur".

        ATTENTION: Si le déplacement est effectué, cette méthode doit retourner "ok" si aucune prise n'a été faite,
            et "prise" si une pièce a été prise.
        ATTENTION: Ne dupliquez pas de code! Vous avez déjà programmé (ou allez programmer) des méthodes permettant
            de valider si une pièce peut se déplacer vers un certain endroit ou non.

        Args:
            position_source (Position): La position source du déplacement.
            position_cible (Position): La position cible du déplacement.

        Returns:
            str: "ok" si le déplacement a été effectué sans prise, "prise" si une pièce adverse a été prise, et
                "erreur" autrement.

        """
        if not self.position_est_dans_damier(position_source) or not self.position_est_dans_damier(position_cible):
            return "erreur"
        
        if self.piece_peut_sauter_vers(position_source,position_cible) is True:
            piece_a_deplacer = self.recuperer_piece_a_position(position_source)
            print(piece_a_deplacer.type_de_piece)
            position_manger_ligne = position_cible.ligne - position_source.ligne
            position_manger_colonne = position_cible.colonne - position_source.colonne
            if position_manger_ligne == 2:
                position_manger_ligne = position_cible.ligne - 1
            else:
                position_manger_ligne = position_cible.ligne + 1
            if position_manger_colonne == 2:
                position_manger_colonne = position_cible.colonne - 1
            else:
                position_manger_colonne = position_cible.colonne + 1
            piece_a_manger = Position(position_manger_ligne,position_manger_colonne)
            self.cases.pop(piece_a_manger)
            self.cases.pop(position_source)
            if position_cible.ligne == 0 or position_cible.ligne == 7:
                self.cases[Position(position_cible.ligne, position_cible.colonne)] = Piece(piece_a_deplacer.couleur,
                                                                                           "dame")
                return "prise"
            else:
                self.cases[Position(position_cible.ligne, position_cible.colonne)] = (
                    Piece(piece_a_deplacer.couleur, piece_a_deplacer.type_de_piece))
                return "prise"
        if self.piece_peut_se_deplacer_vers(position_source,position_cible) is True:
            piece_a_deplacer = self.recuperer_piece_a_position(position_source)
            self.cases.pop(position_source)
            if position_cible.ligne == 0 or position_cible.ligne == 7:
                self.cases[Position(position_cible.ligne,position_cible.colonne)] = Piece(piece_a_deplacer.couleur,
                                                                                          "dame")
                return "ok"
            else:
                self.cases[Position(position_cible.ligne,position_cible.colonne)] = Piece(piece_a_deplacer.couleur,
                                                                                          piece_a_deplacer.type_de_piece)
                return "ok"

        return "erreur"

    def __repr__(self):
        """Cette méthode spéciale permet de modifier le comportement d'une instance de la classe Damier pour
        l'affichage. Faire un print(un_damier) affichera le damier à l'écran.

        """
        s = " +-0-+-1-+-2-+-3-+-4-+-5-+-6-+-7-+\n"
        for i in range(0, 8):
            s += str(i)+"| "
            for j in range(0, 8):
                if Position(i, j) in self.cases:
                    s += str(self.cases[Position(i, j)])+" | "
                else:
                    s += "  | "
            s += "\n +---+---+---+---+---+---+---+---+\n"

        return s


if __name__ == "__main__":
    print('Test unitaires de la classe "Damier"...')

    un_damier = Damier()

    # TODO: À compléter
    p_1 = Position(8,1)
    p_2 = Position(1,8)
    p_3 = Position(-1,1)
    p_4 = Position(1, -1)
    p_5 = Position(1, 1)
    p_6 = Position(5,0)
    p_7 = Position(4, 1)
    p_8 = Position(4, -1)
    p_9 = Position(0,0)
    p_10 = Position(7,0)
    p_11 = Position(6, 1)
    p_12 = Position(3,2)
    p_13 = Position(2,1)

    damier_test = Damier()

    assert ((damier_test.position_est_dans_damier(p_1)) is False)
    assert ((damier_test.position_est_dans_damier(p_2)) is False)
    assert ((damier_test.position_est_dans_damier(p_3)) is False)
    assert ((damier_test.position_est_dans_damier(p_4)) is False)
    assert ((damier_test.position_est_dans_damier(p_5)) is True)

    assert ((damier_test.piece_peut_se_deplacer_vers(p_6, p_7)) is True)
    assert ((damier_test.piece_peut_se_deplacer_vers(p_6, p_8)) is False)
    assert ((damier_test.piece_peut_se_deplacer_vers(p_9, p_5)) is False)
    assert ((damier_test.piece_peut_se_deplacer_vers(p_10, p_11)) is False)

    damier_test.cases[Position(4, 1)]= Piece("noir", "pion")
    assert ((damier_test.piece_peut_sauter_vers(p_6, p_12)) is True)
    damier_test.cases[Position(4, 1)] = Piece("blanc", "pion")
    assert ((damier_test.piece_peut_sauter_vers(p_6, p_12)) is False)
    damier_test.cases.pop(Position(4, 1))

    assert ((damier_test.piece_peut_se_deplacer(p_13)) is True)
    assert ((damier_test.piece_peut_se_deplacer(p_10)) is False)

    damier_test.cases[Position(4, 1)] = Piece("noir", "pion")
    assert ((damier_test.piece_peut_faire_une_prise(p_6)) is True)
    damier_test.cases[Position(4, 1)] = Piece("blanc", "pion")
    assert ((damier_test.piece_peut_faire_une_prise(p_6)) is False)
    damier_test.cases.pop(Position(4, 1))

    damier_test.cases[Position(4, 1)] = Piece("noir", "pion")
    damier_test.cases[Position(4, 3)] = Piece("noir", "pion")
    damier_test.cases[Position(4, 5)] = Piece("noir", "pion")
    damier_test.cases[Position(4, 7)] = Piece("noir", "pion")
    assert ((damier_test.piece_de_couleur_peut_se_deplacer("blanc")) is False)
    assert ((damier_test.piece_de_couleur_peut_se_deplacer("noir")) is True)
    damier_test.cases.pop(Position(4, 1))
    damier_test.cases.pop(Position(4, 3))
    damier_test.cases.pop(Position(4, 5))
    damier_test.cases.pop(Position(4, 7))

    assert ((damier_test.piece_de_couleur_peut_faire_une_prise("noir")) is False)
    damier_test.cases[Position(3, 2)] = Piece("blanc", "pion")
    assert ((damier_test.piece_de_couleur_peut_faire_une_prise("noir")) is True)
    damier_test.cases.pop(Position(3, 2))

    damier_test.deplacer(p_6, p_7)
    damier_test.deplacer(Position(2,1), Position(3,2))
    damier_test.deplacer(Position(2, 3), Position(3, 4))
    damier_test.deplacer(Position(3, 4), Position(4, 5))
    damier_test.deplacer(Position(1, 0), Position(2, 1))
    damier_test.deplacer(Position(0, 1), Position(1, 0))
    damier_test.deplacer(Position(4, 1), Position(2, 3))
    damier_test.deplacer(Position(2, 3), Position(0, 1))
    damier_test.deplacer(Position(0, 1), Position(1, 2))
    print(damier_test.cases)
    
    print('Test unitaires passés avec succès!')

    # NOTEZ BIEN: Pour vous aider lors du développement, affichez le damier!
    print(un_damier)
    print(damier_test)
    