class GenerateurNombresAleatoires:
    ENTROPIE: int = 16807  # Static constant

    def __init__(self, init: int = 1, max_val: int = 2_000_000_000) -> None:
        """Initialise le générateur avec une valeur de départ et une borne max."""
        self.m_etat: int = init
        self.m_maxPlusUn: int = max_val + 1

    def pige(self) -> int:
        """Génère un nombre pseudo-aléatoire."""
        self.m_etat *= self.ENTROPIE
        return self.m_etat % self.m_maxPlusUn