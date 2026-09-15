# Auteurs: Équipe IFT-1004

from tkinter import Tk, Label, NSEW, Menu
from tp3.Partie2.canvas_damier import CanvasDamier
from tp3.Partie1.partie import Partie
from tp3.Partie1.position import Position
from operator import countOf


class FenetrePartie(Tk):
    """Interface graphique de la partie de dames.

    Attributes:
        partie (Partie): Le gestionnaire de la partie de dame
        canvas_damier (CanvasDamier): Le «widget» gérant l'affichage du damier à l'écran
        messages (Label): Un «widget» affichant des messages textes à l'utilisateur du programme
    """

    def __init__(self):
        """Constructeur de la classe FenetrePartie. On initialise une partie en utilisant la classe Partie du TP3 et
        on dispose les «widgets» dans la fenêtre.
        """

        # Appel du constructeur de la classe de base (Tk)
        super().__init__()

        # La partie
        self.partie = Partie()

        # Création du canvas damier.
        self.canvas_damier = CanvasDamier(self, self.partie.damier, 500)
        self.canvas_damier.grid(sticky=NSEW, row=0,column=0)
        self.geometry("484x525")
        self.canvas_damier.bind('<Button-1>', self.selectionner)
        
        # Ajout d'une étiquette pour le joueur courant
        self.joueur_courant = Label(self)
        self.joueur_courant.grid()
        self.joueur_courant['foreground'] = 'black'
        self.joueur_courant['text'] = 'Tour du joueur {}.'.format(self.partie.couleur_joueur_courant)
        
        # Ajout d'une étiquette d'information.
        self.messages = Label(self)
        self.messages.grid()
        


        # Nom de la fenêtre («title» est une méthode de la classe de base «Tk»)
        self.title("Jeu de dames")
        
        # Création de la barre de menu
        self.barre_menu= Menu(self)
        self.config(menu=self.barre_menu)
        
        # Création du menu principal
        menu = Menu(self.barre_menu, tearoff=False)
        menu = Menu(self.barre_menu, tearoff=False)
        self.barre_menu.add_cascade(label="Menu", menu=menu)
        menu.add_command(label="Nouvelle Partie", command=self.nouvelle_partie)
        menu.add_command(label="Quitter", command=self.quitter)
        
        # Truc pour le redimensionnement automatique des éléments de la fenêtre.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Changer icone
        #chemin_icone = 'tp3\Partie2\icone.ico'
        #self.iconbitmap(chemin_icone)
        # Attribution : https://www.flaticon.com/free-icon/checker-board_3270014


    
    
    def quitter(self):
        """Fonction permettant de quitter le jeu
        """ 
        self.destroy() 
        
    def nouvelle_partie(self):
        """Méthode qui permet de réinitialiser la partie.
        """
        self.partie.nouvelle_partie()
        self.joueur_courant['foreground'] = 'black'
        self.joueur_courant['text'] = 'Tour du joueur {}.'.format(self.partie.couleur_joueur_courant)
        self.canvas_damier.bind('<Button-1>', self.selectionner)
        self.canvas_damier.actualiser()    
        
    def selectionner(self, event):
        """Méthode qui gère le clic de souris sur le damier.

        Args:
            event (tkinter.Event): Objet décrivant l'évènement qui a causé l'appel de la méthode.

        """

        # On trouve le numéro de ligne/colonne en divisant les positions en y/x par le nombre de pixels par case.
        ligne = event.y // self.canvas_damier.n_pixels_par_case
        colonne = event.x // self.canvas_damier.n_pixels_par_case
        position = Position(ligne, colonne)

        # On récupère l'information sur la pièce à l'endroit choisi.
        piece = self.partie.damier.recuperer_piece_a_position(position)

        if piece is None:
            self.messages['foreground'] = 'red'
            self.messages['text'] = 'Erreur: Aucune pièce à cet endroit.'
        else:
            position_source_valide, erreur_source = self.partie.position_source_valide(position)

            if not position_source_valide:
                self.messages['foreground'] = 'red'
                self.messages['text'] = 'Erreur: {}'.format(erreur_source)
            else:
                self.messages['foreground'] = 'black'
                self.messages['text'] = 'Pièce sélectionnée à la position {}.\nSelectionnez la position cible pour déplacer la pièce'.format(position)
                self.canvas_damier.bind('<Button-1>', lambda event, source=position: self.deplacement_selectionne(event, source))

    def deplacement_selectionne(self, event, position_source):
        """Méthode qui gére le clic de souris pour sélectionner la position cible.

        Args:
            event (tkinter.Event): Objet décrivant l'évènement qui a causé l'appel de la méthode.
            position_source (Position): La position source de la pièce.

        Returns: None

        """

        #print("Deplacement selectionne. Position source:", position_source)

        # Trouver position cible
        ligne = event.y // self.canvas_damier.n_pixels_par_case
        colonne = event.x // self.canvas_damier.n_pixels_par_case
        position_cible = Position(ligne, colonne)

        #print("Deplacement selectionne. Position cible:", position_cible)

        # Verifier si la position cible est valide
        deplacement_valide, erreur_cible = self.partie.position_cible_valide(position_cible)
        
        if deplacement_valide:
            #print("Deplacement valide. Effectuer deplacement.")
            deplacement = self.partie.damier.deplacer(position_source, position_cible)
            self.tour(position_cible, deplacement)

        else:
            #print("Erreur cible:", erreur_cible)
            self.messages['foreground'] = 'red'
            self.messages['text'] = 'Erreur: {}'.format(erreur_cible)
            self.canvas_damier.unbind('<Button-1>')
            self.canvas_damier.bind('<Button-1>', self.selectionner)
            self.canvas_damier.actualiser()

                
    def tour(self, position_cible, deplacement):
        """Cette méthode effectue le tour d'un joueur

        Args:
            position_cible (Position): La position source de la pièce.
            deplacement (str): Le type de déplacement de la pièce ("prise" ou "ok")

        Returns: None

        """
        
        # Mettre à jour les attributs de la classe
        if deplacement == 'prise':
            print("prise")
            self.partie.doit_prendre = False
            if self.partie.damier.piece_peut_faire_une_prise(position_cible):
                self.partie.position_source_forcee = position_cible
                self.partie.doit_prendre = True
            else:
                self.partie.position_source_forcee = None
            # Détermine si le joueur courant a la possibilité de prendre une pièce adverse.
            if self.partie.damier.piece_de_couleur_peut_faire_une_prise(self.partie.couleur_joueur_courant):
                self.partie.doit_prendre = True
        elif deplacement == 'ok':
            print('ok')
            self.partie.doit_prendre = False
            self.partie.couleur_joueur_courant = "blanc" if self.partie.couleur_joueur_courant == "noir" else "noir"
            # Détermine si le joueur courant a la possibilité de prendre une pièce adverse.
            if self.partie.damier.piece_de_couleur_peut_faire_une_prise(self.partie.couleur_joueur_courant):
                self.partie.doit_prendre = True
        
        # Arrête la partie s'il y a un gagnant
        if self.partie_finie()[0]:
            self.messages['foreground'] = 'black'
            self.messages['text'] = 'Le gagnant est le joueur {}.'.format(self.partie_finie()[1])
            return
        # Rétroaction
        self.messages['foreground'] = 'black'
        self.messages['text'] = 'Déplacement effectué.'
        # Commence le prochain tour
        self.canvas_damier.bind('<Button-1>', self.selectionner)
        self.canvas_damier.actualiser()
        # Écrit message pour le prochain joueur
        self.joueur_courant['foreground'] = 'black'
        self.joueur_courant['text'] = 'Tour du joueur {}.'.format(self.partie.couleur_joueur_courant)
    
    def partie_finie(self):
        """Détermine si la partie est finie et retourne aussi le joueur gagnant en valeur
        """ 
        if self.partie.damier.piece_de_couleur_peut_se_deplacer(self.partie.couleur_joueur_courant) or \
                self.partie.damier.piece_de_couleur_peut_faire_une_prise(self.partie.couleur_joueur_courant):
            return False, None
        if self.partie.couleur_joueur_courant == "blanc":
            return True, "noir"
        else:
            return True, "blanc"  
