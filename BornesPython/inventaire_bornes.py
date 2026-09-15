"""
Module regroupant les fonctions pour gérer et analyser l'inventaire des bornes de stationnement de
la ville de Québec.
"""
import math
from time import perf_counter


def creer_borne(no_borne, cote_rue, nom_topographique, longitute, latitude):
    """
    Construit un dictionnaire contenant les informations pertinentes décrivant une borne

    Args:
        no_borne (int): Le numéro unique de la borne
        cote_rue (str): Le côté de la rue où se trouve la borne
        nom_topographique (str): Le nom de la rue où se trouve la borne
        longitute (float): La postion géographique de la borne (degré longitudinal)
        latitude (float): La postion géographique de la borne (degré latitudinal)

    Returns:
        dict: Un dictionnaire contenant l'information d'une borne
    """
    borne = {}
    borne['Numero'] = no_borne
    borne['Cote'] = cote_rue
    borne['Rue'] = nom_topographique
    borne['Coordonnees'] = (latitude, longitute)
    return borne


def afficher_inventaire(inventaire):
    """
    Affiche l'inventaire des bornes sous la forme d'un tableau dans la console.

    Args:
        inventaire (list): Une liste contenant des bornes. Chacune des bornes est un dictionnaire.
    """
    ligne = '-' * 100
    print(ligne)
    print(f"| {'Numero':6} | {'Cote':4} | {'Rue':35} | {'Coordonnees':42} |")
    print(ligne)
    for borne in inventaire:
        print(f"| {borne['Numero']:6} | {borne['Cote']:4} | {borne['Rue']:35} | {str(borne['Coordonnees']):42} |")
    print(ligne)


def creer_borne_avec_chaine(chaine):
    """
    Construit un dictionnaire contenant les informations pertinentes décrivant une borne, à partir d'une chaîne de
    caractère correspondant à une ligne du fichier contenant l'information sur les bornes. Pensez à utiliser la
    fonction creer_borne().

    Args:
        chaine (str): Une chaîne de caractères contenant les informations sur la borne, séparées par des virgules

    Returns:
        dict: Un dictionnaire contenant les informations sur la borne, tel que retourné par la fonction creer_borne()
    """
    chaine_list = chaine.split(",")
    borne = {}
    if len(chaine_list) > 6:        # len > 6 m'assure que je ne prends pas la dernière ligne
        no_borne = int(chaine_list[1].strip())      # strip() juste en cas des espaces au debut et/ou a la fin
        cote_rue = chaine_list[2].strip()
        nom_topographique = chaine_list[4].strip()
        longitute = float(chaine_list[5].strip())
        latitude = float(chaine_list[6].strip())
        borne = creer_borne(no_borne, cote_rue, nom_topographique, longitute, latitude)

    return borne


def lire_fichier_bornes(nom_fichier):
    """
    Lit un fichier texte contenant l'inventaire des bornes avec une borne par ligne.

    Args:
        nom_fichier (str): Fichier .txt contenant l'inventaire des bornes. Les éléments sur chaque ligne sont
        séparées par une virgule

    Returns:
        list: Une liste de toutes les bornes contenues dans le fichier
    """
    file_handle = open(nom_fichier, 'r')
    inventaire = []
    line = file_handle.readline()       # je ne veux pas avoir la 1er ligne dans ma liste
    while line:
        line = file_handle.readline()
        if line != "":      # pour éviter de prendre une ligne vide et la passer dans ma fonction creer_borne_avec_chaine()
            borne = creer_borne_avec_chaine(line.strip())
            inventaire.append(borne)

    return inventaire


def nombre_de_bornes(inventaire):
    """
    Retourne le nombre de bornes contenu dans un « inventaire ».

    Args:
        inventaire (list): Une liste de bornes

    Returns:
        int: Le nombre de bornes contenues dans l'inventaire.
    """
    return len(inventaire)  # la quantite de bornes(dictionnaires) dans ma liste inventaire


