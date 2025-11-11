"""
Module de support Unicode pour les agents NOVAQUOTE
Fournit des fonctions utilitaires pour gérer correctement l'encodage UTF-8
Évite les erreurs 'charmap' codec sur Windows
"""

import locale
import sys
from typing import Optional


def setup_unicode_support() -> bool:
    """
    Configure le système pour supporter correctement l'UTF-8

    Returns:
        bool: True si la configuration a réussi, False sinon
    """
    try:
        # Forcer l'encodage UTF-8 pour stdin/stdout/stderr
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
        if hasattr(sys.stdin, 'reconfigure'):
            sys.stdin.reconfigure(encoding='utf-8', errors='backslashreplace')

        # Définir les locales pour supporter l'UTF-8
        locale_configs = ['fr_FR.UTF-8', 'C.UTF-8', 'en_US.UTF-8', '']
        for locale_config in locale_configs:
            try:
                locale.setlocale(locale.LC_ALL, locale_config)
                if locale_config:
                    return True
                break
            except locale.Error:
                continue

        return True

    except Exception as e:
        # Silencer l'erreur pour ne pas bloquer le démarrage
        return False


def safe_print(text: str, color: Optional[str] = None, print_func=None, **kwargs) -> None:
    """
    Fonction d'impression sécurisée pour l'UTF-8

    Args:
        text: Le texte à imprimer
        color: Couleur optionnelle (si termcolor est disponible)
        print_func: Fonction d'impression personnalisée
        **kwargs: Arguments supplémentaires pour la fonction d'impression
    """
    try:
        if color and print_func:
            # Utiliser termcolor ou autre fonction colorée
            print_func(text, color, **kwargs)
        elif print_func:
            # Utiliser la fonction personnalisée sans couleur
            print_func(text, **kwargs)
        else:
            # Utiliser print standard
            print(text)

    except UnicodeEncodeError:
        # Fallback: remplacer les caractères non supportés
        safe_text = text.encode('ascii', errors='replace').decode('ascii')
        if color and print_func:
            print_func(safe_text, color, **kwargs)
        elif print_func:
            print_func(safe_text, **kwargs)
        else:
            print(safe_text)

    except Exception as e:
        # Dernier recours: logger l'erreur sans le texte problématique
        error_msg = f"Erreur d'impression: {type(e).__name__}"
        try:
            print(error_msg)
        except:
            pass  # Échec silencieux


def create_safe_cprint(cprint_func):
    """
    Crée une fonction cprint sécurisée qui gère l'UTF-8

    Args:
        cprint_func: La fonction cprint de termcolor

    Returns:
        Fonction cprint sécurisée
    """
    def safe_cprint(text: str, color: str = None, **kwargs):
        safe_print(text, color, cprint_func, **kwargs)
    return safe_cprint


def get_utf8_subprocess_kwargs(base_kwargs: dict = None) -> dict:
    """
    Retourne les arguments par défaut pour subprocess.run avec support UTF-8

    Args:
        base_kwargs: Arguments de base à fusionner

    Returns:
        Dict avec les arguments UTF-8 configurés
    """
    utf8_kwargs = {
        'encoding': 'utf-8',
        'text': True,
        'errors': 'backslashreplace'
    }

    if base_kwargs:
        utf8_kwargs.update(base_kwargs)

    return utf8_kwargs


# Configurer automatiquement le support UTF-8 au import
_setup_success = setup_unicode_support()