from __future__ import annotations
from typing import Iterator, Optional
from case import Case

class ListeDeCases:
    class Noeud:
        def __init__(self, case: Case, suivant: Optional[ListeDeCases.Noeud] = None,
                     precedent: Optional[ListeDeCases.Noeud] = None):
            self.case = case
            self.suivant = suivant
            self.precedent = precedent
    
    def __init__(self) -> None:
        self._debut: Optional[ListeDeCases.Noeud] = None
        self._fin: Optional[ListeDeCases.Noeud] = None
        self._taille: int = 0

    def taille(self) -> int:
        return self._taille
    
    def est_vide(self) -> bool:
        return self._taille == 0
    
    def ajouter_case(self, case: Case, position: int) -> None:
        if position < 1 or position > self._taille + 1:
            raise IndexError("AjouterCase: positon invalide")
        nouveau = ListeDeCases.Noeud(case)
        if position == 1:
            nouveau.suivant = self._debut
            if self._debut:
                self._debut.precedent = nouveau
            self._debut = nouveau
            if not self._fin:
                self._fin = nouveau
        elif position == self._taille + 1:
            nouveau.precedent = self._fin
            if self._fin:
                self._fin.suivant = nouveau
            self._fin = nouveau
            if not self._debut:
                self._debut = nouveau
        else:
            courant = self._noeud_at(position)
            nouveau.suivant = courant
            nouveau.precedent = courant.precedent
            if courant.precedent:
                courant.precedent.suivant = nouveau
            courant.precedent = nouveau
        self._taille += 1
    
    def ajouter_case_a_la_fin(self, case: Case) -> None:
        self.ajouter_case(case, self._taille + 1)

    def enlever_case(self, position: int) -> None:
        if self.est_vide():
            raise ValueError("enleverCase: ListeDeCases est vide")
        if position < 1 or position > self._taille:
            raise IndexError("enleverCase: position invalide")
        courant = self._noeud_at(position)
        if courant == self._debut:
            self._debut = courant.suivant
            if self._debut:
                self._debut.precedent = None
        else:
            courant.precedent.suivant = courant.suivant
        if courant == self._fin:
            self._fin = courant.precedent
            if self._fin:
                self._fin.suivant = None
        else:
            courant.suivant.precedent = courant.precedent
        self._taille -= 1

    def case_a(self, position: int) -> Case:
        return self._noeud_at(position).case

    def _noeud_at(self, position: int) -> ListeDeCases.Noeud:
        if position < 1 or position > self._taille:
            raise IndexError("noeudAt: position invalide")
        noeud = self._debut
        for _ in range(position - 1):
            noeud = noeud.suivant  # type: ignore
        return noeud  # type: ignore

    class Iterateur:
        def __init__(self, liste: ListeDeCases) -> None:
            self._liste = liste
            self._courant: Optional[ListeDeCases.Noeud] = liste._debut

        def case_courante(self) -> Case:
            if not self._courant:
                raise ValueError("Iterateur: Fin de liste atteinte")
            return self._courant.case

        def existe_case_suivante(self) -> bool:
            return self._courant is not None and self._courant.suivant is not None

        def __next__(self) -> Case:
            if self.existe_case_suivante():
                self._courant = self._courant.suivant
                return self.case_courante()
            else:
                raise StopIteration("L'iterateur ne peut pas aller à une case suivante.")

        def case_suivante(self, couleur: Case.Couleur) -> None:
            noeud = self._noeud_suivant(couleur)
            if noeud is None:
                raise ValueError(f"L'iterateur ne peut pas aller à une case suivante de couleur {couleur.name}.")
            self._courant = noeud

        def existe_case_suivante_couleur(self, couleur: Case.Couleur) -> bool:
            return self._noeud_suivant(couleur) is not None

        def _noeud_suivant(self, couleur: Case.Couleur) -> Optional[ListeDeCases.Noeud]:
            courant = self._courant.suivant if self._courant else None
            while courant and courant.case.couleur != couleur:
                courant = courant.suivant
            return courant

        def case_precedente(self, couleur: Case.Couleur) -> None:
            noeud = self._noeud_precedent(couleur)
            if noeud is None:
                raise ValueError(f"L'iterateur ne peut pas aller à une case précédente de couleur {couleur.name}.")
            self._courant = noeud

        def existe_case_precedente(self, couleur: Case.Couleur) -> bool:
            return self._noeud_precedent(couleur) is not None

        def _noeud_precedent(self, couleur: Case.Couleur) -> Optional[ListeDeCases.Noeud]:
            courant = self._courant.precedent if self._courant else None
            while courant and courant.case.couleur != couleur:
                courant = courant.precedent
            return courant

        def position_courante(self) -> int:
            courant = self._liste._debut
            if courant is None:
                raise ValueError("positionCourante: La liste est vide")

            index = 1
            while courant and courant != self._courant:
                courant = courant.suivant
                index += 1
            return index

        def est_a_derniere_case(self) -> bool:
            return self._courant is not None and self._courant == self._liste._fin

        def __iter__(self) -> Iterator[Case]:
            while self._courant:
                yield self._courant.case
                self._courant = self._courant.suivant

    def __str__(self) -> str:
        elements = []
        iterateur = self.debut()
        while not iterateur.est_a_derniere_case():
            elements.append(str(iterateur.case_courante()))
            iterateur.__next__()
        elements.append(str(iterateur.case_courante()))
        return "; ".join(elements) if elements else "Liste de cases vide"
    
    def debut(self) -> Iterateur:
        return ListeDeCases.Iterateur(self)
    
if __name__ == '__main__':
    mylist: ListeDeCases = ListeDeCases()
    case1: Case = Case()
    mylist.ajouter_case(case1, 1)
    print(case1)
    print(case1.__str__())
    print(mylist)
    print(mylist.__str__())
    case2 = Case(Case.Couleur.Rouge, Case.Decoration.Serpent)
    mylist.ajouter_case_a_la_fin(case2)
    print(mylist)
    case3 = Case(Case.Couleur.Jaune, Case.Decoration.Echelle)
    mylist.ajouter_case(case3, 2)
    print(mylist)
    print(mylist.case_a(2))
    myIter = mylist.debut()
    print(myIter.case_courante())
    print(myIter.existe_case_suivante())
    print(myIter.position_courante())
    print(myIter.__next__())
    print(myIter.position_courante())
    print(myIter.existe_case_suivante_couleur(Case.Couleur.Rouge))
    myIter.case_suivante(Case.Couleur.Rouge)
    print(myIter.position_courante())
    print(myIter.est_a_derniere_case())
    print(myIter.existe_case_precedente(Case.Couleur.Bleu))
    myIter.case_precedente(Case.Couleur.Bleu)
    print(myIter.position_courante())
    mylist.enlever_case(2)
    print(mylist)
    mylist.enlever_case(2)
    print(mylist)
    mylist.enlever_case(1)