def selectionner_bornes_par_rue(inventaire, rue):
    """
    Sélectionne toutes les bornes sur la rue spécifiée en argument parmi l'inventaire.

    Args:
        inventaire (list): La liste des bornes de l'inventaire
        rue (str): Nom de la rue

    Returns:
        list: Liste des bornes qui sont sur la rue donnée
    """
    borne_list = []
    for borne in inventaire:
        if borne['Rue'] == rue:     # chaque borne dans inventaire et un dictionnaire
            borne_list.append(borne)

    return borne_list


def selectionner_bornes_par_cote(inventaire, cote):
    """
    Sélectionne toutes les bornes du côté spécifié en argument parmi l'inventaire.

    Args:
        inventaire (list): La liste des bornes de l'inventaire
        cote (str): Le côté de la rue

    Returns:
        list: Liste des bornes qui sont sur le côté donné
    """
    borne_list = []
    for borne in inventaire:
        if borne['Cote'] == cote:
            borne_list.append(borne)

    return borne_list


def selectionner_borne_par_numero(inventaire, numero_borne):
    """
       Sélectionne une borne par son numéro.

       Args:
           inventaire (list): La liste des bornes de l'inventaire
           numero_borne (int): Numéro de la borne

       Returns:
           dict: Un dictionnaire contenant l'information de la borne avec le numéro donné.
                 Si le numéro de borne n'existe pas dans l'inventaire, retourner
                 le dictionnaire {'Numero': -1}.
       """
    borne = {}
    for i in range(len(inventaire)):
        if inventaire[i]['Numero'] == numero_borne:
            return inventaire[i]

    borne['Numero'] = -1
    return borne


def calculer_distance_bornes(borne_1, borne_2):
    """
    Calcule la distance en kilomètre entre deux bornes.

    Note: Pour calculer la distance approximative à partir des coordonnées géographique de la région de Québec,
    il faut d'abord multiplier la distance entre les degrés de lattitude par 110.6 km/degré et la distance entre
    les degrés de longitude par 78.85 km/degré (cette dernière quantité varie selon la distance de l'équateur).

    Args:
        borne_1 (dict): Une première borne
        borne_2 (dict): Une deuxième borne

    Returns:
        float: La distance entre les deux bornes en kilomètres
    """
    latittude_borne_1 = 110.6 * borne_1['Coordonnees'][0]
    latittude_borne_2 = 110.6 * borne_2['Coordonnees'][0]
    longitude_borne_1 = 78.85 * borne_1['Coordonnees'][1]
    longitude_borne_2 = 78.85 * borne_2['Coordonnees'][1]
    distance = math.sqrt((latittude_borne_2 - latittude_borne_1) * (latittude_borne_2 - latittude_borne_1) + (longitude_borne_2 - longitude_borne_1) * (longitude_borne_2 - longitude_borne_1))

    return distance


def trouver_borne_plus_pres(inventaire, numero_borne, autre_rue):
    """
    Trouve la borne dans l'inventaire qui est la plus près.

    Args:
        inventaire (list): La liste des bornes de l'inventaire
        numero_borne (int): Numéro de la borne pour laquelle on cherche la borne la plus proche
        autre_rue (bool): True si la borne retournée doit se trouver sur une autre rue, False sinon

    Returns:
        dict: Un dictionnaire contenant l'information de la borne la plus proche
    """
    borne_plus_pres = {}
    distance_minimale = float("inf")
    for i in range(nombre_de_bornes(inventaire)):
        if inventaire[i]['Numero'] == numero_borne:     # D'abord il faut trouver la borne don't le numero_borne à été donné
            for j in range(nombre_de_bornes(inventaire)):
                if i != j:  # Itérer à traver tous les autres bornes
                    if not autre_rue:   # Si on veut les bornes dans la même rue
                        if inventaire[i]['Rue'] == inventaire[j]['Rue']:
                            distance = calculer_distance_bornes(inventaire[i], inventaire[j])
                            if distance_minimale > distance:
                                distance_minimale = distance
                                borne_plus_pres = inventaire[j]
                    else:   # Si on veut les bornes des rues differents à celle don't le numero_borne à été donné
                        if inventaire[i]['Rue'] != inventaire[j]['Rue']:
                            distance = calculer_distance_bornes(inventaire[i], inventaire[j])
                            if distance_minimale > distance:
                                distance_minimale = distance
                                borne_plus_pres = inventaire[j]

    return borne_plus_pres


