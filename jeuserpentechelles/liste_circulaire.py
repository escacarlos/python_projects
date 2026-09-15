from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class Noeud(Generic[T]):
    def __init__(self, element: T, suivant: Optional["Noeud[T]"] = None):
        self.element = element
        self.suivant = suivant if suivant else self  # Circular reference for a single node

    def __deepcopy__(self, memo):
            from copy import deepcopy
            if id(self) in memo:
                return memo[id(self)]
            copied = Noeud(deepcopy(self.element, memo))
            memo[id(self)] = copied
            # Do not copy self.suivant here — handled in ListeCirculaire to avoid infinite recursion
            return copied

class ListeCirculaire(Generic[T]):
    def __init__(self):
        self.dernier: Optional[Noeud[T]] = None

    def __init__(self, source: Optional["ListeCirculaire[T]"] = None):
        self.dernier: Optional[Noeud[T]] = None
        if source is not None:
            self.copyOf(source)

    def __del__(self):
        self._clear()

    def __deepcopy__(self, memo):
        # if Noeud is not deepcopied then use this:
        # copied = ListeCirculaire()
        # memo[id(self)] = copied
        # copied.copyOf(self)
        # return copied
        from copy import deepcopy

        if id(self) in memo:
            return memo[id(self)]

        copied = ListeCirculaire()
        memo[id(self)] = copied

        if self.dernier is None:
            return copied

        try:
            copied.dernier = deepcopy(self.dernier, memo)
            nouveau = copied.dernier
            courant = self.dernier.suivant

            while courant != self.dernier:
                nouveau.suivant = deepcopy(courant, memo)
                nouveau = nouveau.suivant
                courant = courant.suivant

            nouveau.suivant = copied.dernier
        except Exception:
            copied._clear()
            raise

        return copied
    
    def copyOf(self, source: "ListeCirculaire[T]"):
        """Copies the circular linked list from `source`."""
        self._clear()
        if source.dernier is None:
            self.dernier = None
        else:
            try:
                self.dernier = Noeud(source.dernier.element)
                nouveau = self.dernier
                temp = source.dernier.suivant
                while temp != source.dernier:
                    nouveau.suivant = Noeud(temp.element)
                    nouveau = nouveau.suivant
                    temp = temp.suivant
                nouveau.suivant = self.dernier
            except Exception:
                self._clear()
                raise    

    def _clear(self):
        if self.dernier:
            courant = self.dernier.suivant
            while courant != self.dernier:
                suivant = courant.suivant
                del courant
                courant = suivant
            del self.dernier
        self.dernier = None

    def ajouter(self, element: T, position: int):
        if position < 1 or position > self.taille() + 1:
            raise IndexError("Ajouter: Position d'ajout erronée")

        nouveau = Noeud(element)

        if not self.dernier:
            self.dernier = nouveau
            return

        if position == 1:
            nouveau.suivant = self.dernier.suivant
            self.dernier.suivant = nouveau
        elif position == self.taille() + 1:
            nouveau.suivant = self.dernier.suivant
            self.dernier.suivant = nouveau
            self.dernier = nouveau
        else:
            courant = self.dernier.suivant
            for _ in range(position - 2):
                courant = courant.suivant
            nouveau.suivant = courant.suivant
            courant.suivant = nouveau

    def ajouter_fin(self, element: T):
        self.ajouter(element, self.taille() + 1)

    def enlever_el(self, element: T):
        if not self.dernier:
            raise ValueError("EnleverEl: L'élément à enlever n'est pas présent (liste vide!)")

        courant = self.dernier.suivant
        precedent = self.dernier

        while courant != self.dernier and courant.element != element:
            precedent = courant
            courant = courant.suivant

        if courant.element != element:
            raise ValueError("EnleverEl: L'élément à enlever n'est pas présent")

        precedent.suivant = courant.suivant

        if courant == self.dernier:
            self.dernier = precedent if precedent != courant else None

        del courant

    def enlever_pos(self, position: int):
        if position < 1 or position > self.taille():
            raise IndexError("EnleverPos: Position pour l'enlèvement est erronée")

        courant = self.dernier.suivant
        precedent = self.dernier

        if position == 1:
            if courant == self.dernier:
                self.dernier = None
            else:
                self.dernier.suivant = courant.suivant
        else:
            for _ in range(position - 1):
                precedent = courant
                courant = courant.suivant
            precedent.suivant = courant.suivant
            if courant == self.dernier:
                self.dernier = precedent

        del courant

    def taille(self) -> int:
        if not self.dernier:
            return 0
        compteur = 1
        courant = self.dernier.suivant
        while courant != self.dernier:
            compteur += 1
            courant = courant.suivant
        return compteur

    def est_vide(self) -> bool:
        return self.dernier is None

    def appartient(self, element: T) -> bool:
        if not self.dernier:
            return False
        courant = self.dernier.suivant
        while courant != self.dernier:
            if courant.element == element:
                return True
            courant = courant.suivant
        return self.dernier.element == element

    def element(self, position: int) -> T:
        if position < 1 or position > self.taille():
            raise IndexError("Element: Position erronée")

        courant = self.dernier.suivant
        for _ in range(position - 1):
            courant = courant.suivant
        return courant.element

    def position(self, element: T) -> int:
        if not self.dernier:
            raise ValueError("Position: L'élément recherché n'est pas dans la liste (liste vide!)")

        courant = self.dernier.suivant
        pos = 1
        while courant != self.dernier and courant.element != element:
            courant = courant.suivant
            pos += 1
        if courant.element == element:
            return pos
        raise ValueError("Position: L'élément recherché n'est pas dans la liste")

    def __str__(self) -> str:
        if not self.dernier:
            return "Liste vide"

        elements = []
        courant = self.dernier.suivant
        while courant != self.dernier:
            elements.append(str(courant.element))
            courant = courant.suivant
        elements.append(str(self.dernier.element))

        return "; ".join(elements)
    
if __name__ == '__main__':
    from case import Case
    cirList = ListeCirculaire()
    cirList.ajouter(Case.Couleur.Bleu, 1)
    cirList.ajouter(Case.Couleur.Rouge, 1)
    cirList.ajouter_fin(Case.Couleur.Jaune)
    print(cirList)
    print(cirList.taille())
    print(cirList.est_vide())
    print(cirList.appartient(Case.Couleur.Rouge))
    print(cirList.element(3))
    print(cirList.position(Case.Couleur.Rouge))
    cirList1 = ListeCirculaire()
    cirList1.copyOf(cirList)
    copie = ListeCirculaire(cirList1)
    cirList.enlever_el(Case.Couleur.Rouge)
    print(cirList)
    print(cirList1)
    cirList.enlever_pos(2)
    print(cirList)
    print(cirList1)
    print(copie)
    from copy import deepcopy
    liste = ListeCirculaire()
    liste.ajouter(["A"], 1)
    liste.ajouter(["B"], 2)

    copie = deepcopy(liste)

    # Mutate the copy
    copie.element(1).append("mutated")

    print("Original:", liste)
    print("Copied:", copie)
