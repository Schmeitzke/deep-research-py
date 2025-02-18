import os
from pathlib import Path

allowed_extensions = ('.py', '.tsx', '.json', '.ts', '.css', '.html', '.md')  # changed code: added allowed extensions

def print_directory_structure(startpath, output_file):
    output_file.write('Directory Structure:\n')
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d != 'node_modules']  # changed code: exclude node_modules
        files = [f for f in files if f != 'package-lock.json']  # changed code: exclude package-lock.json

        level = root.replace(str(startpath), '').count(os.sep)
        indent = '  ' * level
        output_file.write(f'{indent}{os.path.basename(root)}/\n')
        subindent = '  ' * (level + 1)
        for f in files:
            if f.endswith(allowed_extensions):  # changed code: check allowed extensions
                output_file.write(f'{subindent}{f}\n')

def write_file_contents(startpath, output_file):
    output_file.write('\nFile Contents:\n')
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d != 'node_modules']  # changed code: exclude node_modules
        files = [f for f in files if f != 'package-lock.json']  # changed code: exclude package-lock.json

        for file in files:
            if file.endswith(allowed_extensions):  # changed code: check allowed extensions
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, startpath)
                output_file.write(f'\n{"="*50}\n')
                output_file.write(f'File: {relative_path}\n')
                output_file.write(f'{"="*50}\n\n')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        output_file.write(f.read())
                except Exception as e:
                    output_file.write(f'Error reading file: {str(e)}\n')

def main():
    # Get the directories to scan: src and frontend directories
    current_dir = Path(__file__).parent
    src_dir = current_dir / 'deep_research'
    frontend_dir = current_dir / 'deep_research_gui'  # changed code: added frontend directory
    db_dir = current_dir / 'deep_research_db'  # changed code: added db directory
    config = current_dir / 'config_all'  # changed code: added config directory
    
    output_path = current_dir / 'source_code.txt'
    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for directory in [src_dir, frontend_dir, db_dir, config]:  # changed code: iterate both directories
            if directory.exists():
                print_directory_structure(str(directory), output_file)
                write_file_contents(str(directory), output_file)
            else:
                output_file.write(f'\nDirectory not found: {directory}\n')

if __name__ == '__main__':
    main()