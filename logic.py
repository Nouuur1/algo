import os
import re

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
        self.key = key                    # La racine trilitère (ex: "كتب")
        self.left = None                  # Fils gauche
        self.right = None                 # Fils droit
        self.height = 1                   # Hauteur du nœud (pour équilibrer)
        self.derived_words = {}           # Mots dérivés validés {mot: fréquence}


# Classe principale : moteur de morphologie arabe (SARF)
class SARF_Logic:
    def __init__(self):
        self.root_tree = None             # Racine de l'arbre AVL
        self.schemes = {}                 # Dictionnaire des أوزان
        self.r_path = 'data/roots.txt'    # Fichier où on sauve les racines
        self.s_path = 'data/schemes.txt'  # Fichier où on sauve les schèmes


    # Vérifie si le texte est une racine arabe de 3 lettres
    def is_arabic_triple(self, text):
        # On utilise une expression régulière pour vérifier
        return bool(re.match(r'^[\u0621-\u064A]{3}$', text))


    # Supprime tous les tashkīl (voyelles, shadda, sukūn...)
    def strip_tashkeel(self, text):
        if not text:
            return ""
        # On enlève tous les caractères de la plage Unicode des tashkīl
        return re.sub(r'[\u064B-\u0652]', '', text)


    # ────────────────────────────────────────────────
    #        FONCTIONS DE L'ARBRE AVL (sans max ni len)
    # ────────────────────────────────────────────────


    # Retourne la hauteur d'un nœud (0 si None)
    def get_height(self, node):
        if node is None:
            return 0
        return node.height


    # Calcule l'équilibre : hauteur gauche - hauteur droite
    def get_balance(self, node):
        if node is None:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)


    # Rotation droite (corrige déséquilibre à gauche)
    def _right_rotate(self, y):
        x = y.left
        T2 = x.right
        
        # Effectue la rotation
        x.right = y
        y.left = T2
        
        # Met à jour les hauteurs (sans max)
        y.height = 1 + mon_max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + mon_max(self.get_height(x.left), self.get_height(x.right))
        
        return x


    # Rotation gauche (corrige déséquilibre à droite)
    def _left_rotate(self, x):
        y = x.right
        T2 = y.left
        
        # Effectue la rotation
        y.left = x
        x.right = T2
        
        # Met à jour les hauteurs
        x.height = 1 + mon_max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + mon_max(self.get_height(y.left), self.get_height(y.right))
        
        return y


    # Insertion d'une racine dans l'arbre AVL
    def insert_root(self, root, key):
        # Cas de base : feuille atteinte → nouveau nœud
        if root is None:
            return Node(key)
        
        # Insertion comme dans un arbre binaire de recherche
        if key < root.key:
            root.left = self.insert_root(root.left, key)
        elif key > root.key:
            root.right = self.insert_root(root.right, key)
        else:
            # Déjà présent → on ne fait rien
            return root

        # Met à jour la hauteur du nœud courant
        root.height = 1 + mon_max(
            self.get_height(root.left),
            self.get_height(root.right)
        )

        # Vérifie si l'arbre est déséquilibré
        balance = self.get_balance(root)

        # Cas LL : rotation droite simple
        if balance > 1 and key < root.left.key:
            return self._right_rotate(root)
        
        # Cas RR : rotation gauche simple
        if balance < -1 and key > root.right.key:
            return self._left_rotate(root)
        
        # Cas LR : rotation gauche puis droite
        if balance > 1 and key > root.left.key:
            root.left = self._left_rotate(root.left)
            return self._right_rotate(root)
        
        # Cas RL : rotation droite puis gauche
        if balance < -1 and key < root.right.key:
            root.right = self._right_rotate(root.right)
            return self._left_rotate(root)

        return root


    # Recherche d'une racine dans l'arbre
    def search_root(self, root, key):
        if root is None or root.key == key:
            return root
        
        if key < root.key:
            return self.search_root(root.left, key)
        return self.search_root(root.right, key)


    # Suppression d'une racine
    def delete_root(self, root, key):
        if root is None:
            return root

        if key < root.key:
            root.left = self.delete_root(root.left, key)
        elif key > root.key:
            root.right = self.delete_root(root.right, key)
        else:
            # Nœud trouvé
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            
            # Deux enfants : on prend le successeur (minimum à droite)
            temp = self._min_node(root.right)
            root.key = temp.key
            root.right = self.delete_root(root.right, temp.key)

        if root is None:
            return root

        # Mise à jour hauteur
        root.height = 1 + mon_max(
            self.get_height(root.left),
            self.get_height(root.right)
        )

        balance = self.get_balance(root)

        # Rééquilibrage après suppression
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


    # Trouve le nœud le plus petit dans un sous-arbre
    def _min_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current


    # ────────────────────────────────────────────────
    #     GÉNÉRATION ET ANALYSE MORPHOLOGIQUE
    # ────────────────────────────────────────────────


    # Génère un mot à partir d'une racine et d'un schème
    def apply_scheme(self, root_word, scheme_name):
        # On vérifie la longueur sans len()
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


    # Génère tous les dérivés possibles pour une racine
    def populate_derivatives(self, root_key):
        noeud = self.search_root(self.root_tree, root_key)
        if noeud is None:
            return False
        
        for schème in self.schemes:
            mot = self.apply_scheme(root_key, schème)
            if mot is not None and mot not in noeud.derived_words:
                noeud.derived_words[mot] = 0  # Initialisé à 0
        return True


    # Recherche inverse : mot → racines + schèmes possibles
    def identify_word(self, word):
        resultats = []
        mot_nettoye = self.strip_tashkeel(word)

        for nom_schème in self.schemes:
            schème_nettoye = self.strip_tashkeel(nom_schème)
            
            # Vérifie longueurs égales sans len()
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


    # ────────────────────────────────────────────────
    #           GESTION DES أوزان (schèmes)
    # ────────────────────────────────────────────────


    def add_scheme(self, name, category="عام"):
        nom_nettoye = self.strip_tashkeel(name)
        if nom_nettoye not in self.schemes:
            self.schemes[nom_nettoye] = {"cat": category}
            self.save_data()  # Sauvegarde automatique
            return True
        return False


    def delete_scheme(self, name):
        nom_nettoye = self.strip_tashkeel(name)
        if nom_nettoye in self.schemes:
            del self.schemes[nom_nettoye]
            self.save_data()  # Sauvegarde automatique
            return True
        return False


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
                        self.schemes[nom] = {"cat": cat}


    def save_data(self):
        """Sauvegarde les racines et schèmes sur disque"""
        # Sauvegarde racines (parcours inorder)
        racines = self.get_all_roots_data(self.root_tree, [])
        with open(self.r_path, 'w', encoding='utf-8') as f:
            for elem in racines:
                f.write(elem['root'] + '\n')
        
        # Sauvegarde schèmes
        with open(self.s_path, 'w', encoding='utf-8') as f:
            for nom, info in self.schemes.items():
                f.write(f"{nom},{info['cat']}\n")


    # Parcours inorder pour collecter toutes les racines
    def get_all_roots_data(self, node, resultat):
        if node:
            self.get_all_roots_data(node.left, resultat)
            resultat.append({"root": node.key, "derivatives": node.derived_words})
            self.get_all_roots_data(node.right, resultat)
        return resultat


    # Vérifie si un mot appartient à une racine selon les schèmes
    def verify_morphology(self, word, root_key):
        noeud = self.search_root(self.root_tree, root_key)
        if noeud is None:
            return False, None
            
        mot_net = self.strip_tashkeel(word)
        racine_net = self.strip_tashkeel(root_key)
        
        for nom_schème in self.schemes:
            genere = self.apply_scheme(racine_net, nom_schème)
            if genere is not None and mot_net == self.strip_tashkeel(genere):
                # On augmente le compteur de ce mot dérivé
                noeud.derived_words[mot_net] = noeud.derived_words.get(mot_net, 0) + 1
                return True, nom_schème
                
        return False, None