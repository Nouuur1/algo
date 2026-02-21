from flask import Flask, render_template, request, jsonify
from logic import SARF_Logic

app = Flask(__name__)
logic = SARF_Logic()
logic.load_data('data/roots.txt', 'data/schemes.txt')

@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/view_roots')
def view_roots():
    data = logic.get_all_roots_data(logic.root_tree, [])
    return render_template('view_roots.html', roots=data)

@app.route('/view_schemes')
def view_schemes():
    s_list = [{"name": k, "cat": v["cat"]} for k, v in logic.schemes.items()]
    return render_template('view_schemes.html', schemes=s_list)

# Route améliorée pour utiliser populate_derivatives (Génération massive)
@app.route('/generate_all', methods=['POST'])
def generate_all():
    root = request.json.get('root')
    if not logic.search_root(logic.root_tree, root):
        return jsonify({"error": "الجذر غير موجود في قاعدة البيانات"}), 404
    
    # On génère et on stocke dans l'arbre AVL
    logic.populate_derivatives(root)
    
    # On renvoie la liste pour l'affichage immédiat
    res = [{"scheme": s, "word": logic.apply_scheme(root, s)} for s in logic.schemes]
    return jsonify({"results": res})

@app.route('/verify', methods=['POST'])
def verify():
    word, root = request.json.get('word'), request.json.get('root')
    ok, scheme = logic.verify_morphology(word, root)
    if ok: 
        return jsonify({"valid": True, "message": f"تَمَّ التحقق بنجاح! الوزن: {scheme}"})
    return jsonify({"valid": False, "message": "هذه الكلمة لا تنتمي لهذا الجذر وفق الأوزان المتاحة"})

@app.route('/identify', methods=['POST'])
def identify():
    word = request.json.get('word')
    res = logic.identify_word(word)
    if not res: 
        return jsonify({"error": "لم يتم العثور على أصل لهذا المشتق"}), 404
    return jsonify({"results": res})

@app.route('/manage', methods=['POST'])
def manage():
    data = request.json
    root, action = data.get('root', '').strip(), data.get('action')
    if not logic.is_arabic_triple(root): 
        return jsonify({"error": "3 أحرف عربية فقط"}), 400
    
    if action == 'add':
        logic.root_tree = logic.insert_root(logic.root_tree, root)
        return jsonify({"success": f"تمت إضافة الجذر '{root}'"})
    elif action == 'delete':
        logic.root_tree = logic.delete_root(logic.root_tree, root)
        return jsonify({"success": f"تم حذف الجذر '{root}'"})

# Route pour ajouter un schème dynamiquement
@app.route('/add_scheme', methods=['POST'])
def add_scheme():
    name = request.json.get('name')
    cat = request.json.get('category', 'عام')
    if logic.add_scheme(name, cat):
        return jsonify({"success": f"تمت إضافة الوزن '{name}'"})
    return jsonify({"error": "الوزن موجود بالفعل"}), 400

# Route pour supprimer un schème
@app.route('/delete_scheme', methods=['POST'])
def delete_scheme():
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"error": "الوزن مطلوب"}), 400
    
    if logic.delete_scheme(name):
        return jsonify({"success": f"تم حذف الوزن '{name}' بنجاح"})
    else:
        return jsonify({"error": f"الوزن '{name}' غير موجود"}), 404


if __name__ == '__main__': 
    app.run(debug=True)