def trouver_bornes_plus_eloignees(inventaire):
    """
    Trouve les deux bornes les plus éloignées géographiquement parmi l'inventaire.

    Args:
        inventaire (list): La liste des bornes de l'inventaire

    Returns:
        tuple: Les deux dictionnaires contenant l'information des bornes les plus éloignées
    """
    bornes_plus_eloignees = ()
    distance_maximale = calculer_distance_bornes(inventaire[0], inventaire[1]) # point de départ pour les distances a comparer
    for i in range(nombre_de_bornes(inventaire)):   # comparer chaque borne avec toutes les autres
        for j in range(i+1, nombre_de_bornes(inventaire)):
            distance = calculer_distance_bornes(inventaire[i], inventaire[j])
            if distance_maximale < distance:
                distance_maximale = distance
                bornes_plus_eloignees = (inventaire[i], inventaire[j])

    return bornes_plus_eloignees


def trouver_borne_centrale(inventaire):
    """ Trouve la borne «centrale», c-a-d celle dont la moyenne des distances avec toutes les autres bornes de
    l'inventaire est minimale.

    Args:
        inventaire (list): La liste des bornes de l'inventaire

    Returns:
        dict: Dictionnaire contenant l'information de la borne centrale
    """
    borne_centrale = {}
    borne_1, borne_2 = trouver_bornes_plus_eloignees(inventaire)    # tuple unpacking
    distance_moyenne_minimale = calculer_distance_bornes(borne_1, borne_2)  # point de départ la distance maximale
    for i in range(nombre_de_bornes(inventaire)):
        distance_moyenne = 0.0
        for j in range(nombre_de_bornes(inventaire)):
            if i != j:
                distance = calculer_distance_bornes(inventaire[i], inventaire[j])
                distance_moyenne += distance
        distance_moyenne /= nombre_de_bornes(inventaire)
        if distance_moyenne < distance_moyenne_minimale:
            distance_moyenne_minimale = distance_moyenne
            borne_centrale = inventaire[i]

    return borne_centrale


def ajouter_borne(inventaire, borne):
    """
    Ajoute une borne à l'inventaire.

    Args:
        inventaire (list): La liste des bornes de l'inventaire
        borne (dict): Dictionnaire contenant l'information de la borne à ajouter à l'inventaire

    Returns:
        bool: True si la borne a été ajoutée à l'inventaire, False si le numéro de borne existait déjà.
    """
    ajouter = True
    for i in range(len(inventaire)):
        if borne['Numero'] == inventaire[i]['Numero']:
            ajouter = False

    if ajouter:
        inventaire.append(borne)
        return ajouter
    else:
        return ajouter


def retirer_borne(inventaire, numero_borne):
    """
    Retire une borne de l'inventaire.

    Args:
        inventaire (list): La liste des bornes de l'inventaire
        numero_borne (int): Numéro de la borne à retirer de l'inventaire

    Returns:
        bool: True si la borne a été retirée de l'inventaire, False si le numéro de borne n'existait pas.
    """
    retirer = False
    index_borne_retirer = len(inventaire)   # Assurer que index part avec une valeur dehors la plage de valeurs possibles
    for i in range(len(inventaire)):
        if inventaire[i]['Numero'] == numero_borne:
            retirer = True
            index_borne_retirer = i

    if retirer:
        del inventaire[index_borne_retirer]
        return retirer
    else:
        return retirer



