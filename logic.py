import os
import re

# ════════════════════════════════════════════════════════════════
#  TABLE DE HACHAGE FAITE MAIN
#  Remplace les dictionnaires Python {} utilisés dans le projet.
#  Implémente : insertion, recherche, suppression, itération.
# ════════════════════════════════════════════════════════════════

class MaTableHachage:
    """
    Table de hachage codée manuellement avec gestion des collisions
    par chaînage (chaque case du tableau contient une liste de paires
    clé-valeur).

    Capacité par défaut : 64 cases.
    Facteur de charge : si (nb_elements / capacite) > 0.75, on double
    la taille et on re-hache tout (rehashing).
    """

    CAPACITE_DEFAUT = 64        # Nombre de cases initiales du tableau
    FACTEUR_CHARGE  = 0.75      # Seuil déclenchant le rehashing


    def __init__(self, capacite=None):
        # On utilise la capacité fournie ou la valeur par défaut
        self._capacite    = capacite if capacite else self.CAPACITE_DEFAUT
        # Le tableau interne : chaque case est une liste (chaînage)
        self._tableau     = [[] for _ in range(self._capacite)]
        self._nb_elements = 0   # Compteur d'éléments (pour le facteur de charge)


    # ────────────────────────────────────────────────
    #  FONCTION DE HACHAGE
    # ────────────────────────────────────────────────

    def _hacher(self, cle):
        """
        Calcule l'indice dans le tableau pour une clé (chaîne de caractères).
        Algorithme : somme pondérée des codes Unicode de chaque caractère,
        multipliée par un premier (31) pour réduire les collisions.
        Résultat : indice entre 0 et (capacité - 1).
        """
        valeur = 0
        for caractere in cle:
            # ord() donne le code Unicode du caractère
            valeur = valeur * 31 + ord(caractere)
        # On prend le modulo pour rester dans les bornes du tableau
        return valeur % self._capacite


    # ────────────────────────────────────────────────
    #  INSERTION  /  MISE À JOUR
    # ────────────────────────────────────────────────

    def __setitem__(self, cle, valeur):
        """
        Insère ou met à jour la paire (cle, valeur).
        Syntaxe identique aux dicts Python : table[cle] = valeur
        """
        indice = self._hacher(cle)
        seau   = self._tableau[indice]   # La liste à cet indice

        # Parcourt la liste pour voir si la clé existe déjà
        for i, (k, v) in enumerate(seau):
            if k == cle:
                seau[i] = (cle, valeur)  # Mise à jour de la valeur
                return

        # Clé absente → on ajoute la paire
        seau.append((cle, valeur))
        self._nb_elements += 1

        # Vérifie si on dépasse le facteur de charge
        if self._nb_elements / self._capacite > self.FACTEUR_CHARGE:
            self._rehacher()


    # ────────────────────────────────────────────────
    #  LECTURE
    # ────────────────────────────────────────────────

    def __getitem__(self, cle):
        """
        Retourne la valeur associée à la clé.
        Lève KeyError si la clé est absente (comportement identique aux dicts).
        Syntaxe : valeur = table[cle]
        """
        indice = self._hacher(cle)
        for k, v in self._tableau[indice]:
            if k == cle:
                return v
        raise KeyError(cle)


    def get(self, cle, defaut=None):
        """
        Retourne la valeur ou `defaut` si la clé est absente.
        Équivalent de dict.get(cle, defaut).
        """
        try:
            return self[cle]
        except KeyError:
            return defaut


    # ────────────────────────────────────────────────
    #  TEST D'APPARTENANCE
    # ────────────────────────────────────────────────

    def __contains__(self, cle):
        """
        Permet d'écrire :  if cle in table
        Retourne True si la clé est présente, False sinon.
        """
        indice = self._hacher(cle)
        for k, v in self._tableau[indice]:
            if k == cle:
                return True
        return False


    # ────────────────────────────────────────────────
    #  SUPPRESSION
    # ────────────────────────────────────────────────

    def __delitem__(self, cle):
        """
        Supprime la paire associée à la clé.
        Lève KeyError si absente.
        Syntaxe : del table[cle]
        """
        indice = self._hacher(cle)
        seau   = self._tableau[indice]
        for i, (k, v) in enumerate(seau):
            if k == cle:
                seau.pop(i)
                self._nb_elements -= 1
                return
        raise KeyError(cle)


    # ────────────────────────────────────────────────
    #  ITÉRATION (clés, valeurs, paires)
    # ────────────────────────────────────────────────

    def __iter__(self):
        """
        Itère sur les clés.
        Permet :  for cle in table
        """
        for seau in self._tableau:
            for k, v in seau:
                yield k


    def items(self):
        """
        Itère sur les paires (clé, valeur).
        Permet :  for cle, valeur in table.items()
        """
        for seau in self._tableau:
            for k, v in seau:
                yield k, v


    def values(self):
        """
        Itère sur les valeurs uniquement.
        Permet :  for valeur in table.values()
        """
        for seau in self._tableau:
            for k, v in seau:
                yield v


    # ────────────────────────────────────────────────
    #  TAILLE
    # ────────────────────────────────────────────────

    def __len__(self):
        """Retourne le nombre d'éléments stockés."""
        return self._nb_elements


    # ────────────────────────────────────────────────
    #  REHASHING (agrandissement automatique)
    # ────────────────────────────────────────────────

    def _rehacher(self):
        """
        Double la capacité du tableau et re-insère tous les éléments.
        Appelé automatiquement quand le facteur de charge est dépassé.
        Cela maintient des performances en O(1) amorti.
        """
        ancienne_capacite = self._capacite
        ancien_tableau    = self._tableau

        # Nouvelle capacité : double de l'ancienne
        self._capacite    = ancienne_capacite * 2
        self._tableau     = [[] for _ in range(self._capacite)]
        self._nb_elements = 0   # Sera recompté par __setitem__

        # Re-insère chaque paire dans le nouveau tableau
        for seau in ancien_tableau:
            for k, v in seau:
                self[k] = v


