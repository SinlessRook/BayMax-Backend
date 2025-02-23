# 📖 Project Setup Guide

This guide will walk you through installing all dependencies and setting up the project, including the `script/` and `lib/` folders.

---

## ⚡ 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

---

## 🐍 2. Create and Activate a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

### For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 3. Install Dependencies

Install all project dependencies listed in **`requirements.txt`**:

```bash
pip install -r requirements.txt
```

This will install all required packages for the Flask project, as well as dependencies for the **`script/`** and **`lib/`** folders.

---

## 📂 4. Understanding `script/` and `lib/` Folders

- **`script/`**: Contains custom scripts for running tasks, utilities, or data processing.

- **`lib/`**: Contains shared libraries or modules used across the project.

Ensure both folders are correctly structured and accessible within the Flask app.

---

## ⚙️ 5. Set Python Path (Optional)

To make sure Python can find modules inside `script/` and `lib/`, set the `PYTHONPATH`:

### For Windows:

```bash
set PYTHONPATH=%cd%\lib;%cd%\script
```

### For macOS/Linux:

```bash
export PYTHONPATH=$(pwd)/lib:$(pwd)/script
```

---

## 🚀 6. Running the Flask App

### Set Flask Environment Variables:

```bash
# For macOS/Linux
export FLASK_APP=run.py
export FLASK_ENV=development

# For Windows (CMD)
set FLASK_APP=run.py
set FLASK_ENV=development
```

### Run the Flask App:

```bash
flask run
```

Your Flask app should now be running at [http://localhost:5000](http://localhost:5000) 🚀

---

## ✅ 7. Verify Installations

Run the following script to verify that dependencies and paths are set up correctly:

```bash
python -c "import flask; import sys; print('Flask Version:', flask.__version__); print('PYTHONPATH:', sys.path)"
```

---

