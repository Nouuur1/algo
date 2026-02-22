import os
import re
import json
from anytree import Node as AnyNode, RenderTree

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

# ────────────────────────────────────────────────
# Table de hachage manuelle pour les schèmes
# ────────────────────────────────────────────────
class HashTable:
    """Table de hachage implémentée manuellement avec chaînage."""
    def __init__(self, size=101):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        total = 0
        for ch in key:
            total += ord(ch)
        return total % self.size

    def insert(self, key, value):
        idx = self._hash(key)
        bucket = self.table[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        return None

    def delete(self, key):
        idx = self._hash(key)
        bucket = self.table[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return True
        return False

    def items(self):
        for bucket in self.table:
            for item in bucket:
                yield item

    def keys(self):
        for bucket in self.table:
            for k, v in bucket:
                yield k

    def __contains__(self, key):
        return self.get(key) is not None

# ────────────────────────────────────────────────
# Classe Node : un nœud de l'arbre AVL
# ────────────────────────────────────────────────
class Node:
    def __init__(self, key):
        self.key = key                    # La racine trilitère (ex: "كتب")
        self.left = None                  # Fils gauche
        self.right = None                 # Fils droit
        self.height = 1                   # Hauteur du nœud (pour équilibrer)
        self.derived_words = {}           # Mots dérivés validés {mot: fréquence}

# ────────────────────────────────────────────────
# Classe principale : moteur de morphologie arabe (SARF)
# ────────────────────────────────────────────────
class SARF_Logic:
    def __init__(self):
        self.root_tree = None             # Racine de l'arbre AVL
        self.schemes = HashTable()        # Table de hachage des أوزان
        self.r_path = 'data/roots.txt'    # Fichier où on sauve les racines
        self.s_path = 'data/schemes.txt'  # Fichier où on sauve les schèmes
        self.deriv_path = 'data/derivatives.json'  # Fichier JSON des dérivés

    # Vérifie si le texte est une racine arabe de 3 lettres
    def is_arabic_triple(self, text):
        return bool(re.match(r'^[\u0621-\u064A]{3}$', text))

    # Supprime tous les tashkīl (voyelles, shadda, sukūn...)
    def strip_tashkeel(self, text):
        if not text:
            return ""
        return re.sub(r'[\u064B-\u0652]', '', text)

    # ────────────────────────────────────────────────
    #        FONCTIONS DE L'ARBRE AVL
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
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + mon_max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + mon_max(self.get_height(x.left), self.get_height(x.right))
        return x

    def _left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
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

        # Cas LL
        if balance > 1 and key < root.left.key:
            return self._right_rotate(root)
        # Cas RR
        if balance < -1 and key > root.right.key:
            return self._left_rotate(root)
        # Cas LR
        if balance > 1 and key > root.left.key:
            root.left = self._left_rotate(root.left)
            return self._right_rotate(root)
        # Cas RL
        if balance < -1 and key < root.right.key:
            root.right = self._right_rotate(root.right)
            return self._left_rotate(root)

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
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            temp = self._min_node(root.right)
            root.key = temp.key
            root.right = self.delete_root(root.right, temp.key)

        if root is None:
            return root

        root.height = 1 + mon_max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1 and self.get_balance(root.left) >= 0:
            return self._right_rotate(root)
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self._left_rotate(root.left)
            return self._right_rotate(root)
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self._left_rotate(root)
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self._right_rotate(root.right)
            return self._left_rotate(root)

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
        root_word = self.strip_tashkeel(root_word)
        scheme_name = self.strip_tashkeel(scheme_name)

        resultat = ""
        for lettre in scheme_name:
            if lettre == 'ف':
                resultat += root_word[0]
            elif lettre == 'ع':
                resultat += root_word[1]
            elif lettre == 'ل':
                resultat += root_word[2]
            else:
                resultat += lettre
        return resultat

    def populate_derivatives(self, root_key):
        noeud = self.search_root(self.root_tree, root_key)
        if noeud is None:
            return False
        for scheme_name in self.schemes.keys():
            mot = self.apply_scheme(root_key, scheme_name)
            if mot is not None and mot not in noeud.derived_words:
                noeud.derived_words[mot] = 0
        self.save_derivatives()
        return True

    def identify_word(self, word):
        resultats = []
        mot_nettoye = self.strip_tashkeel(word)

        for nom_schème, _ in self.schemes.items():
            schème_nettoye = self.strip_tashkeel(nom_schème)
            if ma_longueur(mot_nettoye) != ma_longueur(schème_nettoye):
                continue

            r1 = r2 = r3 = None
            est_possible = True

            for i in range(ma_longueur(mot_nettoye)):
                lettre_mot = mot_nettoye[i]
                lettre_schème = schème_nettoye[i]

                if lettre_schème == 'ف':
                    r1 = lettre_mot
                elif lettre_schème == 'ع':
                    r2 = lettre_mot
                elif lettre_schème == 'ل':
                    r3 = lettre_mot
                elif lettre_mot != lettre_schème:
                    est_possible = False
                    break

            if est_possible and r1 is not None and r2 is not None and r3 is not None:
                racine_candidate = r1 + r2 + r3
                if self.search_root(self.root_tree, racine_candidate):
                    resultats.append({
                        "root": racine_candidate,
                        "scheme": nom_schème,
                        "word": word
                    })

        return resultats

    def verify_morphology(self, word, root_key):
        noeud = self.search_root(self.root_tree, root_key)
        if noeud is None:
            return False, None

        mot_net = self.strip_tashkeel(word)
        racine_net = self.strip_tashkeel(root_key)

        for nom_schème in self.schemes.keys():
            genere = self.apply_scheme(racine_net, nom_schème)
            if genere is not None and mot_net == self.strip_tashkeel(genere):
                noeud.derived_words[mot_net] = noeud.derived_words.get(mot_net, 0) + 1
                self.save_derivatives()
                return True, nom_schème

        return False, None

    # ────────────────────────────────────────────────
    #           GESTION DES أوزان (schèmes)
    # ────────────────────────────────────────────────
    def add_scheme(self, name, category="عام"):
        nom_nettoye = self.strip_tashkeel(name)
        if nom_nettoye not in self.schemes:
            self.schemes.insert(nom_nettoye, {"cat": category})
            self.save_data()
            return True
        return False

    def delete_scheme(self, name):
        nom_nettoye = self.strip_tashkeel(name)
        if self.schemes.delete(nom_nettoye):
            self.save_data()
            return True
        return False

    # ────────────────────────────────────────────────
    #           FONCTIONNALITÉS SUPPLÉMENTAIRES
    # ────────────────────────────────────────────────
    def get_stats(self):
        roots_count = 0
        total_derivs = 0
        max_derivs = 0
        max_root = None
        nodes = self.get_all_roots_data(self.root_tree, [])
        for item in nodes:
            roots_count += 1
            dcount = len(item['derivatives'])
            total_derivs += dcount
            if dcount > max_derivs:
                max_derivs = dcount
                max_root = item['root']
        schemes_count = sum(1 for _ in self.schemes.items())
        return {
            "roots": roots_count,
            "schemes": schemes_count,
            "total_derivatives": total_derivs,
            "max_derivatives_root": max_root,
            "max_derivatives_count": max_derivs
        }

    def search_derivatives(self, pattern):
        pattern = self.strip_tashkeel(pattern)
        results = []
        nodes = self.get_all_roots_data(self.root_tree, [])
        for item in nodes:
            root = item['root']
            for word, freq in item['derivatives'].items():
                if pattern in word:
                    results.append({"root": root, "word": word, "freq": freq})
        return results

    # ────────────────────────────────────────────────
    #           SAUVEGARDE ET CHARGEMENT
    # ────────────────────────────────────────────────
    def load_data(self, r_path=None, s_path=None):
        if r_path:
            self.r_path = r_path
        if s_path:
            self.s_path = s_path

        # Chargement racines
        if os.path.exists(self.r_path):
            with open(self.r_path, 'r', encoding='utf-8') as f:
                for ligne in f:
                    racine = self.strip_tashkeel(ligne.strip())
                    if self.is_arabic_triple(racine):
                        self.root_tree = self.insert_root(self.root_tree, racine)

        # Chargement schèmes
        if os.path.exists(self.s_path):
            with open(self.s_path, 'r', encoding='utf-8') as f:
                for ligne in f:
                    parties = ligne.strip().split(',')
                    if parties:
                        nom = self.strip_tashkeel(parties[0])
                        cat = parties[1] if ma_longueur(parties) > 1 else "عام"
                        self.schemes.insert(nom, {"cat": cat})

        self.load_derivatives()

    def load_derivatives(self):
        if not os.path.exists(self.deriv_path):
            return
        with open(self.deriv_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for root_key, derivs in data.items():
            node = self.search_root(self.root_tree, root_key)
            if node:
                node.derived_words = derivs

    def save_data(self):
        racines = self.get_all_roots_data(self.root_tree, [])
        with open(self.r_path, 'w', encoding='utf-8') as f:
            for elem in racines:
                f.write(elem['root'] + '\n')
        with open(self.s_path, 'w', encoding='utf-8') as f:
            for nom, info in self.schemes.items():
                f.write(f"{nom},{info['cat']}\n")
        self.save_derivatives()

    def save_derivatives(self):
        all_derivs = {}
        nodes = self.get_all_roots_data(self.root_tree, [])
        for item in nodes:
            root = item['root']
            derivs = item['derivatives']
            if derivs:
                all_derivs[root] = derivs
        with open(self.deriv_path, 'w', encoding='utf-8') as f:
            json.dump(all_derivs, f, ensure_ascii=False, indent=2)

    def get_all_roots_data(self, node, resultat):
        if node:
            self.get_all_roots_data(node.left, resultat)
            resultat.append({"root": node.key, "derivatives": node.derived_words})
            self.get_all_roots_data(node.right, resultat)
        return resultat

    # ────────────────────────────────────────────────
    #           VISUALISATION DE L'ARBRE
    # ────────────────────────────────────────────────
    def get_tree_text(self):
        """Retourne une représentation textuelle de l'arbre AVL (anytree)."""
        if self.root_tree is None:
            return "🌱 Arbre vide"

        def build_anytree(node, parent=None):
            if node is None:
                return None
            # Affiche la clé et la hauteur
            any_node = AnyNode(name=f"{node.key} (h={node.height})", parent=parent)
            build_anytree(node.left, any_node)
            build_anytree(node.right, any_node)
            return any_node

        root_any = build_anytree(self.root_tree)
        lines = []
        for pre, fill, node in RenderTree(root_any):
            lines.append(f"{pre}{node.name}")
        return "\n".join(lines)

    def display_tree(self):
        """Affiche dans la console."""
        print(self.get_tree_text())