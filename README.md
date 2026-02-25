# Maghara Sarf -- Arabic Morphology Engine

Educational web application for learning Arabic morphology (As-Sarf).\
The system manages Arabic triliteral roots, morphological schemes
(أوزان), and generates valid derivatives.

------------------------------------------------------------------------

## Features

### Root Management

-   Store and search Arabic triliteral roots using an AVL tree.
-   Add or delete roots dynamically.

### Scheme Management

-   Store morphological schemes in a manually implemented hash table.
-   Fast access for word generation.

### Word Generation

-   Generate derived words from a valid 3-letter root.
-   Apply morphological patterns algorithmically.

### Word Validation

-   Check if a word belongs to a root according to stored schemes.

### Arabic Text Display (CLI Support)

-   Proper right-to-left rendering in terminal.

------------------------------------------------------------------------

## Installation

### 1. Clone the repository

``` bash
git clone <your-repository-url>
cd <project-folder>
```

### 2. Create a virtual environment

Linux / macOS:

``` bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
pip install arabic-reshaper python-bidi
```

#### Why these libraries?

**arabic-reshaper**\
Arabic letters change shape depending on their position in the word.\
This library reshapes characters correctly so they display properly
outside browsers (like in CLI).

**python-bidi**\
Handles bidirectional text rendering.\
It ensures Arabic (RTL) is displayed correctly when mixed with
left-to-right text in the terminal.

These are necessary for correct Arabic visualization in the command-line
interface.

------------------------------------------------------------------------

## Project Structure

. ├── app.py ├── cli.py ├── cli_final.py ├── logic.py ├──
requirements.txt ├── APP_FLOW_GUIDE.md ├── README.md │ ├── data/ │ ├──
roots.txt │ ├── schemes.txt │ └── derivatives.json │ ├── templates/ │
├── favicon.png └── .venv/

------------------------------------------------------------------------

## Main Files

-   **app.py**\
    Entry point for running the application.

-   **cli.py / cli_final.py**\
    Command-line interface for interacting with roots and schemes.

-   **logic.py**\
    Core engine:

    -   AVL tree for root storage
    -   Custom hash table for schemes
    -   Morphological generation logic

-   **data/roots.txt**\
    Stores Arabic triliteral roots.

-   **data/schemes.txt**\
    Stores morphological patterns (أوزان).

-   **data/derivatives.json**\
    Stores generated derivatives and related data.

-   **templates/**\
    HTML templates (if running as a web interface).

------------------------------------------------------------------------

## Run the Application

CLI version: python cli_final.py

Or: python app.py
