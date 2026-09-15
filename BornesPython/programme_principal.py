"""
Module contenant l'exécution du programme pour gérer et analyser l'inventaire des bornes de stationnement de
la ville de Québec.
"""

import inventaire_bornes as ibornes


def demander_une_borne(inventaire, message):
    """ Fonction utilitaire pour demamder un numéro de borne à l'utilisateur et la trouver dans l'inventaire

    Args:
        inventaire (list): La liste des bornes de l'inventaire
        message (str): Le message à afficher à l'utilisateur au moment de lui demander un numéro de borne

    Returns:
        dict: Dictionnaire contenant l'information de la borne
    """
    borne = {'Numero': -1}

    while borne['Numero'] == -1:
        numero = input(message)
        if numero.isnumeric():
            numero = int(numero)
            borne = ibornes.selectionner_borne_par_numero(inventaire, numero)
        if borne['Numero'] == -1:
            print('Numéro de borne introuvable.')

    ibornes.afficher_inventaire([borne])
    return borne


print("Execution du programme d'analyse des bornes")
print("-------------------------------------------")

print("""
Sélectionner le fichier d'inventaire:
1) Inventaire complet ('vdq-bornestationnement.txt')
2) Inventaire réduit ('vdq-bornestationnement-reduit.txt')
3) Autre fichier
""")

choix = ''
while choix not in ('1', '2', '3'):
    choix = input('Choix:')

if choix == '1':
    nom_fichier = 'vdq-bornestationnement.txt'
elif choix == '2':
    nom_fichier = 'vdq-bornestationnement-reduit.txt'
else:
    nom_fichier = input('Entrez le nom de fichier contenant l\'inventaire:')

print('Lecture du fichier...')
inventaire = ibornes.lire_fichier_bornes(nom_fichier)
nb_bornes = ibornes.nombre_de_bornes(inventaire)
print(f'{nb_bornes} bornes répertoriées')

choix = ""

while choix != 'q':
    print("""Actions possibles:
    1) Afficher l'inventaire
    2) Rechercher les bornes par nom de rue
    3) Rechercher les bornes par côté de rue
    4) Calculer la distance entre deux bornes
    5) Trouver la borne la plus près d'une autre
    6) Trouver les bornes les plus éloignées
    7) Trouver la borne centrale
    """)

    choix = input('Choix ("q" pour quitter): ')

    if choix == '1':
        ibornes.afficher_inventaire(inventaire)
    elif choix == '2':
        rue = input("Entrez le nom de la rue: ")
        selection = ibornes.selectionner_bornes_par_rue(inventaire, rue)
        print("\nRésultat de la recherche:")
        ibornes.afficher_inventaire(selection)
    elif choix == '3':
        cote = input("Entrez un côté de la rue: ")
        selection = ibornes.selectionner_bornes_par_cote(inventaire, cote)
        print("\nRésultat de la recherche:")
        ibornes.afficher_inventaire(selection)
    elif choix == '4':
        borne_1 = demander_une_borne(inventaire, "Numéro de la première borne: ")
        borne_2 = demander_une_borne(inventaire, "Numéro de la deuxième borne: ")
        distance = ibornes.calculer_distance_bornes(borne_1, borne_2)
        print(f"\nDistance : {distance:.3} km\n")
    elif choix == '5':
        borne_1 = demander_une_borne(inventaire, "Numéro de la borne de référence: ")
        borne_2 = ibornes.trouver_borne_plus_pres(inventaire, borne_1['Numero'], False)
        print("\nRésultat de la recherche:")
        ibornes.afficher_inventaire([borne_2])
        if borne_1['Rue'] == borne_2['Rue']:
            borne_2 = ibornes.trouver_borne_plus_pres(inventaire, borne_1['Numero'], True)
            print("\nRésultat de la recherche (sur une autre rue):")
            ibornes.afficher_inventaire([borne_2])
    elif choix == '6':
        borne_1, borne_2 = ibornes.trouver_bornes_plus_eloignees(inventaire)
        print("\nRésultat de la recherche:")
        ibornes.afficher_inventaire([borne_1, borne_2])
    elif choix == '7':
        borne = ibornes.trouver_borne_centrale(inventaire)
        print("\nRésultat de la recherche:")
        ibornes.afficher_inventaire([borne])

print("Fin du programme.")