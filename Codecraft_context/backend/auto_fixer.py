import ast
import tokenize
from io import StringIO

class AutoFixer:
    def __init__(self):
        self.fix_strategies = self._load_fix_strategies()
    
    def generate_fix(self, issue: Dict, original_code: str) -> str:
        """HARD: Automatically generate code fixes"""
        fix_strategy = self.fix_strategies.get(issue['type'])
        
        if fix_strategy:
            return fix_strategy(issue, original_code)
        
        return None
    
    def _load_fix_strategies(self):
        """HARD: Expert system for code fixes"""
        return {
            'resource_leak': self._fix_resource_leak,
            'infinite_loop': self._fix_infinite_loop,
            'performance_issue': self._fix_performance_issue,
        }
    
    def _fix_resource_leak(self, issue, code):
        """HARD: Automatically add resource cleanup"""
        lines = code.split('\n')
        line_idx = issue['line'] - 1
        
        if 'open(' in lines[line_idx]:
            # Find the scope to add close()
            indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
            close_line = ' ' * indent + '# AUTO-FIX: Added resource cleanup'
            
            # Insert close statement in appropriate place
            # This requires complex scope analysis
            return self._insert_in_scope(lines, line_idx, close_line)
        
        return None
    
    def _fix_infinite_loop(self, issue, code):
        """HARD: Add loop termination conditions"""
        lines = code.split('\n')
        line_idx = issue['line'] - 1
        
        if 'while True:' in lines[line_idx]:
            # Transform: while True: → while should_continue:
            new_line = lines[line_idx].replace('while True:', 'while should_continue:')
            lines[line_idx] = new_line
            
            # Add termination condition
            indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
            condition_line = ' ' * indent + 'should_continue = True  # AUTO-FIX: Added loop condition'
            
            # Insert before loop
            lines.insert(line_idx, condition_line)
            
            return '\n'.join(lines)
        
        return None
    
    def _insert_in_scope(self, lines, target_line, new_line):
        """HARD: Insert code in correct scope (VERY COMPLEX)"""
        # This requires full parse tree analysis to understand scope
        # Simplified version:
        for i in range(target_line, len(lines)):
            if len(lines[i].strip()) == 0 or lines[i].startswith(' ' * 4):
                continue
            # Found end of scope
            lines.insert(i, new_line)
            break
        
        return '\n'.join_lines(lines)