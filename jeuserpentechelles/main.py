from generateur_aleatoire_jeu_serpents_echelles import GenerateurAleatoireJeuSerpentsEtEchelles
from jeu_serpent_et_echelles import JeuSerpentsEtEchelles

def main() -> None:
    jeu: JeuSerpentsEtEchelles = JeuSerpentsEtEchelles()

    print("Jeu 1:")
    generateur_jeu: GenerateurAleatoireJeuSerpentsEtEchelles = GenerateurAleatoireJeuSerpentsEtEchelles(1)
    generateur_jeu.generer(jeu, 5, 9, 2)
    jeu.affiche_resultats(jeu.jouer(100))

    print("\nJeu 2:")
    generateur_jeu.generer(jeu, 5, 9, 2)
    jeu.affiche_resultats(jeu.jouer(100))

    print("\nJeu 3:")
    generateur_jeu_2: GenerateurAleatoireJeuSerpentsEtEchelles = GenerateurAleatoireJeuSerpentsEtEchelles(9569686)
    generateur_jeu_2.generer(jeu, 243, 53, 4)
    jeu.affiche_resultats(jeu.jouer(20000))

    print("\nJeu 4:")
    generateur_jeu_2.generer(jeu, 243, 53, 4)
    jeu.affiche_resultats(jeu.jouer(20000))

if __name__ == "__main__":
    main()
