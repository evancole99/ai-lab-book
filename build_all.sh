eval "$(conda shell.bash hook)"
conda activate sqlalchemy
python build_er.py
conda deactivate
jb build --all ../ai-lab-book
