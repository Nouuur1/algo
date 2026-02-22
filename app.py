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

@app.route('/generate_all', methods=['POST'])
def generate_all():
    root = request.json.get('root')
    if not logic.search_root(logic.root_tree, root):
        return jsonify({"error": "الجذر غير موجود في قاعدة البيانات"}), 404
    logic.populate_derivatives(root)
    res = [{"scheme": s, "word": logic.apply_scheme(root, s)} for s in logic.schemes.keys()]
    return jsonify({"results": res})

@app.route('/verify', methods=['POST'])
def verify():
    word = request.json.get('word')
    root = request.json.get('root')
    ok, scheme = logic.verify_morphology(word, root)
    if ok:
        return jsonify({
            "valid": True,
            "message": f"تَمَّ التحقق بنجاح! الوزن: {scheme}"
        })
    else:
        return jsonify({
            "valid": False,
            "message": "هذه الكلمة لا تنتمي لهذا الجذر وفق الأوزان المتاحة"
        })

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
    root = data.get('root', '').strip()
    action = data.get('action')
    if not logic.is_arabic_triple(root):
        return jsonify({"error": "3 أحرف عربية فقط"}), 400
    if action == 'add':
        logic.root_tree = logic.insert_root(logic.root_tree, root)
        logic.save_data()
        return jsonify({"success": f"تمت إضافة الجذر '{root}'"})
    elif action == 'delete':
        logic.root_tree = logic.delete_root(logic.root_tree, root)
        logic.save_data()
        return jsonify({"success": f"تم حذف الجذر '{root}'"})
    return jsonify({"error": "Action non valide"}), 400

@app.route('/add_scheme', methods=['POST'])
def add_scheme():
    name = request.json.get('name')
    cat = request.json.get('category', 'عام')
    if logic.add_scheme(name, cat):
        return jsonify({"success": f"تمت إضافة الوزن '{name}'"})
    return jsonify({"error": "الوزن موجود بالفعل"}), 400

@app.route('/delete_scheme', methods=['POST'])
def delete_scheme():
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({"error": "الوزن مطلوب"}), 400
    if logic.delete_scheme(name):
        return jsonify({"success": f"تم حذف الوزن '{name}' بنجاح"})
    return jsonify({"error": f"الوزن '{name}' غير موجود"}), 404

# Fonctionnalités supplémentaires
@app.route('/stats')
def stats():
    return jsonify(logic.get_stats())

@app.route('/search_derivatives', methods=['POST'])
def search_derivatives():
    pattern = request.json.get('pattern', '')
    results = logic.search_derivatives(pattern)
    return jsonify({"results": results})

# Visualisation de l'arbre
@app.route('/visualize_tree')
def visualize_tree():
    tree_text = logic.get_tree_text()
    return f"""
    <!DOCTYPE html>
    <html dir="ltr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌳 شجرة الجذور المتوازنة</title>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                background: linear-gradient(145deg, #f0f9ff 0%, #e6f7f0 100%);
                font-family: 'Cairo', sans-serif;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }}
            .card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(8px);
                border-radius: 2rem;
                padding: 2rem 3rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                border: 2px solid rgba(255, 255, 255, 0.8);
                max-width: 800px;
                width: 100%;
                text-align: center;
            }}
            h2 {{
                font-size: 2.2rem;
                color: #2f2e41;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }}
            h2 span {{
                background: #10b981;
                color: white;
                font-size: 1.2rem;
                padding: 0.3rem 1rem;
                border-radius: 3rem;
            }}
            .tree-container {{
                background: #1e293b;
                border-radius: 1.5rem;
                padding: 2rem;
                overflow-x: auto;
                text-align: left;
                direction: ltr;
                box-shadow: inset 0 4px 6px rgba(0, 0, 0, 0.3);
                margin-bottom: 2rem;
            }}
            pre {{
                color: #bbf7d0;
                font-family: 'Courier New', monospace;
                font-size: 1.1rem;
                line-height: 1.6;
                margin: 0;
            }}
            .btn {{
                display: inline-block;
                background: #3b82f6;
                color: white;
                text-decoration: none;
                padding: 1rem 2.5rem;
                border-radius: 3rem;
                font-weight: 700;
                font-size: 1.2rem;
                box-shadow: 0 8px 0 #1e40af;
                transition: all 0.2s;
                border: 2px solid transparent;
            }}
            .btn:hover {{
                transform: translateY(-4px);
                box-shadow: 0 12px 0 #1e40af;
                background: #2563eb;
            }}
            .btn:active {{
                transform: translateY(4px);
                box-shadow: 0 4px 0 #1e40af;
            }}
            .note {{
                margin-top: 1rem;
                color: #4b5563;
            }}
        </style>
    </head>
    <body>
        <div class="card animate__animated animate__zoomIn">
            <h2>🌳 شجرة الجذور المتوازنة (AVL) <span>{logic.get_stats()['roots']} nœuds</span></h2>
            <div class="tree-container">
                <pre>{tree_text}</pre>
            </div>
            <a href="/" class="btn">⬅️ العودة إلى المغارة</a>
            <div class="note">(h = ارتفاع العُقدة)</div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)