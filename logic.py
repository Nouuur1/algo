import os
import re

class Node:
    def __init__(self, key):
        self.key = key
        self.left = self.right = None
        self.height = 1
        self.derived_words = {} 

class SARF_Logic:
    def __init__(self):
        self.root_tree = None
        self.schemes = {}
        # Chemins par défaut pour la sauvegarde
        self.r_path = 'data/roots.txt'
        self.s_path = 'data/schemes.txt'

    def is_arabic_triple(self, text):
        return bool(re.match(r'^[\u0621-\u064A]{3}$', text))

    def strip_tashkeel(self, text):
        if not text: return ""
        return re.sub(r'[\u064B-\u0652]', '', text)

    # --- MÉCANISMES AVL ---
    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        if not node: return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def _right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x

    def _left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def insert_root(self, root, key):
        if not root: return Node(key)
        if key < root.key: root.left = self.insert_root(root.left, key)
        elif key > root.key: root.right = self.insert_root(root.right, key)
        else: return root 

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1 and key < root.left.key: return self._right_rotate(root)
        if balance < -1 and key > root.right.key: return self._left_rotate(root)
        if balance > 1 and key > root.left.key:
            root.left = self._left_rotate(root.left)
            return self._right_rotate(root)
        if balance < -1 and key < root.right.key:
            root.right = self._right_rotate(root.right)
            return self._left_rotate(root)
        return root

    def search_root(self, root, key):
        if not root or root.key == key: return root
        if key < root.key: return self.search_root(root.left, key)
        return self.search_root(root.right, key)

    def delete_root(self, root, key):
        if not root: return root
        if key < root.key: root.left = self.delete_root(root.left, key)
        elif key > root.key: root.right = self.delete_root(root.right, key)
        else:
            if not root.left: return root.right
            elif not root.right: return root.left
            temp = self._min_node(root.right)
            root.key = temp.key
            root.right = self.delete_root(root.right, temp.key)

        if not root: return root
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1 and self.get_balance(root.left) >= 0: return self._right_rotate(root)
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self._left_rotate(root.left)
            return self._right_rotate(root)
        if balance < -1 and self.get_balance(root.right) <= 0: return self._left_rotate(root)
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self._right_rotate(root.right)
            return self._left_rotate(root)
        return root

    def _min_node(self, node):
        curr = node
        while curr.left: curr = curr.left
        return curr

    # --- MOTEURS DE TRANSFORMATION & ANALYSE ---
    def apply_scheme(self, root_word, scheme_name):
        if len(root_word) != 3: return None
        root_word, scheme_name = self.strip_tashkeel(root_word), self.strip_tashkeel(scheme_name)
        res = ""
        for char in scheme_name:
            if char == 'ف': res += root_word[0]
            elif char == 'ع': res += root_word[1]
            elif char == 'ل': res += root_word[2]
            else: res += char
        return res

    def populate_derivatives(self, root_key):
        node = self.search_root(self.root_tree, root_key)
        if not node: return False
        for s_name in self.schemes:
            word = self.apply_scheme(root_key, s_name)
            if word and word not in node.derived_words:
                node.derived_words[word] = 0
        return True

    def identify_word(self, word):
        results = []
        w_clean = self.strip_tashkeel(word)
        for s_name in self.schemes:
            s_clean = self.strip_tashkeel(s_name)
            if len(w_clean) == len(s_clean):
                r1, r2, r3, possible = None, None, None, True
                for wc, sc in zip(w_clean, s_clean):
                    if sc == 'ف': r1 = wc
                    elif sc == 'ع': r2 = wc
                    elif sc == 'ل': r3 = wc
                    elif wc != sc: possible = False; break
                if possible and r1 and r2 and r3:
                    root_cand = r1 + r2 + r3
                    if self.search_root(self.root_tree, root_cand):
                        results.append({"root": root_cand, "scheme": s_name, "word": word})
        return results

    # --- GESTION DES SCHÈMES ---
    def add_scheme(self, name, category=""):
        name = self.strip_tashkeel(name)
        if name not in self.schemes:
            self.schemes[name] = {"cat": category}
            self.save_data() # Sauvegarde auto
            return True
        return False

    def delete_scheme(self, name):
        name = self.strip_tashkeel(name)
        if name in self.schemes:
            del self.schemes[name]
            self.save_data() # Sauvegarde auto
            return True
        return False

    # --- PERSISTANCE DES DONNÉES ---
    def load_data(self, r_path=None, s_path=None):
        if r_path: self.r_path = r_path
        if s_path: self.s_path = s_path
        
        if os.path.exists(self.r_path):
            with open(self.r_path, 'r', encoding='utf-8') as f:
                for line in f:
                    r = self.strip_tashkeel(line.strip())
                    if self.is_arabic_triple(r): self.root_tree = self.insert_root(self.root_tree, r)
        
        if os.path.exists(self.s_path):
            with open(self.s_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if parts: self.schemes[self.strip_tashkeel(parts[0])] = {"cat": parts[1] if len(parts)>1 else "عام"}

    def save_data(self):
        """Sauvegarde les racines et les schèmes dans les fichiers respectifs."""
        # Sauvegarde des racines
        roots_list = self.get_all_roots_data(self.root_tree, [])
        with open(self.r_path, 'w', encoding='utf-8') as f:
            for r_obj in roots_list:
                f.write(r_obj['root'] + '\n')
        
        # Sauvegarde des schèmes
        with open(self.s_path, 'w', encoding='utf-8') as f:
            for s_name, info in self.schemes.items():
                f.write(f"{s_name},{info['cat']}\n")

    def get_all_roots_data(self, node, res):
        if node:
            self.get_all_roots_data(node.left, res)
            res.append({"root": node.key, "derivatives": node.derived_words})
            self.get_all_roots_data(node.right, res)
        return res
    def verify_morphology(self, word, root_key):
        """Vérifie si un mot correspond à une racine selon les schèmes connus."""
        node = self.search_root(self.root_tree, root_key)
        if not node:
            return False, None
            
        word_clean = self.strip_tashkeel(word)
        root_clean = self.strip_tashkeel(root_key)
        
        for s_name in self.schemes:
            # On génère le mot théorique avec ce schème
            generated = self.apply_scheme(root_clean, s_name)
            if word_clean == self.strip_tashkeel(generated):
                # Si ça match, on enregistre qu'on a trouvé ce dérivé
                node.derived_words[word_clean] = node.derived_words.get(word_clean, 0) + 1
                return True, s_name
                
        return False, None