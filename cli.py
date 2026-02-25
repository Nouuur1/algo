#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Command-Line Interface for Maghara Sarf
Allows users to manage roots, schemes, and generate/validate derivatives
"""

from email.mime import text

from logic import SARF_Logic
import os
import re
import arabic_reshaper
from bidi.algorithm import get_display

class SarfCLI:
    def __init__(self):
        """Initialize CLI with logic engine"""
        self.logic = SARF_Logic()
        self.logic.load_data('data/roots.txt', 'data/schemes.txt')
        self.running = True

    LRM = "\u200E"   # Left-to-Right Mark
    RLM = "\u200F"   # Right-to-Left Mark

    _AR_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
    _EN_PAREN_RE = re.compile(r'\([^\)]*[A-Za-z0-9][^\)]*\)')  # parentheses containing ASCII
    _EN_RUN_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9\s\-_/.:,+]*')  # loose ASCII run

    def ar(self, text: str) -> str:
        """Return a terminal-friendly display string for Arabic/English mixed text."""
        if not text:
            return text

        # Fix Arabic runs first
        def _fix_ar(match: re.Match) -> str:
            s = match.group(0)
            s = arabic_reshaper.reshape(s)
            s = get_display(s)
            return f"{self.RLM}{s}{self.RLM}"

        out = self._AR_RE.sub(_fix_ar, text)

        # Stabilize English parentheses so punctuation doesn't jump around
        out = self._EN_PAREN_RE.sub(lambda m: f"{self.LRM}{m.group(0)}{self.LRM}", out)

        # Stabilize remaining English runs (keeps numbers and words in expected LTR order)
        out = self._EN_RUN_RE.sub(lambda m: f"{self.LRM}{m.group(0)}{self.LRM}", out)

        return out

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*50)
        print(f"  {self.ar(title)}")
        print("="*50)

    def print_menu(self, options):
        """Print menu options"""
        for key, value in options.items():
            print(f"  {key}. {self.ar(value)}")
        print()
    def aprint(self, text, **kwargs):
        print(self.ar(text), **kwargs)

    # ════════════════════════════════════════════════════════════════
    # ROOT MANAGEMENT
    # ════════════════════════════════════════════════════════════════

    def add_root(self):
        """Add a new root to the database"""
        self.print_header("إضافة جذر جديد (Add New Root)")
        root = input(self.ar("  أدخل الجذر (Enter root - 3 Arabic letters): ")).strip()
        
        if not self.logic.is_arabic_triple(root):
            self.aprint("  ❌ خطأ: يجب أن يكون الجذر 3 أحرف عربية (Error: Must be 3 Arabic letters)")
        
            return
        
        if self.logic.search_root(self.logic.root_tree, root):
            self.aprint(f"  ❌ الجذر '{root}' موجود بالفعل (Root already exists)")
            return
        
        self.logic.root_tree = self.logic.insert_root(self.logic.root_tree, root)
        self.logic.save_data()
        self.aprint(f"  ✅ تمت إضافة الجذر '{root}' بنجاح (Root added successfully)")

    def delete_root(self):
        """Delete a root from the database"""
        self.print_header("حذف جذر (Delete Root)")
        root = input(self.ar("  أدخل الجذر المراد حذفه (Enter root to delete): ")).strip()
        
        if not self.logic.is_arabic_triple(root):
            self.aprint("  ❌ خطأ: يجب أن يكون الجذر 3 أحرف عربية (Error: Must be 3 Arabic letters)")
            return
        
        if not self.logic.search_root(self.logic.root_tree, root):
            self.aprint(f"  ❌ الجذر '{root}' غير موجود (Root not found)")
            return
        
        self.logic.root_tree = self.logic.delete_root(self.logic.root_tree, root)
        self.logic.save_data()
        self.aprint(f"  ✅ تم حذف الجذر '{root}' بنجاح (Root deleted successfully)")

    def search_root(self):
        """Search for a root"""
        self.print_header("بحث عن جذر (Search Root)")
        root = input(self.ar("  أدخل الجذر المراد البحث عنه (Enter root to search): ")).strip()
        
        node = self.logic.search_root(self.logic.root_tree, root)
        if node:
            self.aprint(f"  ✅ الجذر '{root}' موجود (Root found)")
            if node.derived_words:
                self.aprint(f"  📊 عدد المشتقات: {len(node.derived_words)} derivatives")
                self.aprint("  المشتقات (Derivatives):")
                for word, freq in list(node.derived_words.items())[:5]:  # Show first 5
                    self.aprint(f"    - {word} (frequency: {freq})")
                if len(node.derived_words) > 5:
                    self.aprint(f"    ... و {len(node.derived_words) - 5} مشتقات أخرى")
        else:
            self.aprint(f"  ❌ الجذر '{root}' غير موجود (Root not found)")

    def list_roots(self):
        """List all roots in database"""
        self.print_header("قائمة جميع الجذور (List All Roots)")
        roots_data = self.logic.get_all_roots_data(self.logic.root_tree, [])
        
        if not roots_data:
            self.aprint("  ⚠️ لا توجد جذور في قاعدة البيانات (No roots in database)")
            return
        
        self.aprint(f"  📚 عدد الجذور: {len(roots_data)} roots\n")
        for idx, item in enumerate(roots_data, 1):
            root = item['root']
            derivs_count = len(item['derivatives'])
            self.aprint(f"  {idx:2}. {root} - {derivs_count} مشتقات (derivatives)")
        
        self.aprint(f"\n  المجموع: {len(roots_data)} جذور (Total)")

    # ════════════════════════════════════════════════════════════════
    # SCHEME MANAGEMENT
    # ════════════════════════════════════════════════════════════════

    def add_scheme(self):
        """Add a new scheme/weight"""
        self.print_header("إضافة وزن جديد (Add New Scheme)")
        name = input(self.ar("  أدخل الوزن (Enter scheme - e.g., فعل): ")).strip()
        if not name:
            self.aprint("  ❌ الحقل مطلوب (Field required)")
            return
        
        category = input(self.ar("  أدخل الفئة (Enter category - default: عام): ")).strip() or "عام"
        
        if self.logic.add_scheme(name, category):
            self.aprint(f"  ✅ تمت إضافة الوزن '{name}' بفئة '{category}' بنجاح")
        else:
            print(f"  ❌ الوزن '{name}' موجود بالفعل (Scheme already exists)")

    def delete_scheme(self):
        """Delete a scheme"""
        self.print_header("حذف وزن (Delete Scheme)")
        name = input(self.ar("  أدخل الوزن المراد حذفه (Enter scheme to delete): ")).strip()
        
        if self.logic.delete_scheme(name):
            self.aprint(f"  ✅ تم حذف الوزن '{name}' بنجاح (Scheme deleted)")
        else:
            self.aprint(f"  ❌ الوزن '{name}' غير موجود (Scheme not found)")

    def list_schemes(self):
        """List all schemes"""
        self.print_header("قائمة جميع الأوزان (List All Schemes)")
        schemes_list = [(name, info['cat']) for name, info in self.logic.schemes.items()]
        
        if not schemes_list:
            self.aprint("  ⚠️ لا توجد أوزان في قاعدة البيانات (No schemes in database)")
            return
        
        self.aprint(f"  📚 عدد الأوزان: {len(schemes_list)} schemes\n")
        
        # Group by category
        categories = {}
        for name, cat in schemes_list:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)
        
        for cat, names in sorted(categories.items()):
            self.aprint(f"  📁 الفئة: {cat}")
            for idx, name in enumerate(names, 1):
                self.aprint(f"     {idx}. {name}")
            self.aprint("")

    # ════════════════════════════════════════════════════════════════
    # GENERATION & VALIDATION
    # ════════════════════════════════════════════════════════════════

    def generate_derivatives(self):
        self.print_header("توليد المشتقات (Generate Derivatives)")

        try:
            root = input(self.ar("  أدخل الجذر (Enter root): ")).strip()

            if not self.logic.is_arabic_triple(root):
                self.aprint("  ❌ خطأ: يجب أن يكون الجذر 3 أحرف عربية (Error: Must be 3 Arabic letters)", flush=True)
                return

            node = self.logic.search_root(self.logic.root_tree, root)
            if not node:
                self.aprint(f"  ❌ الجذر '{root}' غير موجود (Root not found)", flush=True)
                return

            # Populate/refresh derivatives in the node (if your logic stores them)
            self.logic.populate_derivatives(root)

            schemes_list = list(self.logic.schemes.keys())
            if not schemes_list:
                self.aprint("  ⚠️ لا توجد أوزان متاحة (No schemes available)", flush=True)
                return

            self.aprint(f"\n  📋 الأوزان المتاحة ({len(schemes_list)} available):", flush=True)
            for idx, scheme in enumerate(schemes_list, 1):
                self.aprint(f"     {idx}. {scheme}", flush=True)

            self.aprint("\n  0. توليد جميع المشتقات (Generate all)", flush=True)
            choice = input(self.ar("\n  اختر رقماً أو اضغط Enter (Select number or press Enter): ")).strip()

            results = []

            if choice == "" or choice == "0":
                for scheme in schemes_list:
                    word = self.logic.apply_scheme(root, scheme)
                    if word:
                        results.append((scheme, word))
            else:
                try:
                    idx = int(choice) - 1
                except ValueError:
                    self.aprint("  ❌ أدخل رقماً صحيحاً (Enter a valid number)", flush=True)
                    return

                if idx < 0 or idx >= len(schemes_list):
                    self.aprint("  ❌ اختيار غير صحيح (Invalid choice)", flush=True)
                    return

                scheme = schemes_list[idx]
                word = self.logic.apply_scheme(root, scheme)
                if word:
                    results = [(scheme, word)]

            if results:
                self.aprint(f"\n  ✅ المشتقات المولدة ({len(results)}):", flush=True)
                for scheme, word in results:
                    self.aprint(f"     {word} ← {scheme}", flush=True)
            else:
                self.aprint("  ⚠️ لم يتم توليد أي مشتقات (No derivatives generated)", flush=True)

        finally:
            # Plain pause (no self.ar), so it can't be affected by RTL helpers.
            input("\n  Press Enter to return...")
    def validate_word(self):
        self.print_header("التحقق من المشتق (Validate Derivative)")

        word = input(self.ar("  أدخل الكلمة (Enter word): ")).strip()
        if not word:
            self.aprint("  ❌ الحقل مطلوب (Field required)")
            input(self.ar("\n  اضغط Enter للعودة للقائمة (Press Enter to return)..."))
            return

        root = input(self.ar("  أدخل الجذر (Enter root): ")).strip()
        if not self.logic.is_arabic_triple(root):
            self.aprint("  ❌ خطأ: يجب أن يكون الجذر 3 أحرف عربية (Error: Must be 3 Arabic letters)")
            input(self.ar("\n  اضغط Enter للعودة للقائمة (Press Enter to return)..."))
            return

        ok, scheme = self.logic.verify_morphology(word, root)

        if ok:
            self.aprint(f"\n  ✅ صحيح! (Valid!)")
            self.aprint(f"     الكلمة: {word}")
            self.aprint(f"     الجذر: {root}")
            self.aprint(f"     الوزن: {scheme}")

            # Show word frequency (if stored)
            node = self.logic.search_root(self.logic.root_tree, root)
            if node and word in node.derived_words:
                freq = node.derived_words[word]
                self.aprint(f"     التكرار: {freq} times")
        else:
            self.aprint(f"\n  ❌ غير صحيح (Invalid!)")
            self.aprint(f"     الكلمة '{word}' لا تنتمي إلى الجذر '{root}'")
            self.aprint(f"     بناءً على الأوزان المتاحة")

        input(self.ar("\n  اضغط Enter للعودة للقائمة (Press Enter to return)..."))
    
    def identify_word(self):
        self.print_header("تحديد الجذر من الكلمة (Identify Root from Word)")

        word = input(self.ar("  أدخل الكلمة (Enter word): ")).strip()
        if not word:
            self.aprint("  ❌ الحقل مطلوب (Field required)")
            input(self.ar("\n  اضغط Enter للعودة للقائمة (Press Enter to return)..."))
            return

        # Expecting something like: [{'root': 'كتب', 'scheme': 'فاعل'}, ...]
        results = self.logic.identify_word(word)

        if results:
            self.aprint(f"\n  ✅ تحليل الكلمة '{word}' (Analysis):")
            for item in results:
                root = item.get("root")
                scheme = item.get("scheme")

                self.aprint(f"\n     الجذر: {root}  →  الوزن: {scheme}")

                # Show other words from the same root (family words)
                family = []

                # Option A: if your logic has a direct method, use it
                if hasattr(self.logic, "generate_all_derivatives"):
                    try:
                        # expected: list of (scheme_name, derived_word)
                        family = self.logic.generate_all_derivatives(root) or []
                    except Exception:
                        family = []
                else:
                    # Option B: generate using schemes + apply_scheme
                    schemes_list = list(self.logic.schemes.keys()) if hasattr(self.logic, "schemes") else []
                    for s_name in schemes_list:
                        s_word = self.logic.apply_scheme(root, s_name)
                        if s_word:
                            family.append((s_name, s_word))

                if family:
                    self.aprint(f"     كلمات أخرى من نفس العائلة '{root}':")
                    for s_name, s_word in family[:8]:
                        marker = " ◄" if s_word == word else ""
                        self.aprint(f"       • {s_name} → {s_word}{marker}")
                else:
                    self.aprint(f"     ⚠️ لا توجد مشتقات متاحة لعرضها للجذر '{root}' (No family words available)")
        else:
            self.aprint(f"\n  ❌ الكلمة '{word}' غير معروفة (Word not recognized)")

        input(self.ar("\n  اضغط Enter للعودة للقائمة (Press Enter to return)..."))

    # ════════════════════════════════════════════════════════════════
    # STATISTICS & UTILITIES
    # ════════════════════════════════════════════════════════════════

    def show_statistics(self):
        """Display database statistics"""
        self.print_header("الإحصائيات (Statistics)")
        stats = self.logic.get_stats()

        self.aprint(f"  📊 إحصائيات قاعدة البيانات:")
        self.aprint(f"     • عدد الجذور: {stats['roots']} roots")
        self.aprint(f"     • عدد الأوزان: {stats['schemes']} schemes")
        self.aprint(f"     • إجمالي المشتقات: {stats['total_derivatives']} derivatives")
        if stats.get('max_derivatives_root'):
            self.aprint(f"     • جذر به أكثر مشتقات: {stats['max_derivatives_root']}")
            self.aprint(f"     • عدد مشتقاته: {stats['max_derivatives_count']}")

        input(self.ar("\n  اضغط Enter للعودة للقائمة (Press Enter to return)..."))

    def search_derivatives(self):
        """Search for derivatives by pattern"""
        self.print_header("البحث عن المشتقات (Search Derivatives)")
        pattern = input(self.ar("  أدخل نمط البحث (Enter search pattern): ")).strip()

        if not pattern:
            self.aprint("  ❌ النمط مطلوب (Pattern required)")
            input(self.ar("\n  اضغط Enter للعودة للقائمة (Press Enter to return)..."))
            return

        results = self.logic.search_derivatives(pattern)

        if results:
            self.aprint(f"\n  ✅ تم العثور على {len(results)} نتيجة (Found {len(results)} result(s)):\n")
            results.sort(key=lambda x: x.get('freq', 0), reverse=True)

            for idx, result in enumerate(results[:10], 1):
                self.aprint(f"     {idx}. {result['word']} ← {result['root']} (freq: {result.get('freq', 0)})")

            if len(results) > 10:
                self.aprint(f"     ... و {len(results) - 10} نتائج أخرى (and {len(results) - 10} more)")
        else:
            self.aprint("  ❌ لم يتم العثور على نتائج (No results found)")

        input(self.ar("\n  اضغط Enter للعودة للقائمة (Press Enter to return)..."))
    # ════════════════════════════════════════════════════════════════
    # MAIN MENU
    # ════════════════════════════════════════════════════════════════

    def show_main_menu(self):
        """Display main menu"""
        self.clear_screen()
        self.print_header("مغارة الكلمات - Maghara Sarf 🌟")
        self.aprint(f"  {self.ar('أهلاً بك في تطبيق تعليمي للصرف العربي')}")
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
        return input(self.ar("  اختر خياراً (Choose option): ")).strip()

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
        return input(self.ar("  اختر خياراً (Choose option): ")).strip()

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
        return input(self.ar("  اختر خياراً (Choose option): ")).strip()

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
                self.aprint("  ❌ خيار غير صحيح (Invalid choice)")
            
            input(self.ar("\n  اضغط Enter للمتابعة (Press Enter to continue)..."))

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
                self.aprint("  ❌ خيار غير صحيح (Invalid choice)")
            
            input(self.ar("\n  اضغط Enter للمتابعة (Press Enter to continue)..."))

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
                self.aprint("\n  👋 شكراً لاستخدامك التطبيق! (Thank you for using the app!)\n")
                self.running = False
            else:
                self.aprint("  ❌ خيار غير صحيح (Invalid choice)")
                input(self.ar("\n  اضغط Enter للمتابعة (Press Enter to continue)..."))


def main():
    """Entry point"""
    try:
        cli = SarfCLI()
        cli.run()
    except KeyboardInterrupt:
        cli.aprint("\n\n  👋 تم الإيقاف (Interrupted)\n")
    except Exception as e:
        cli.aprint(f"\n  ❌ خطأ: {e}\n")


if __name__ == "__main__":
    main()
