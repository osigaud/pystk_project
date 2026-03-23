#!/bin/bash

# On determine ou on est (src/agents/team5)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# On definit la destination (src/agents/team5/team5_docs/HTML)
TARGET_DIR="$SCRIPT_DIR/team5_docs/HTML"

# On remonte pour trouver le .venv (my_pystk_project/.venv)
# On part de team5, on remonte 3 fois : team5 -> agents -> src -> projet
VENV_PATH="$SCRIPT_DIR/../../../.venv/bin/activate"

# Activation de l'environnement
if [ -f "$VENV_PATH" ]; then
    echo "--- Activation de l'environnement virtuel ---"
    source "$VENV_PATH"
else
    echo "ERREUR : .venv non trouve dans $VENV_PATH"
    echo "Verifie que ton dossier .venv est bien a la racine du projet."
    read -p "Appuyez sur Entree pour quitter..."
    exit 1
fi

# Creation du dossier de doc
mkdir -p "$TARGET_DIR"

# Preparation des modules pour pydoc
echo "--- Recherche des modules dans team5 ---"
cd "$SCRIPT_DIR/.."  # On va dans src/agents

# On liste les fichiers agent5*.py dans le dossier team5
MODULES=$(ls team5/agent5*.py | sed 's/\.py//' | sed 's/\//./g')
ALL_MODULES="team5 $MODULES"

echo "Modules detectes : $ALL_MODULES"

echo "--- Generation de la documentation ---"
python3 -m pydoc -w $ALL_MODULES
mv team5*.html "$TARGET_DIR/"

echo "--- Succes ---"
echo "Doc generee dans : $TARGET_DIR"

read -p "Appuyez sur Entree pour fermer..."