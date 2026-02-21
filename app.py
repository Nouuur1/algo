# Importation des modules nécessaires de Flask
# Flask est le framework web léger utilisé pour créer l'application
from flask import Flask, render_template, request, jsonify

# Importation de la classe principale SARF_Logic (le moteur de morphologie)
# C'est elle qui gère l'arbre AVL, les racines, les schèmes, la génération, etc.
from logic import SARF_Logic

# Création de l'application Flask
# __name__ permet à Flask de savoir où chercher les templates et fichiers statiques
app = Flask(__name__)

# Création d'une instance unique du moteur SARF_Logic
# Cette instance est partagée par toutes les routes (singleton)
logic = SARF_Logic()

# Chargement initial des données depuis les fichiers txt au démarrage de l'application
# Cela remplit l'arbre AVL avec les racines et le dictionnaire avec les schèmes
logic.load_data('data/roots.txt', 'data/schemes.txt')


# ────────────────────────────────────────────────
# ROUTE PRINCIPALE : page d'accueil
# ────────────────────────────────────────────────
@app.route('/')
def home():
    # Affiche la page principale (index.html) qui contient toutes les cartes interactives
    # C'est la page que l'utilisateur voit en premier
    return render_template('index.html')


# ────────────────────────────────────────────────
# AFFICHAGE DE TOUTES LES RACINES STOCKÉES
# ────────────────────────────────────────────────
@app.route('/view_roots')
def view_roots():
    # Récupère toutes les racines et leurs dérivés via un parcours inorder de l'arbre AVL
    # get_all_roots_data retourne une liste de dictionnaires {root, derivatives}
    data = logic.get_all_roots_data(logic.root_tree, [])
    
    # Affiche la page view_roots.html en lui passant la liste des racines
    return render_template('view_roots.html', roots=data)


# ────────────────────────────────────────────────
# AFFICHAGE DE TOUS LES SCHÈMES (أوزان)
# ────────────────────────────────────────────────
@app.route('/view_schemes')
def view_schemes():
    # Transforme le dictionnaire self.schemes en une liste de dictionnaires
    # plus facile à afficher dans le template Jinja2
    s_list = [{"name": k, "cat": v["cat"]} for k, v in logic.schemes.items()]
    
    # Affiche la page view_schemes.html avec la liste des schèmes
    return render_template('view_schemes.html', schemes=s_list)


# ────────────────────────────────────────────────
# GÉNÉRATION MASSIVE DE TOUS LES DÉRIVÉS D'UNE RACINE
# ────────────────────────────────────────────────
@app.route('/generate_all', methods=['POST'])
def generate_all():
    # Récupère la racine envoyée par JavaScript (via JSON)
    root = request.json.get('root')
    
    # Vérifie si cette racine existe vraiment dans l'arbre AVL
    if not logic.search_root(logic.root_tree, root):
        # Si non trouvée → erreur 404 avec message en arabe
        return jsonify({"error": "الجذر غير موجود في قاعدة البيانات"}), 404
    
    # Génère tous les dérivés possibles et les stocke dans derived_words (fréquence = 0)
    logic.populate_derivatives(root)
    
    # Prépare une liste de résultats pour l'affichage immédiat dans le navigateur
    # Chaque élément contient le schème et le mot généré
    res = [{"scheme": s, "word": logic.apply_scheme(root, s)} for s in logic.schemes]
    
    # Retourne la liste en JSON pour que JavaScript puisse l'afficher
    return jsonify({"results": res})


