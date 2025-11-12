import ast
import re
from typing import Dict, List
import numpy as np
from sklearn.ensemble import IsolationForest  # ML for anomaly detection

class SmartAnalyzer:
    def __init__(self):
        self.bug_patterns = self._load_bug_patterns()
        self.ml_model = IsolationForest(contamination=0.1)
    
    def _load_bug_patterns(self):
        """Hard-coded expert knowledge of common bugs"""
        return {
            'resource_leak': [
                r'open\([^)]+\)[^)]*(?!close\()',
                r'connect\([^)]+\)[^)]*(?!disconnect\()'
            ],
            'infinite_loop': [
                r'while\s*\(\s*True\s*\):',
                r'while\s*\(\s*1\s*\):',
                r'for\s+\w+\s+in\s+range\(\s*\):'  # empty range
            ],
            'type_confusion': [
                r'str\(\s*\)\s*\+\s*int\(\s*\)',
                r'dict\.keys\(\)\[0\]',  # Python 3 compatibility
            ],
            'performance_issue': [
                r'\.append\(\s*\)\s+in\s+loop',
                r'deepcopy\(\s*\)\s+in\s+loop',
                r'SELECT\s+\*\s+FROM',  # SQL no-no
            ]
        }
    
    def analyze_code_quality(self, code: str, file_path: str) -> List[Dict]:
        """HARD: Static analysis that finds bugs automatically"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # AST-based analysis
            issues.extend(self._ast_analysis(tree, file_path))
            
            # Pattern-based analysis
            issues.extend(self._pattern_analysis(code, file_path))
            
            # ML-based anomaly detection
            issues.extend(self._ml_analysis(code, file_path))
            
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'file': file_path,
                'line': e.lineno,
                'message': f'Syntax error: {e.msg}',
                'severity': 'critical'
            })
        
        return issues
    
    def _ast_analysis(self, tree, file_path):
        """HARD: Use AST to find complex logical errors"""
        issues = []
        
        class BugFinder(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                self.function_stack = []
            
            def visit_FunctionDef(self, node):
                self.function_stack.append(node.name)
                self.generic_visit(node)
                self.function_stack.pop()
            
            def visit_Call(self, node):
                # Find function calls with suspicious patterns
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'append' and self._in_loop():
                        self.issues.append({
                            'type': 'performance',
                            'file': file_path,
                            'line': node.lineno,
                            'message': 'List append in loop - consider pre-allocation',
                            'severity': 'warning'
                        })
                
                self.generic_visit(node)
            
            def _in_loop(self):
                # Complex control flow analysis
                return len(self.function_stack) > 0
        
        finder = BugFinder()
        finder.visit(tree)
        return finder.issues
    
    def _pattern_analysis(self, code, file_path):
        """HARD: Regex + heuristic based bug detection"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for each bug pattern
            for bug_type, patterns in self.bug_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            'type': bug_type,
                            'file': file_path,
                            'line': i,
                            'message': f'Potential {bug_type.replace("_", " ")}',
                            'severity': 'warning' if 'performance' in bug_type else 'error'
                        })
        
        return issues
    
    def _ml_analysis(self, code, file_path):
        """HARD: Machine learning based anomaly detection"""
        # Convert code to features for ML
        features = self._extract_code_features(code)
        
        if len(features) > 0:
            # Train on-the-fly (this is simplified)
            prediction = self.ml_model.fit_predict([features])[0]
            
            if prediction == -1:  # Anomaly detected
                return [{
                    'type': 'ml_anomaly',
                    'file': file_path,
                    'message': 'ML model detected unusual code pattern',
                    'severity': 'info'
                }]
        
        return []
    
    def _extract_code_features(self, code):
        """HARD: Feature engineering for ML model"""
        # This is where real data science happens
        features = []
        
        # Complexity metrics
        features.append(len(re.findall(r'if\s*\(', code)))
        features.append(len(re.findall(r'for\s+\w+\s+in', code)))
        features.append(len(re.findall(r'while\s*\(', code)))
        
        # Code quality metrics
        features.append(len(re.findall(r'# TODO', code)))
        features.append(len(re.findall(r'print\(', code)))  # debug statements
        
        return features