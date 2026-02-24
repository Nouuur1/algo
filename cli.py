#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Command-Line Interface for Maghara Sarf
Allows users to manage roots, schemes, and generate/validate derivatives
"""

from logic import SARF_Logic
import os

class SarfCLI:
    def __init__(self):
        """Initialize CLI with logic engine"""
        self.logic = SARF_Logic()
        self.logic.load_data('data/roots.txt', 'data/schemes.txt')
        self.running = True

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*50)
        print(f"  {title}")
        print("="*50)

    def print_menu(self, options):
        """Print menu options"""
        for key, value in options.items():
            print(f"  {key}. {value}")
        print()

    # ════════════════════════════════════════════════════════════════
    # ROOT MANAGEMENT
    # ════════════════════════════════════════════════════════════════

    def add_root(self):
        """Add a new root to the database"""
        self.print_header("إضافة جذر جديد (Add New Root)")
        root = input("  أدخل الجذر (Enter root - 3 Arabic letters): ").strip()
        
        if not self.logic.is_arabic_triple(root):
            print("  ❌ خطأ: يجب أن يكون الجذر 3 أحرف عربية (Error: Must be 3 Arabic letters)")
            return
        
        if self.logic.search_root(self.logic.root_tree, root):
            print(f"  ❌ الجذر '{root}' موجود بالفعل (Root already exists)")
            return
        
        self.logic.root_tree = self.logic.insert_root(self.logic.root_tree, root)
        self.logic.save_data()
        print(f"  ✅ تمت إضافة الجذر '{root}' بنجاح (Root added successfully)")

    def delete_root(self):
        """Delete a root from the database"""
        self.print_header("حذف جذر (Delete Root)")
        root = input("  أدخل الجذر المراد حذفه (Enter root to delete): ").strip()
        
        if not self.logic.is_arabic_triple(root):
            print("  ❌ خطأ: يجب أن يكون الجذر 3 أحرف عربية (Error: Must be 3 Arabic letters)")
            return
        
        if not self.logic.search_root(self.logic.root_tree, root):
            print(f"  ❌ الجذر '{root}' غير موجود (Root not found)")
            return
        
        self.logic.root_tree = self.logic.delete_root(self.logic.root_tree, root)
        self.logic.save_data()
        print(f"  ✅ تم حذف الجذر '{root}' بنجاح (Root deleted successfully)")

    def search_root(self):
        """Search for a root"""
        self.print_header("بحث عن جذر (Search Root)")
        root = input("  أدخل الجذر المراد البحث عنه (Enter root to search): ").strip()
        
        node = self.logic.search_root(self.logic.root_tree, root)
        if node:
            print(f"  ✅ الجذر '{root}' موجود (Root found)")
            if node.derived_words:
                print(f"  📊 عدد المشتقات: {len(node.derived_words)} derivatives")
                print("  المشتقات (Derivatives):")
                for word, freq in list(node.derived_words.items())[:5]:  # Show first 5
                    print(f"    - {word} (frequency: {freq})")
                if len(node.derived_words) > 5:
                    print(f"    ... و {len(node.derived_words) - 5} مشتقات أخرى")
        else:
            print(f"  ❌ الجذر '{root}' غير موجود (Root not found)")

    def list_roots(self):
        """List all roots in database"""
        self.print_header("قائمة جميع الجذور (List All Roots)")
        roots_data = self.logic.get_all_roots_data(self.logic.root_tree, [])
        
        if not roots_data:
            print("  ⚠️ لا توجد جذور في قاعدة البيانات (No roots in database)")
            return
        
        print(f"  📚 عدد الجذور: {len(roots_data)} roots\n")
        for idx, item in enumerate(roots_data, 1):
            root = item['root']
            derivs_count = len(item['derivatives'])
            print(f"  {idx:2}. {root} - {derivs_count} مشتقات (derivatives)")
        
        print(f"\n  المجموع: {len(roots_data)} جذور (Total)")

    # ════════════════════════════════════════════════════════════════
    # SCHEME MANAGEMENT
    # ════════════════════════════════════════════════════════════════

    def add_scheme(self):
        """Add a new scheme/weight"""
        self.print_header("إضافة وزن جديد (Add New Scheme)")
        name = input("  أدخل الوزن (Enter scheme - e.g., فعل): ").strip()
        if not name:
            print("  ❌ الحقل مطلوب (Field required)")
            return
        
        category = input("  أدخل الفئة (Enter category - default: عام): ").strip() or "عام"
        
        if self.logic.add_scheme(name, category):
            print(f"  ✅ تمت إضافة الوزن '{name}' بفئة '{category}' بنجاح")
        else:
            print(f"  ❌ الوزن '{name}' موجود بالفعل (Scheme already exists)")

    def delete_scheme(self):
        """Delete a scheme"""
        self.print_header("حذف وزن (Delete Scheme)")
        name = input("  أدخل الوزن المراد حذفه (Enter scheme to delete): ").strip()
        
        if self.logic.delete_scheme(name):
            print(f"  ✅ تم حذف الوزن '{name}' بنجاح (Scheme deleted)")
        else:
            print(f"  ❌ الوزن '{name}' غير موجود (Scheme not found)")

    def list_schemes(self):
        """List all schemes"""
        self.print_header("قائمة جميع الأوزان (List All Schemes)")
        schemes_list = [(name, info['cat']) for name, info in self.logic.schemes.items()]
        
        if not schemes_list:
            print("  ⚠️ لا توجد أوزان في قاعدة البيانات (No schemes in database)")
            return
        
        print(f"  📚 عدد الأوزان: {len(schemes_list)} schemes\n")
        
        # Group by category
        categories = {}
        for name, cat in schemes_list:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)
        
        for cat, names in sorted(categories.items()):
            print(f"  📁 الفئة: {cat}")
            for idx, name in enumerate(names, 1):
                print(f"     {idx}. {name}")
            print()

    # ════════════════════════════════════════════════════════════════
    # GENERATION & VALIDATION
    # ════════════════════════════════════════════════════════════════

    def generate_derivatives(self):
        """Generate all derivatives for a root"""
        self.print_header("توليد المشتقات (Generate Derivatives)")
        root = input("  أدخل الجذر (Enter root): ").strip()
        
        if not self.logic.is_arabic_triple(root):
            print("  ❌ خطأ: يجب أن يكون الجذر 3 أحرف عربية (Error: Must be 3 Arabic letters)")
            return
        
        node = self.logic.search_root(self.logic.root_tree, root)
        if not node:
            print(f"  ❌ الجذر '{root}' غير موجود (Root not found)")
            return
        
        self.logic.populate_derivatives(root)
        
        # Collect scheme selection
        schemes_list = list(self.logic.schemes.keys())
        if not schemes_list:
            print("  ⚠️ لا توجد أوزان متاحة (No schemes available)")
            return
        
        print(f"\n  📋 الأوزان المتاحة ({len(schemes_list)} available):")
        for idx, scheme in enumerate(schemes_list, 1):
            print(f"     {idx}. {scheme}")
        
        print("\n  0. توليد جميع المشتقات (Generate all)")
        choice = input("\n  اختر رقماً أو اضغط Enter (Select number or press Enter): ").strip()
        
        if not choice or choice == "0":
            # Generate all
            results = []
            for scheme in schemes_list:
                word = self.logic.apply_scheme(root, scheme)
                if word:
                    results.append((scheme, word))
        else:
            # Generate selected scheme
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(schemes_list):
                    scheme = schemes_list[idx]
                    word = self.logic.apply_scheme(root, scheme)
                    results = [(scheme, word)] if word else []
                else:
                    print("  ❌ اختيار غير صحيح (Invalid choice)")
                    return
            except ValueError:
                print("  ❌ أدخل رقماً صحيحاً (Enter a valid number)")
                return
        
        if results:
            print(f"\n  ✅ المشتقات المولدة ({len(results)}):")
            for scheme, word in results:
                print(f"     {word} ← {scheme}")
        else:
            print("  ⚠️ لم يتم توليد أي مشتقات (No derivatives generated)")

    def validate_word(self):
        """Validate if a word belongs to a root"""
        self.print_header("التحقق من المشتق (Validate Derivative)")
        word = input("  أدخل الكلمة (Enter word): ").strip()
        if not word:
            print("  ❌ الحقل مطلوب (Field required)")
            return
        
        root = input("  أدخل الجذر (Enter root): ").strip()
        if not self.logic.is_arabic_triple(root):
            print("  ❌ خطأ: يجب أن يكون الجذر 3 أحرف عربية (Error: Must be 3 Arabic letters)")
            return
        
        ok, scheme = self.logic.verify_morphology(word, root)
        
        if ok:
            print(f"\n  ✅ صحيح! (Valid!)")
            print(f"     الكلمة: {word}")
            print(f"     الجذر: {root}")
            print(f"     الوزن: {scheme}")
            
            # Show word frequency
            node = self.logic.search_root(self.logic.root_tree, root)
            if node and word in node.derived_words:
                freq = node.derived_words[word]
                print(f"     التكرار: {freq} times")
        else:
            print(f"\n  ❌ غير صحيح (Invalid!)")
            print(f"     الكلمة '{word}' لا تنتمي إلى الجذر '{root}'")
            print(f"     بناءً على الأوزان المتاحة")

    def identify_word(self):
        """Identify root from a word"""
        self.print_header("تحديد الجذر من الكلمة (Identify Root from Word)")
        word = input("  أدخل الكلمة (Enter word): ").strip()
        if not word:
            print("  ❌ الحقل مطلوب (Field required)")
            return
        
        results = self.logic.identify_word(word)
        
        if results:
            print(f"\n  ✅ تم العثور على {len(results)} نتيجة (Found {len(results)} result(s)):\n")
            for idx, result in enumerate(results, 1):
                print(f"     {idx}. الجذر: {result['root']} | الوزن: {result['scheme']}")
        else:
            print(f"\n  ❌ لم يتم العثور على جذر لهذه الكلمة (No root found for this word)")

    # ════════════════════════════════════════════════════════════════
    # STATISTICS & UTILITIES
    # ════════════════════════════════════════════════════════════════

    def show_statistics(self):
        """Display database statistics"""
        self.print_header("الإحصائيات (Statistics)")
        stats = self.logic.get_stats()
        
        print(f"  📊 إحصائيات قاعدة البيانات:")
        print(f"     • عدد الجذور: {stats['roots']} roots")
        print(f"     • عدد الأوزان: {stats['schemes']} schemes")
        print(f"     • إجمالي المشتقات: {stats['total_derivatives']} derivatives")
        if stats['max_derivatives_root']:
            print(f"     • جذر به أكثر مشتقات: {stats['max_derivatives_root']}")
            print(f"     • عدد مشتقاته: {stats['max_derivatives_count']}")

    def search_derivatives(self):
        """Search for derivatives by pattern"""
        self.print_header("البحث عن المشتقات (Search Derivatives)")
        pattern = input("  أدخل نمط البحث (Enter search pattern): ").strip()
        
        if not pattern:
            print("  ❌ النمط مطلوب (Pattern required)")
            return
        
        results = self.logic.search_derivatives(pattern)
        
        if results:
            print(f"\n  ✅ تم العثور على {len(results)} نتيجة (Found {len(results)} result(s)):\n")
            # Sort by frequency (descending)
            results.sort(key=lambda x: x['freq'], reverse=True)
            for idx, result in enumerate(results[:10], 1):  # Show first 10
                print(f"     {idx}. {result['word']} ← {result['root']} (freq: {result['freq']})")
            if len(results) > 10:
                print(f"     ... و {len(results) - 10} نتائج أخرى (and {len(results) - 10} more)")
        else:
            print(f"  ❌ لم يتم العثور على نتائج (No results found)")

    # ════════════════════════════════════════════════════════════════
    # MAIN MENU
    # ════════════════════════════════════════════════════════════════

    def show_main_menu(self):
        """Display main menu"""
        self.clear_screen()
        self.print_header("مغارة الكلمات - Maghara Sarf 🌟")
        print("  أهلاً بك في تطبيق تعليمي للصرف العربي")
        print("  Interactive Arabic Morphology Learning App\n")
        
        menu = {
            "1": "إدارة الجذور (Root Management)",
            "2": "إدارة الأوزان (Scheme Management)",
            "3": "توليد المشتقات (Generate Derivatives)",
            "4": "التحقق من المشتق (Validate Word)",
            "5": "تحديد الجذر من الكلمة (Identify Root)",
            "6": "الإحصائيات (Statistics)",
            "7": "البحث عن المشتقات (Search Derivatives)",
            "0": "خروج (Exit)"
        }
        self.print_menu(menu)
        return input("  اختر خياراً (Choose option): ").strip()

    def show_roots_menu(self):
        """Display roots management submenu"""
        self.clear_screen()
        self.print_header("إدارة الجذور (Root Management)")
        menu = {
            "1": "إضافة جذر جديد (Add Root)",
            "2": "حذف جذر (Delete Root)",
            "3": "البحث عن جذر (Search Root)",
            "4": "عرض جميع الجذور (List All Roots)",
            "0": "العودة للقائمة الرئيسية (Back)"
        }
        self.print_menu(menu)
        return input("  اختر خياراً (Choose option): ").strip()

    def show_schemes_menu(self):
        """Display schemes management submenu"""
        self.clear_screen()
        self.print_header("إدارة الأوزان (Scheme Management)")
        menu = {
            "1": "إضافة وزن جديد (Add Scheme)",
            "2": "حذف وزن (Delete Scheme)",
            "3": "عرض جميع الأوزان (List All Schemes)",
            "0": "العودة للقائمة الرئيسية (Back)"
        }
        self.print_menu(menu)
        return input("  اختر خياراً (Choose option): ").strip()

    def handle_roots_menu(self):
        """Handle roots management menu"""
        while True:
            choice = self.show_roots_menu()
            
            if choice == "1":
                self.add_root()
            elif choice == "2":
                self.delete_root()
            elif choice == "3":
                self.search_root()
            elif choice == "4":
                self.list_roots()
            elif choice == "0":
                break
            else:
                print("  ❌ خيار غير صحيح (Invalid choice)")
            
            input("\n  اضغط Enter للمتابعة (Press Enter to continue)...")

    def handle_schemes_menu(self):
        """Handle schemes management menu"""
        while True:
            choice = self.show_schemes_menu()
            
            if choice == "1":
                self.add_scheme()
            elif choice == "2":
                self.delete_scheme()
            elif choice == "3":
                self.list_schemes()
            elif choice == "0":
                break
            else:
                print("  ❌ خيار غير صحيح (Invalid choice)")
            
            input("\n  اضغط Enter للمتابعة (Press Enter to continue)...")

    def run(self):
        """Main CLI loop"""
        while self.running:
            choice = self.show_main_menu()
            
            if choice == "1":
                self.handle_roots_menu()
            elif choice == "2":
                self.handle_schemes_menu()
            elif choice == "3":
                self.generate_derivatives()
            elif choice == "4":
                self.validate_word()
            elif choice == "5":
                self.identify_word()
            elif choice == "6":
                self.show_statistics()
            elif choice == "7":
                self.search_derivatives()
            elif choice == "0":
                print("\n  👋 شكراً لاستخدامك التطبيق! (Thank you for using the app!)\n")
                self.running = False
            else:
                print("  ❌ خيار غير صحيح (Invalid choice)")
                input("\n  اضغط Enter للمتابعة (Press Enter to continue)...")


def main():
    """Entry point"""
    try:
        cli = SarfCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n  👋 تم الإيقاف (Interrupted)\n")
    except Exception as e:
        print(f"\n  ❌ خطأ: {e}\n")


if __name__ == "__main__":
    main()