# ────────────────────────────────────────────────
# VÉRIFICATION MORPHOLOGIQUE : mot appartient-il à une racine ?
# ────────────────────────────────────────────────
@app.route('/verify', methods=['POST'])
def verify():
    # Récupère le mot et la racine envoyés par l'utilisateur (via JSON)
    word = request.json.get('word')
    root = request.json.get('root')
    
    # Appelle la fonction verify_morphology du moteur
    # Retourne (True/False, nom_du_schème) ou (False, None)
    ok, scheme = logic.verify_morphology(word, root)
    
    if ok:
        # Succès → message positif avec le nom du schème
        return jsonify({
            "valid": True,
            "message": f"تَمَّ التحقق بنجاح! الوزن: {scheme}"
        })
    else:
        # Échec → message négatif
        return jsonify({
            "valid": False,
            "message": "هذه الكلمة لا تنتمي لهذا الجذر وفق الأوزان المتاحة"
        })


# ────────────────────────────────────────────────
# IDENTIFICATION : trouver la/les racines possibles d'un mot
# ────────────────────────────────────────────────
@app.route('/identify', methods=['POST'])
def identify():
    # Récupère le mot envoyé par l'utilisateur
    word = request.json.get('word')
    
    # Appelle identify_word : recherche inverse mot → racines + schèmes
    res = logic.identify_word(word)
    
    if not res:
        # Aucun résultat → erreur 404
        return jsonify({"error": "لم يتم العثور على أصل لهذا المشتق"}), 404
    
    # Retourne la liste des résultats trouvés en JSON
    return jsonify({"results": res})


# ────────────────────────────────────────────────
# GESTION DES RACINES : ajout ou suppression
# ────────────────────────────────────────────────
@app.route('/manage', methods=['POST'])
def manage():
    # Récupère les données envoyées par JavaScript (JSON)
    data = request.json
    root = data.get('root', '').strip()   # La racine (3 lettres)
    action = data.get('action')           # 'add' ou 'delete'
    
    # Vérification : doit être exactement 3 lettres arabes
    if not logic.is_arabic_triple(root):
        return jsonify({"error": "3 أحرف عربية فقط"}), 400
    
    if action == 'add':
        # Insertion dans l'arbre AVL (équilibré automatiquement)
        logic.root_tree = logic.insert_root(logic.root_tree, root)
        return jsonify({"success": f"تمت إضافة الجذر '{root}'"})
    
    elif action == 'delete':
        # Suppression de l'arbre AVL (rééquilibrage après)
        logic.root_tree = logic.delete_root(logic.root_tree, root)
        return jsonify({"success": f"تم حذف الجذر '{root}'"})
    
    # Si action inconnue → erreur
    return jsonify({"error": "Action non valide"}), 400


# ────────────────────────────────────────────────
# AJOUT D'UN NOUVEAU SCHÈME (وزن) DYNAMIQUEMENT
# ────────────────────────────────────────────────
@app.route('/add_scheme', methods=['POST'])
def add_scheme():
    # Récupère le nom du schème et sa catégorie (optionnelle)
    name = request.json.get('name')
    cat = request.json.get('category', 'عام')
    
    # Appelle la fonction d'ajout dans le moteur
    # Elle vérifie si le schème existe déjà et sauvegarde automatiquement
    if logic.add_scheme(name, cat):
        return jsonify({"success": f"تمت إضافة الوزن '{name}'"})
    
    # Déjà existant
    return jsonify({"error": "الوزن موجود بالفعل"}), 400


# ────────────────────────────────────────────────
# SUPPRESSION D'UN SCHÈME EXISTANT
# ────────────────────────────────────────────────
@app.route('/delete_scheme', methods=['POST'])
def delete_scheme():
    # Récupère le nom du schème à supprimer
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"error": "الوزن مطلوب"}), 400
    
    # Appelle la fonction de suppression dans le moteur
    if logic.delete_scheme(name):
        return jsonify({"success": f"تم حذف الوزن '{name}' بنجاح"})
    
    # Non trouvé
    return jsonify({"error": f"الوزن '{name}' غير موجود"}), 404


# ────────────────────────────────────────────────
# POINT D'ENTRÉE : lance le serveur Flask
# ────────────────────────────────────────────────
if __name__ == '__main__':
    # debug=True → affiche les erreurs détaillées dans le navigateur
    # Très utile pendant le développement
    app.run(debug=True)