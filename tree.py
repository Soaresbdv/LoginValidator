import os
from pathlib import Path

def generate_project_tree(start_path='.', output_file='project_tree.txt', 
                         ignore_dirs=None, ignore_files=None):
    """
    Gera a estrutura de diretórios do projeto, ignorando pastas/arquivos específicos.
    
    Args:
        start_path (str): Pasta raiz para começar (padrão: diretório atual)
        output_file (str): Arquivo de saída (padrão: 'project_tree.txt')
        ignore_dirs (list): Pastas a ignorar
        ignore_files (list): Arquivos a ignorar
    """
    if ignore_dirs is None:
        ignore_dirs = ['__pycache__', '.git', '.idea', 'venv', 'env', 'node_modules']
    
    if ignore_files is None:
        ignore_files = ['.DS_Store', '.env', '*.pyc']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(start_path):
            # Remove pastas ignoradas
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            level = root.replace(start_path, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                if not any(file.endswith(ext) for ext in ignore_files if '*' not in ext) and \
                   not any(file == pattern for pattern in ignore_files if '*' in pattern):
                    f.write(f"{subindent}{file}\n")

if __name__ == "__main__":
    generate_project_tree()
    print("✅ Estrutura do projeto salva em 'project_tree.txt'")