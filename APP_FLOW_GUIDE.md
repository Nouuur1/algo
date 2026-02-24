# 🌟 Maghara Sarf - App Flow Guide

This guide walks you through how the Arabic morphology app works, step-by-step, with code references.

---

## 📋 Table of Contents
1. [App Overview](#app-overview)
2. [Architecture & Data Structures](#architecture--data-structures)
3. [Initialization Flow](#initialization-flow)
4. [Core Features & Routes](#core-features--routes)
5. [Data Operations](#data-operations)

---

## 🎯 App Overview

**Maghara Sarf** is an interactive web application for learning Arabic morphology (As-Sarf). It teaches users about:
- **Roots (الجذور)**: Triliteral Arabic words (3 letters)
- **Schemes/Weights (الأوزان)**: Patterns to generate derivatives
- **Derivatives (المشتقات)**: Words derived from roots using schemes

---

## 🏗️ Architecture & Data Structures

The app uses a **Flask backend** with two main files:

### `app.py` - Routes & API Endpoints
- Handles HTTP requests
- Calls logic layer functions
- Returns JSON responses

### `logic.py` - Core Business Logic
Contains essential data structures:

#### 1. **AVL Binary Search Tree** (For Roots)
- **Line 79-82**: `Node` class defines tree nodes
  - Stores: root (key), left/right children, height, derived_words
  
- **AVL Operations** (Lines 114-210):
  - `insert_root()` - Inserts balanced root
  - `delete_root()` - Removes root while rebalancing
  - `search_root()` - Finds root (O(log n) complexity)
  - `_right_rotate()` / `_left_rotate()` - Rebalancing operations

#### 2. **Hash Table** (For Schemes/Weights)
- **Lines 43-76**: Custom `HashTable` implementation
  - Uses chaining for collision handling
  - `insert()` - Adds scheme
  - `get()` - Retrieves scheme
  - `delete()` - Removes scheme
  - Hash function: sum of character codes modulo table size

#### 3. **Custom Functions** (No built-in len/max allowed)
- **Line 8-23**: `mon_max()` and `ma_longueur()` - Custom implementations

---

## 🚀 Initialization Flow

### Step 1: Server Startup
```
File: app.py, Lines 1-6
├─ Flask app created
├─ SARF_Logic() instantiated
└─ Data loaded from files
```

**Code triggered:**
```python
app = Flask(__name__)                    # Line 3
logic = SARF_Logic()                     # Line 4
logic.load_data('%s', '%s')             # Line 5
```

### Step 2: Data Loading
```
Function: SARF_Logic.load_data() at logic.py, Lines 375-396
├─ Load roots.txt into AVL tree
├─ Load schemes.txt into Hash table
└─ Load derivatives.json
```

**Key operations:**
- **Lines 380-383**: Read roots file, build AVL tree with `insert_root()`
- **Lines 385-390**: Read schemes file, populate hash table with `schemes.insert()`
- **Line 391**: Call `load_derivatives()` to restore word frequencies

---

## 🎮 Core Features & Routes

### Feature 1: 🏠 Home Page
**Route:** `GET /` (Line 8-9 in app.py)
```python
@app.route('/')
def home():
    return render_template('index.html')
```
- Loads main HTML interface

---

### Feature 2: 📊 View All Roots
**Route:** `GET /view_roots` (Lines 11-13)

**Flow:**
1. User clicks "View Roots" button
2. Route handler triggers `view_roots()`
3. Calls `logic.get_all_roots_data()` → **Line 447**: Traverses AVL tree in-order
4. Returns all roots with their derivatives
5. Renders `view_roots.html` with data

---

### Feature 3: 📋 View All Schemes
**Route:** `GET /view_schemes` (Lines 15-17)

**Flow:**
1. Retrieves all schemes from hash table
2. Creates list with scheme name and category
3. Renders `view_schemes.html`

---

### Feature 4: 🪄 Generate All Derivatives
**Route:** `POST /generate_all` (Lines 19-25)

**Step-by-step execution:**

| Step | Code Location | Operation |
|------|--------------|-----------|
| 1 | Line 20 | Extract root from JSON request |
| 2 | Line 21 | Search root in AVL tree via `search_root()` (Line 171) |
| 3 | Line 22 | Check if root exists (return 404 if not) |
| 4 | Line 23 | Populate derivatives with `populate_derivatives()` (Line 222) |
| 5 | Line 24 | Apply each scheme to root via `apply_scheme()` (Line 212) |
| 6 | Line 25 | Return all generated words in JSON |

**Key function:** `apply_scheme()` (Lines 212-220)
- Replaces 'ف' (Fa) → 1st letter of root
- Replaces 'ع' (Ayn) → 2nd letter
- Replaces 'ل' (Lam) → 3rd letter
- Keeps other letters unchanged

**Example:**
- Root: "كتب" (K-T-B)
- Scheme: "فعل"
- Result: "كتب" (original form)

---

### Feature 5: ✅ Verify Morphology
**Route:** `POST /verify` (Lines 27-36)

**Verification Process:**
1. Get word and root from request (Lines 28-29)
2. Search root in AVL tree
3. Apply all schemes to root
4. Check if generated word matches input word
5. If match found:
   - Update word frequency in node (Line 33)
   - Save to derivatives.json
   - Return success with scheme name
6. If no match: Return error

**Code reference:** `verify_morphology()` at Lines 309-324

---

### Feature 6: 🔍 Identify Word Root
**Route:** `POST /identify` (Lines 38-43)

**Reverse Engineering Process:**
1. User provides a word (e.g., "كاتب")
2. Try each scheme to extract possible roots
3. For each character in word:
   - If scheme position is 'ف' → extract 1st root letter
   - If scheme position is 'ع' → extract 2nd root letter
   - If scheme position is 'ل' → extract 3rd root letter
   - Otherwise → must match literally
4. Check if extracted root exists in database
5. Return all valid roots and schemes

**Code reference:** `identify_word()` at Lines 270-307

**Example:**
- Word: "كاتب" (K-A-T-B)
- Try scheme "فاعل" (active participle):
  - Position 0: 'ف' → extract 'ك' (1st root letter)
  - Position 1: 'ا' → must match 'ا' ✓
  - Position 2: 'ع' → extract 'ت' (2nd root letter)
  - Position 3: 'ل' → extract 'ب' (3rd root letter)
- Result: Root "كتب" with scheme "فاعل"

---

### Feature 7: ⚙️ Manage Roots
**Route:** `POST /manage` (Lines 45-61)

**Add Root:**
1. Extract root from request (Line 46)
2. Validate: Must be exactly 3 Arabic letters (Line 48)
3. Insert into AVL tree via `insert_root()` (Line 50)
4. Rebalancing occurs automatically
5. Save to roots.txt (Line 51)

**Delete Root:**
1. Extract root (Line 46)
2. Validate syntax (Line 48)
3. Remove via `delete_root()` (Line 53)
4. Rebalancing occurs automatically
5. Save changes (Line 54)

**Validation:** `is_arabic_triple()` at Line 102

---

### Feature 8: ⚙️ Manage Schemes
**Route:** `POST /add_scheme` (Lines 63-67)

1. Extract scheme name and category
2. Strip diacritics via `strip_tashkeel()` (Line 109)
3. Check if scheme already exists in hash table
4. If new: Insert via `schemes.insert()` (Line 325)
5. Save to schemes.txt

**Delete Scheme:**
**Route:** `POST /delete_scheme` (Lines 69-76)

1. Extract scheme name
2. Delete from hash table via `schemes.delete()` (Line 333)
3. Save changes

**Code references:**
- `add_scheme()` at Lines 319-324
- `delete_scheme()` at Lines 326-331

---

### Feature 9: 📈 Get Statistics
**Route:** `GET /stats` (Line 78)

Returns:
- Total roots count
- Total schemes count
- Total derivatives
- Root with most derivatives
- Max derivative count

**Code reference:** `get_stats()` at Lines 336-353

---

### Feature 10: 🔎 Search Derivatives
**Route:** `POST /search_derivatives` (Lines 80-83)

1. Get search pattern from request
2. Strip diacritics for matching
3. Traverse all roots in AVL tree
4. Check each word's derivatives for pattern match
5. Return matching words with frequencies

**Code reference:** `search_derivatives()` at Lines 355-364

---

## 💾 Data Operations

### Data Persistence Flow

#### **Save Data**
Function: `save_data()` at Lines 408-416

```
get_all_roots_data() → Traverse AVL tree (in-order)
    ↓
Write roots.txt (each root on new line)
    ↓
Write schemes.txt (format: name,category)
    ↓
save_derivatives() → JSON file
```

#### **Load Data**
Function: `load_data()` at Lines 375-396

```
Read roots.txt
    ↓
For each line: insert_root() into AVL tree
    ↓
Read schemes.txt
    ↓
For each line: schemes.insert() into hash table
    ↓
load_derivatives() → Restore word frequencies from JSON
```

#### **Derivative Storage**
- File: `data/derivatives.json`
- Format: `{ "root": { "word1": frequency, "word2": frequency } }`
- Updated when: User verifies a word or generates derivatives

**Code reference:**
- `save_derivatives()` at Lines 418-427
- `load_derivatives()` at Lines 401-406

---

## 🔄 Complete User Journey Example

**Scenario: User generates derivatives for root "كتب"**

### Timeline:

| Step | User Action | Code Triggered | File Modified |
|------|------------|---------------|----|
| 1 | Enters "كتب" in form | - | - |
| 2 | Clicks "Generate" | `POST /generate_all` (Line 19) | - |
| 3 | Backend searches root | `search_root()` (Line 171) | - |
| 4 | Iterates schemes | Loop Line 24 | - |
| 5 | Applies each scheme | `apply_scheme()` (Line 212) | - |
| 6 | Populates node | `populate_derivatives()` (Line 222) | derivatives.json |
| 7 | Returns JSON to frontend | Response Line 25 | - |
| 8 | Browser displays results | JavaScript rendering | - |
| 9 | User clicks word | (Not shown in provided code) | - |
| 10 | Optional: Verify word | `POST /verify` (Line 27) | derivatives.json |
| 11 | Update frequency | Line 33 saves to file | derivatives.json |

---

## 🎯 Key Algorithms Explained

### AVL Tree Rebalancing
When inserting root "ن" into tree [ك, ج, ن]:
1. Recursively insert (Line 151-156)
2. Update height (Line 157)
3. Calculate balance factor (Line 158)
4. Check rotation cases:
   - **LL rotation** (Line 160): `_right_rotate()` (Line 126)
   - **RR rotation** (Line 162): `_left_rotate()` (Line 135)
   - **LR rotation** (Lines 165-167): Left then right
   - **RL rotation** (Lines 168-170): Right then left

**Guarantee:** Tree stays balanced → All operations O(log n)

### Hash Table Collision Resolution
When adding schemes with same hash:
1. Hash function: Sum of character codes % table size (Line 48)
2. Multiple items in bucket (chaining)
3. `insert()` checks bucket for existing key (Lines 54-58)
4. Appends new key-value pair if new (Line 59)

---

## 📝 Summary

The app workflow:
1. ✅ **Initialize** - Load roots (AVL tree), schemes (hash table), derivatives (JSON)
2. ✅ **Generate** - Apply schemes to roots → new derivatives
3. ✅ **Verify** - Check if word matches root+scheme
4. ✅ **Identify** - Reverse process: word → root + scheme
5. ✅ **Manage** - Add/delete roots and schemes
6. ✅ **Persist** - Save all changes to files

**All operations leverage balanced tree and hash table for efficiency!** 🚀
