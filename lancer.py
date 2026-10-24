"""
Bensikin Roch — Motard d'honneur du Cameroun
Jeu de sécurité routière en pygame.

    pip install -r requirements.txt
    python lancer.py
"""

from bensikin.ecrans import App


def main() -> None:
    print("Bensikin Roch (pygame). Respecte la route : on te prime. Sinon, on te coupe.")
    App().boucle()


if __name__ == "__main__":
    main()