if __name__ == '__main__':
    print('Exécution des tests...')
    print('-----------------------')
    inventaire = lire_fichier_bornes('vdq-bornestationnement.txt')
    # for borne in inventaire:
    #     print(borne)
    # print(len(inventaire))

    borne_test = creer_borne(4, 'N', 'Ruelle Rouge', -71.23, 46.82)
    assert borne_test == {'Numero': 4, 'Cote': 'N', 'Rue': 'Ruelle Rouge', 'Coordonnees': (46.82, -71.23)}
    print('creer_borne: OK')

    inventaire_reduit = lire_fichier_bornes("vdq-bornestationnement-reduit.txt")
    # for borne in inventaire_reduit:
    #     print(borne)
    # print(len(inventaire_reduit))

    # creer_borne_avec_chaine TEST
    assert creer_borne_avec_chaine("300219,3170,E,101189,Rue Caron,-71.2275177088525,46.81163827847973") == {'Numero': 3170, 'Cote': 'E', 'Rue': 'Rue Caron', 'Coordonnees': (46.81163827847973, -71.2275177088525)}
    assert creer_borne_avec_chaine("") == {}
    assert creer_borne_avec_chaine("0,0,0,0,0,0,0") == {'Numero': 0, 'Cote': '0', 'Rue': '0', 'Coordonnees': (0,0)}

    # lire_fichier_bornes TEST
    assert isinstance(inventaire_reduit, list)
    assert len(lire_fichier_bornes("vdq-bornestationnement-reduit.txt")) == 5
    assert isinstance(lire_fichier_bornes('vdq-bornestationnement.txt')[5], dict)
    # tester si le fichier est invalide

    # nombre_de_bornes TEST
    assert nombre_de_bornes(inventaire) == len(inventaire)
    assert nombre_de_bornes(inventaire_reduit) == len(inventaire_reduit)
    assert isinstance(nombre_de_bornes(inventaire), int)

    # selectionner_bornes_par_rue TEST
    bornes_par_rue = selectionner_bornes_par_rue(inventaire_reduit, 'Boulevard Charest Est')
    assert bornes_par_rue[0]['Numero'] == 3008
    assert bornes_par_rue[1]['Numero'] == 3060
    assert len(bornes_par_rue) == 2

    # selectionner_bornes_par_cote TEST
    assert selectionner_bornes_par_cote(inventaire_reduit, 'E')[0]['Numero'] == 4083
    assert selectionner_bornes_par_cote(inventaire_reduit, 'E')[1]['Numero'] == 3170
    assert selectionner_bornes_par_cote(inventaire_reduit, 'S')[1]['Numero'] == 3008

    # selectionner_borne_par_numero TEST
    borne_par_numero = selectionner_borne_par_numero(inventaire_reduit, 3170)
    assert borne_par_numero == {'Numero': 3170, 'Cote': 'E', 'Rue': 'Rue Caron', 'Coordonnees': (46.81163827847973, -71.2275177088525)}
    borne_par_numero = selectionner_borne_par_numero(inventaire_reduit, 3060)
    assert borne_par_numero == {'Numero': 3060, 'Cote': 'N', 'Rue': 'Boulevard Charest Est', 'Coordonnees': (46.8141394906634, -71.22296230536146)}
    assert selectionner_borne_par_numero(inventaire_reduit, 0)['Numero'] == -1

    # calculer_distance_bornes TEST
    distance = calculer_distance_bornes(inventaire_reduit[3], inventaire_reduit[4])
    assert f'{distance:.3f}' == '0.453'
    assert calculer_distance_bornes(inventaire_reduit[3], inventaire_reduit[4]) == calculer_distance_bornes(inventaire_reduit[4], inventaire_reduit[3])
    distance = calculer_distance_bornes(inventaire[0], inventaire[nombre_de_bornes(inventaire) - 1])
    #print(distance)
    assert calculer_distance_bornes(inventaire[0], inventaire[nombre_de_bornes(inventaire) - 1]) != 0

    # trouver_borne_plus_pres TEST
    assert trouver_borne_plus_pres(inventaire_reduit, 3060, False)['Numero'] == 3008
    assert trouver_borne_plus_pres(inventaire_reduit, 3060, True)['Numero'] == 3170
    time_start = perf_counter()
    borne_plus_pres = trouver_borne_plus_pres(inventaire, 4062, True)
    # print(borne_plus_pres)
    time_end = perf_counter()
    time_duration = time_end - time_start
    print("Temps d'execution trouver_borne_plus_pres(inventaire, 4062, True): ", time_duration)
    assert trouver_borne_plus_pres(inventaire, 4060, False) == {'Numero': 4061, 'Cote': 'N', 'Rue': "Rue De L'Espinay", 'Coordonnees': (46.827747332523316, -71.23588622493276)}

    # trouver_bornes_plus_eloignees TEST
    assert trouver_bornes_plus_eloignees(inventaire_reduit) == (inventaire_reduit[0], inventaire_reduit[4])
    borne1 = selectionner_borne_par_numero(inventaire_reduit, 3170)
    borne2 = selectionner_borne_par_numero(inventaire_reduit, 4034)
    assert trouver_bornes_plus_eloignees(inventaire_reduit) == (borne2, borne1)
    # borne1, borne2 = trouver_bornes_plus_eloignees(inventaire)
    # print(borne1, borne2)
    time_start = perf_counter()
    assert trouver_bornes_plus_eloignees(inventaire) == ({'Numero': 4140, 'Cote': 'N', 'Rue': 'Boulevard Sainte-Anne', 'Coordonnees': (46.84520539397195, -71.21370767822152)}, {'Numero': 6111, 'Cote': 'O', 'Rue': 'Avenue Maguire', 'Coordonnees': (46.779296353862875, -71.25043521119333)})
    time_end = perf_counter()
    time_duration = time_end - time_start
    print("Temps d'execution trouver_bornes_plus_eloignees(inventaire): ", time_duration)

    # trouver_borne_centrale  TEST
    assert trouver_borne_centrale(inventaire_reduit) == inventaire_reduit[2]
    assert trouver_borne_centrale(inventaire_reduit) == {'Numero': 3008, 'Cote': 'S', 'Rue': 'Boulevard Charest Est', 'Coordonnees': (46.812700620681355, -71.22626380380918)}
    # borne_centrale = trouver_borne_centrale(inventaire)
    # print(borne_centrale)
    time_start = perf_counter()
    assert trouver_borne_centrale(inventaire) != {}
    time_end = perf_counter()
    time_duration = time_end - time_start
    print("Temps d'execution trouver_borne_centrale(inventaire): ", time_duration)

    # ajouter_borne TEST
    # print("ajouter", ajouter_borne(inventaire_reduit, borne_test))
    assert ajouter_borne(inventaire_reduit, borne_test) == True
    assert ajouter_borne(inventaire_reduit, borne_test) == False
    assert ajouter_borne(inventaire, creer_borne(4030,'S','Boulevard Cardinal-Villeneuve',-71.23596889800088,46.828783759871975)) == False
    # for borne in inventaire_reduit:
    #     print(borne)
    # print("--- "*10)

    # retirer_borne TEST
    # print("retirer:", retirer_borne(inventaire_reduit, 4))
    assert retirer_borne(inventaire_reduit, 4) == True
    assert retirer_borne(inventaire_reduit, 4) == False
    assert retirer_borne(inventaire, 25) == False
    # for borne in inventaire_reduit:
    #     print(borne)

    ###############################
    print("Tous les tests ok!!!")
    ###############################




