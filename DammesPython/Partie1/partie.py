# Auteurs: Équipe IFT-1004

from tp3.Partie1.damier import Damier
from tp3.Partie1.position import Position
from tp3.Partie1.piece import Piece


class Partie:
    """Gestionnaire de partie de dames.

    Attributes:
        damier (Damier): Le damier de la partie, contenant notamment les pièces.
        couleur_joueur_courant (str): Le joueur à qui c'est le tour de jouer.
        doit_prendre (bool): Un booléen représentant si le joueur actif doit absolument effectuer une prise
            de pièce. Sera utile pour valider les mouvements et pour gérer les prises multiples.
        position_source_selectionnee (Position): La position source qui a été sélectionnée. Utile pour sauvegarder
            cette information avant de poursuivre. Contient None si aucune pièce n'est sélectionnée.
        position_source_forcee (Position): Une position avec laquelle le joueur actif doit absolument jouer. Le
            seul moment où cette position est utilisée est après une prise: si le joueur peut encore prendre
            d'autres pièces adverses, il doit absolument le faire. Ce membre contient None si aucune position n'est
            forcée.

    """
    def __init__(self):
        """Constructeur de la classe Partie. Initialise les attributs à leur valeur par défaut. Le damier est construit
        avec les pièces à leur valeur initiales, le joueur actif est le joueur blanc, et celui-ci n'est pas forcé
        de prendre une pièce adverse. Aucune position source n'est sélectionnée, et aucune position source n'est forcée.

        """
        self.damier = Damier()
        self.couleur_joueur_courant = "blanc"
        self.doit_prendre = False
        self.position_source_selectionnee = None
        self.position_source_forcee = None


    def position_source_valide(self, position_source):
        """Vérifie la validité de la position source, notamment:
            - Est-ce que la position contient une pièce?
            - Est-ce que cette pièce est de la couleur du joueur actif?
            - Si le joueur doit absolument continuer son mouvement avec une prise supplémentaire, a-t-il choisi la
              bonne pièce?

        Cette méthode retourne deux valeurs. La première valeur est Booléenne (True ou False), et la seconde valeur est
        un message d'erreur indiquant la raison pourquoi la position n'est pas valide (ou une chaîne vide s'il n'y a pas
        d'erreur).

        ATTENTION: Utilisez les attributs de la classe pour connaître les informations sur le jeu! (le damier, le joueur
            actif, si une position source est forcée, etc.

        ATTENTION: Vous avez accès ici à un attribut de type Damier. vous avez accès à plusieurs méthodes pratiques
            dans le damier qui vous simplifieront la tâche ici :)

        Args:
            position_source (Position): La position source à valider.

        Returns:
            bool, str: Un couple où le premier élément représente la validité de la position (True ou False), et le
                 deuxième élément est un message d'erreur (ou une chaîne vide s'il n'y a pas d'erreur).

        """      
        piece_source = self.damier.recuperer_piece_a_position(position_source)
        
        if piece_source is None:
            return False, "La position source ne contient pas de pièce"
        
        if piece_source.couleur != self.couleur_joueur_courant:
            return False, "La pièce sélectionnée n'appartient pas au joueur actif."
        
        try:
            if self.position_source_forcee == None:
                pass
        except AttributeError:
            if position_source != self.position_source_forcee:
                return False, "Le joueur doit continuer ses prises avec la pièce en position {}.".format(self.position_source_forcee) 
        
        if self.doit_prendre:   
            if not self.damier.piece_peut_faire_une_prise(position_source):
                return False, "Le joueur doit effectuer une prise"

        if not self.damier.piece_peut_se_deplacer(position_source) and not self.damier.piece_peut_faire_une_prise(position_source):
            return False, "La position source selectionnée n'a pas des deplacements possibles"

        self.position_source_selectionnee = position_source
        return True, ""


    def position_cible_valide(self, position_cible):
        """Vérifie si la position cible est valide (en fonction de la position source sélectionnée). Doit non seulement
        vérifier si le déplacement serait valide (utilisez les méthodes que vous avez programmées dans le Damier!), mais
        également si le joueur a respecté la contrainte de prise obligatoire.

        Returns:
            bool, str: Deux valeurs, la première étant Booléenne et indiquant si la position cible est valide, et la
                seconde valeur est une chaîne de caractères indiquant un message d'erreur (ou une chaîne vide s'il n'y
                a pas d'erreur).

        """
        if not self.damier.position_est_dans_damier(position_cible):
            return False, "La position cible n'est pas valide."

        if not self.damier.piece_peut_se_deplacer_vers(self.position_source_selectionnee, position_cible) and \
            not self.damier.piece_peut_sauter_vers(self.position_source_selectionnee, position_cible):
            return False, "Déplacement invalide"

        if self.doit_prendre:
            if not self.damier.piece_peut_sauter_vers(self.position_source_selectionnee, position_cible):
                return False, "Le joueur doit effectuer une prise"

        return True, ""
    

    def demander_positions_deplacement(self):
        """Demande à l'utilisateur les positions sources et cible, et valide ces positions. Cette méthode doit demander
        les positions à l'utilisateur tant que celles-ci sont invalides.

        Cette méthode ne doit jamais planter, peu importe ce que l'utilisateur entre.

        Returns:
            Position, Position: Un couple de deux positions (source et cible).

        """
        position_source = None
        position_cible = None

        # Input position_source
        source_input = input("Entrez la position source ligne et colonne: ")
        while True:
            source_input = source_input.strip().replace(' ', '')
            if source_input[0] not in '0123456789':
                print("Erreur, entrez des chiffres valides")
                source_input = input("Entrez la position source ligne et colonne: ")
                continue
            elif source_input[1] not in '0123456789':
                print("Erreur, entrez des chiffres valides")
                source_input = input("Entrez la position source ligne et colonne: ")
                continue
            else:
                p_ligne = int(source_input[0])
                p_colonne = int(source_input[1])
                position_source = Position(p_ligne, p_colonne)
                print(f"Position entrée: ({source_input[0]},{source_input[1]})")

            if self.position_source_valide(position_source)[0]:
                break
            else: 
                print("Erreur, position non valide")
                print(self.position_source_valide(position_source)[1])

            source_input = input("Entrez la position source ligne et colonne: ")

        # Input position_cible
        cible_input = input("Entrez la position cible ligne et colonne: ")
        while True:
            cible_input = cible_input.strip().replace(' ', '')
            if cible_input[0] not in '0123456789':
                print("Erreur, entrez de chiffres valides")
                cible_input = input("Entrez la position source ligne et colonne: ")
                continue
            elif cible_input[1] not in '0123456789':
                print("Erreur, entrez de chiffres valides")
                cible_input = input("Entrez la position source ligne et colonne: ")
                continue
            else:
                p_ligne = int(cible_input[0])
                p_colonne = int(cible_input[1])
                position_cible = Position(p_ligne, p_colonne)
                print(f"Position entrée: ({cible_input[0]},{cible_input[1]})")

            if self.position_cible_valide(position_cible)[0]:
                break
            else: 
                print("Erreur, position non valide")
                print(self.position_cible_valide(position_cible)[1])

            cible_input = input("Entrez la position cible ligne et colonne: ")

        return position_source, position_cible


    def tour(self):
        """Cette méthode effectue le tour d'un joueur, et doit effectuer les actions suivantes:
        - Assigne self.doit_prendre à True si le joueur courant a la possibilité de prendre une pièce adverse.
        - Affiche l'état du jeu
        - Demander les positions source et cible (utilisez self.demander_positions_deplacement!)
        - Effectuer le déplacement (à l'aide de la méthode du damier appropriée)
        - Si une pièce a été prise lors du déplacement, c'est encore au tour du même joueur si celui-ci peut encore
          prendre une pièce adverse en continuant son mouvement. Utilisez les membres self.doit_prendre et
          self.position_source_forcee pour forcer ce prochain tour!
        - Si aucune pièce n'a été prise ou qu'aucun coup supplémentaire peut être fait avec la même pièce, c'est le
          tour du joueur adverse. Mettez à jour les attributs de la classe en conséquence.

        """

        # Détermine si le joueur courant a la possibilité de prendre une pièce adverse.
        if self.damier.piece_de_couleur_peut_faire_une_prise(self.couleur_joueur_courant):
            self.doit_prendre = True

        # Affiche l'état du jeu
        print(self.damier)
        print("")
        print("Tour du joueur", self.couleur_joueur_courant, end=".")
        if self.doit_prendre:
            if self.position_source_forcee is None:
                print(" Doit prendre une pièce.")
            else:
                print(" Doit prendre avec la pièce en position {}.".format(self.position_source_forcee))
        else:
            print("")

        # Demander les positions
        position_source, position_cible = self.demander_positions_deplacement()

        # Effectuer le déplacement (à l'aide de la méthode du damier appropriée)
        deplacement = self.damier.deplacer(position_source, position_cible)

        # Mettre à jour les attributs de la classe
        if deplacement == 'prise':
            self.doit_prendre = False
            if self.damier.piece_peut_faire_une_prise(position_cible):
                self.position_source_forcee = position_cible
            else:
                self.position_source_forcee = None
            if self.damier.piece_de_couleur_peut_faire_une_prise(self.couleur_joueur_courant):
                self.doit_prendre = True
        elif deplacement == 'ok':
            self.doit_prendre = False
            self.couleur_joueur_courant = "blanc" if self.couleur_joueur_courant == "noir" else "noir"


    def jouer(self):
        """Démarre une partie. Tant que le joueur courant a des déplacements possibles (utilisez les méthodes
        appriopriées!), un nouveau tour est joué.

        Returns:
            str: La couleur du joueur gagnant.
        """

        while self.damier.piece_de_couleur_peut_se_deplacer(self.couleur_joueur_courant) or \
                self.damier.piece_de_couleur_peut_faire_une_prise(self.couleur_joueur_courant):
            self.tour()

        if self.couleur_joueur_courant == "blanc":
            return "noir"
        else:
            return "blanc"
    
    def nouvelle_partie(self):
        """Méthode qui permet de réinitialiser la partie

        """    
        self.damier.cases = {
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
        
        self.couleur_joueur_courant = "blanc"
        self.doit_prendre = False
        self.position_source_forcee = None