# ════════════════════════════════════════════════════════════════
#  FIN DE LA TABLE DE HACHAGE
# ════════════════════════════════════════════════════════════════


# ────────────────────────────────────────────────
# Fonctions auxiliaires pour remplacer max() et len()
# (interdites par la prof → on les code nous-mêmes)
# ────────────────────────────────────────────────

def mon_max(a, b):
    """Retourne le plus grand entre a et b sans utiliser max()"""
    if a > b:
        return a
    else:
        return b


def ma_longueur(chaine):
    """Compte le nombre de caractères sans utiliser len()"""
    compteur = 0
    for _ in chaine:
        compteur += 1
    return compteur


# Classe Node : un nœud de l'arbre AVL
class Node:
    def __init__(self, key):
        self.key          = key    # La racine trilitère (ex: "كتب")
        self.left         = None   # Fils gauche
        self.right        = None   # Fils droit
        self.height       = 1      # Hauteur du nœud (pour équilibrer)

        # ── CHANGEMENT : derived_words est maintenant une MaTableHachage
        #    au lieu d'un dict Python {}
        #    {mot: fréquence}  →  MaTableHachage mot → fréquence
        self.derived_words = MaTableHachage()


# Classe principale : moteur de morphologie arabe (SARF)
class SARF_Logic:
    def __init__(self):
        self.root_tree = None        # Racine de l'arbre AVL

        # ── CHANGEMENT : self.schemes est maintenant une MaTableHachage
        #    au lieu d'un dict Python {}
        #    {nom_schème: {"cat": catégorie}}  →  MaTableHachage
        self.schemes   = MaTableHachage()

        self.r_path = 'data/roots.txt'    # Fichier où on sauve les racines
        self.s_path = 'data/schemes.txt'  # Fichier où on sauve les schèmes


    # Vérifie si le texte est une racine arabe de 3 lettres
    def is_arabic_triple(self, text):
        return bool(re.match(r'^[\u0621-\u064A]{3}$', text))


    # Supprime tous les tashkīl (voyelles, shadda, sukūn...)
    def strip_tashkeel(self, text):
        if not text:
            return ""
        return re.sub(r'[\u064B-\u0652]', '', text)


    # ────────────────────────────────────────────────
    #        FONCTIONS DE L'ARBRE AVL (sans max ni len)
    # ────────────────────────────────────────────────

    def get_height(self, node):
        if node is None:
            return 0
        return node.height

    def get_balance(self, node):
        if node is None:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def _right_rotate(self, y):
        x  = y.left
        T2 = x.right
        x.right = y
        y.left  = T2
        y.height = 1 + mon_max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + mon_max(self.get_height(x.left), self.get_height(x.right))
        return x

    def _left_rotate(self, x):
        y  = x.right
        T2 = y.left
        y.left  = x
        x.right = T2
        x.height = 1 + mon_max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + mon_max(self.get_height(y.left), self.get_height(y.right))
        return y

    def insert_root(self, root, key):
        if root is None:
            return Node(key)
        if key < root.key:
            root.left = self.insert_root(root.left, key)
        elif key > root.key:
            root.right = self.insert_root(root.right, key)
        else:
            return root

        root.height = 1 + mon_max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1  and key < root.left.key:  return self._right_rotate(root)
        if balance < -1 and key > root.right.key: return self._left_rotate(root)
        if balance > 1  and key > root.left.key:
            root.left = self._left_rotate(root.left); return self._right_rotate(root)
        if balance < -1 and key < root.right.key:
            root.right = self._right_rotate(root.right); return self._left_rotate(root)

        return root

    def search_root(self, root, key):
        if root is None or root.key == key:
            return root
        if key < root.key:
            return self.search_root(root.left, key)
        return self.search_root(root.right, key)

    def delete_root(self, root, key):
        if root is None:
            return root
        if key < root.key:
            root.left = self.delete_root(root.left, key)
        elif key > root.key:
            root.right = self.delete_root(root.right, key)
        else:
            if root.left is None:  return root.right
            elif root.right is None: return root.left
            temp      = self._min_node(root.right)
            root.key  = temp.key
            root.right = self.delete_root(root.right, temp.key)

        if root is None:
            return root

        root.height = 1 + mon_max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1  and self.get_balance(root.left)  >= 0: return self._right_rotate(root)
        if balance > 1  and self.get_balance(root.left)  <  0:
            root.left = self._left_rotate(root.left); return self._right_rotate(root)
        if balance < -1 and self.get_balance(root.right) <= 0: return self._left_rotate(root)
        if balance < -1 and self.get_balance(root.right) >  0:
            root.right = self._right_rotate(root.right); return self._left_rotate(root)

        return root

    def _min_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current


    # ────────────────────────────────────────────────
    #     GÉNÉRATION ET ANALYSE MORPHOLOGIQUE
    # ────────────────────────────────────────────────

    def apply_scheme(self, root_word, scheme_name):
        if ma_longueur(root_word) != 3:
            return None
        root_word   = self.strip_tashkeel(root_word)
        scheme_name = self.strip_tashkeel(scheme_name)
        resultat = ""
        for lettre in scheme_name:
            if   lettre == 'ف': resultat += root_word[0]
            elif lettre == 'ع': resultat += root_word[1]
            elif lettre == 'ل': resultat += root_word[2]
            else:               resultat += lettre
        return resultat


    def populate_derivatives(self, root_key):
        noeud = self.search_root(self.root_tree, root_key)
        if noeud is None:
            return False

        # ── Itération sur self.schemes (MaTableHachage) : for schème in self.schemes
        #    fonctionne grâce à __iter__ qui yield les clés
        for schème in self.schemes:
            mot = self.apply_scheme(root_key, schème)
            if mot is not None and mot not in noeud.derived_words:
                # ── Insertion dans derived_words (MaTableHachage)
                noeud.derived_words[mot] = 0
        return True


    def identify_word(self, word):
        resultats   = []
        mot_nettoye = self.strip_tashkeel(word)

        # ── Itération sur self.schemes via __iter__
        for nom_schème in self.schemes:
            schème_nettoye = self.strip_tashkeel(nom_schème)

            if ma_longueur(mot_nettoye) != ma_longueur(schème_nettoye):
                continue

            r1 = r2 = r3 = None
            est_possible = True

            for i in range(ma_longueur(mot_nettoye)):
                lettre_mot   = mot_nettoye[i]
                lettre_schème = schème_nettoye[i]

                if   lettre_schème == 'ف': r1 = lettre_mot
                elif lettre_schème == 'ع': r2 = lettre_mot
                elif lettre_schème == 'ل': r3 = lettre_mot
                elif lettre_mot != lettre_schème:
                    est_possible = False
                    break

            if est_possible and r1 and r2 and r3:
                racine_candidate = r1 + r2 + r3
                if self.search_root(self.root_tree, racine_candidate):
                    resultats.append({
                        "root":   racine_candidate,
                        "scheme": nom_schème,
                        "word":   word
                    })

        return resultats


    # ────────────────────────────────────────────────
    #           GESTION DES أوزان (schèmes)
    # ────────────────────────────────────────────────

    def add_scheme(self, name, category="عام"):
        nom_nettoye = self.strip_tashkeel(name)
        # ── Test d'appartenance avec  'in'  (utilise __contains__)
        if nom_nettoye not in self.schemes:
            # ── Insertion avec  table[cle] = valeur  (utilise __setitem__)
            self.schemes[nom_nettoye] = {"cat": category}
            self.save_data()
            return True
        return False


    def delete_scheme(self, name):
        nom_nettoye = self.strip_tashkeel(name)
        if nom_nettoye in self.schemes:
            # ── Suppression avec  del table[cle]  (utilise __delitem__)
            del self.schemes[nom_nettoye]
            self.save_data()
            return True
        return False


    # ────────────────────────────────────────────────
    #           SAUVEGARDE ET CHARGEMENT
    # ────────────────────────────────────────────────

    def load_data(self, r_path=None, s_path=None):
        if r_path: self.r_path = r_path
        if s_path: self.s_path = s_path

        # Chargement des racines
        if os.path.exists(self.r_path):
            with open(self.r_path, 'r', encoding='utf-8') as f:
                for ligne in f:
                    racine = self.strip_tashkeel(ligne.strip())
                    if self.is_arabic_triple(racine):
                        self.root_tree = self.insert_root(self.root_tree, racine)

        # Chargement des schèmes
        if os.path.exists(self.s_path):
            with open(self.s_path, 'r', encoding='utf-8') as f:
                for ligne in f:
                    parties = ligne.strip().split(',')
                    if parties:
                        nom = self.strip_tashkeel(parties[0])
                        # ma_longueur sur une liste Python standard → ok
                        cat = parties[1] if ma_longueur(parties) > 1 else "عام"
                        # ── Insertion dans self.schemes (MaTableHachage)
                        self.schemes[nom] = {"cat": cat}


    def save_data(self):
        """Sauvegarde les racines et schèmes sur disque"""
        # Sauvegarde des racines (parcours inorder)
        racines = self.get_all_roots_data(self.root_tree, [])
        with open(self.r_path, 'w', encoding='utf-8') as f:
            for elem in racines:
                f.write(elem['root'] + '\n')

        # Sauvegarde des schèmes
        # ── Itération avec .items() (utilise la méthode items() de MaTableHachage)
        with open(self.s_path, 'w', encoding='utf-8') as f:
            for nom, info in self.schemes.items():
                f.write(f"{nom},{info['cat']}\n")


    def get_all_roots_data(self, node, resultat):
        """Parcours inorder pour collecter toutes les racines"""
        if node:
            self.get_all_roots_data(node.left, resultat)

            # ── Conversion de derived_words (MaTableHachage) en dict Python
            #    pour la compatibilité avec les templates Jinja2 qui
            #    utilisent .items() de Python standard.
            derives_dict = {}
            for mot, freq in node.derived_words.items():
                derives_dict[mot] = freq

            resultat.append({"root": node.key, "derivatives": derives_dict})
            self.get_all_roots_data(node.right, resultat)
        return resultat


    def verify_morphology(self, word, root_key):
        noeud = self.search_root(self.root_tree, root_key)
        if noeud is None:
            return False, None

        mot_net    = self.strip_tashkeel(word)
        racine_net = self.strip_tashkeel(root_key)

        # ── Itération sur self.schemes via __iter__
        for nom_schème in self.schemes:
            genere = self.apply_scheme(racine_net, nom_schème)
            if genere is not None and mot_net == self.strip_tashkeel(genere):
                # ── Lecture/incrémentation dans derived_words (MaTableHachage)
                #    .get(clé, 0) utilise la méthode get() codée manuellement
                noeud.derived_words[mot_net] = noeud.derived_words.get(mot_net, 0) + 1
                return True, nom_schème

        return False, None