#!/usr/bin/env python3
"""Localise l'installation d'ARK, quelle que soit la machine.

Le chemin du jeu etait ecrit en dur dans quatre fichiers, ce qui liait tout le
projet a une seule machine. Il se resout maintenant ici, dans cet ordre :

  1. la variable d'environnement ARK_ASA, qui a toujours le dernier mot ;
  2. les emplacements usuels d'une bibliotheque Steam.

Le suffixe des paks depend de l'edition installee : `-Windows` pour le client,
`-WindowsServer` pour le serveur dedie. Les deux conviennent, le locres y est
rigoureusement identique (verifie : memes 34 687 chaines FR et 39 201 EN, meme
empreinte). Un serveur dedie suffit donc a construire le patch, ce qui permet
de travailler sans le jeu complet, 1,5 Go au lieu de 212.

    python3 tools/chemins.py      # montre ce qui a ete trouve
"""
import glob
import os
import sys

CANDIDATS = (
    "/mnt/Apps/SteamLibrary/steamapps/common/ARK Survival Ascended",
    "~/.steam/steam/steamapps/common/ARK Survival Ascended",
    "~/.local/share/Steam/steamapps/common/ARK Survival Ascended",
    "/mnt/*/SteamLibrary/steamapps/common/ARK Survival Ascended",
    "~/*/SteamLibrary/steamapps/common/ARK Survival Ascended",
    # serveur dedie : l'arborescence de POK-manager, puis celle de SteamCMD
    "~pokuser/asa_server/ServerFiles/arkserver",
    "/home/*/asa_server/ServerFiles/arkserver",
    "~/.local/share/Steam/steamapps/common/ARK Survival Ascended Dedicated Server",
)


def racine_jeu():
    """Dossier d'installation d'ARK, ou None s'il n'y en a aucun de lisible."""
    env = os.environ.get("ARK_ASA")
    if env:
        return env if os.path.isdir(env) else None
    for motif in CANDIDATS:
        for chemin in sorted(glob.glob(os.path.expanduser(motif))):
            if os.path.isdir(os.path.join(chemin, "ShooterGame/Content/Paks")):
                return chemin
    return None


def paks():
    """Dossier des paks du jeu. Leve une erreur parlante s'il est introuvable."""
    racine = racine_jeu()
    if not racine:
        raise SystemExit(
            "ARK introuvable. Indiquez le dossier d'installation dans la "
            "variable ARK_ASA (client ou serveur dedie, les deux conviennent).")
    return os.path.join(racine, "ShooterGame/Content/Paks")


def chunk0(extension="pak"):
    """pakchunk0 du jeu, suffixe client ou serveur selon ce qui est installe."""
    dossier = paks()
    trouves = glob.glob(os.path.join(dossier, f"pakchunk0-Windows*.{extension}"))
    if not trouves:
        raise SystemExit(f"pakchunk0-Windows*.{extension} absent de {dossier}")
    # le client d'abord : son nom est le plus court, et c'est l'edition de
    # reference puisque c'est elle qui affiche le patch
    return sorted(trouves, key=len)[0]


def serveur_dedie():
    """Vrai si l'installation trouvee est un serveur dedie, pas le client.

    Un serveur dedie sert a construire et a verifier, jamais a installer : y
    deposer le pak modifierait un serveur de jeu en production.
    """
    return "WindowsServer" in os.path.basename(chunk0())


def main():
    racine = racine_jeu()
    if not racine:
        print("ARK introuvable (definir ARK_ASA)")
        return 1
    print(f"  jeu       : {racine}")
    print(f"  pakchunk0 : {os.path.basename(chunk0())}")
    print(f"  edition   : {'serveur dedie' if serveur_dedie() else 'client'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
