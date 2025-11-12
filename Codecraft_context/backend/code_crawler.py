import os
import ast
import json

class CodeCrawler:
    def __init__(self, project_root):
        self.project_root = project_root
        self.code_structure = {}
    
    def find_all_code_files(self):
        """Find ALL code files in the project (Python + Arduino)"""
        code_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                # Look for Python files
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.project_root)
                    code_files.append(relative_path)
                
                #Looking for Arduino files
                elif file.endswith('.ino'):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.project_root)
                    code_files.append(relative_path)
        
        return code_files
    
    def parse_python_file(self, file_path):
        """Read and understand a Python file"""
        full_path = os.path.join(self.project_root, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use AST to understand the code structure
            tree = ast.parse(content)
            
            file_info = {
                'file_path': file_path,
                'classes': {},
                'functions': {},
                'imports': []
            }
    
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    file_info['classes'][class_name] = methods
                
                elif isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    file_info['functions'][func_name] = {
                        'line_number': node.lineno
                    }
                
                # Extract imports
                elif isinstance(node, ast.Import):
                    for name in node.names:
                        file_info['imports'].append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        file_info['imports'].append(f"{module}.{name.name}")
            
            return file_info
            
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None
    
    def parse_arduino_file(self, file_path):
        """Read and understand an Arduino .ino file"""
        full_path = os.path.join(self.project_root, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                'file_path': file_path,
                'type': 'arduino',
                'functions': {},
                'setup_loop': False
            }
            
            # Look for Arduino-specific patterns
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Find setup() and loop() functions
                if line.startswith('void setup()'):
                    file_info['functions']['setup'] = {'line_number': i}
                    file_info['setup_loop'] = True
                elif line.startswith('void loop()'):
                    file_info['functions']['loop'] = {'line_number': i}
                    file_info['setup_loop'] = True
                
                # Find custom functions
                elif line.startswith('void ') and '(' in line and ')' in line:
                    # Extract function name
                    func_declaration = line.split('void ')[1].split('(')[0].strip()
                    if func_declaration and func_declaration not in ['setup', 'loop']:
                        file_info['functions'][func_declaration] = {'line_number': i}
            
            return file_info
            
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None
    
    def build_project_map(self):
        """MAIN FUNCTION: Build the understanding of the whole project"""
        print("🕷️  CodeCrawler is mapping your project...")
        
        files = self.find_all_code_files()
        print(f"📁 Found {len(files)} code files")
        
        for file_path in files:
            print(f"   Scanning: {file_path}")
            
            if file_path.endswith('.py'):
                file_info = self.parse_python_file(file_path)
            elif file_path.endswith('.ino'):
                file_info = self.parse_arduino_file(file_path)  # NEW!
            else:
                continue  # Skip other files
                
            if file_info:
                self.code_structure[file_path] = file_info
        
        # Save the map to JSON file
        with open('project_brain.json', 'w', encoding='utf-8') as f:
            json.dump(self.code_structure, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Project brain built! Analyzed {len(self.code_structure)} files.")
        return self.code_structure
# TEST FUNCTION
def test_crawler():
    """Test our crawler on the EcoPulse project"""
    eco_pulse_path = r"C:\Users\vrawa\Documents\GitHub\Vishesh_Rawal_Labs\Ecopulse"  # Windows
    # eco_pulse_path = "/home/pi/EcoPulse"  # Raspberry Pi
    
    crawler = CodeCrawler(eco_pulse_path)
    project_map = crawler.build_project_map()
    
    # Show what we found
    print("\n📊 PROJECT SUMMARY:")
    for file_path, info in project_map.items():
        print(f"📄 {file_path}:")
        print(f"   Classes: {list(info['classes'].keys())}")
        print(f"   Functions: {list(info['functions'].keys())}")

if __name__ == "__main__":
    test_crawler()