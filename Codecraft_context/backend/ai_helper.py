import json
import subprocess
import os
import requests

class AIHelper:
    def __init__(self, project_brain_file='project_brain.json'):
        self.project_brain_file = project_brain_file
        self.project_map = self.load_project_map()
        self.ollama_url = "http://localhost:11434/api/generate"
    
    def load_project_map(self):
        """Load the project brain we built"""
        try:
            with open(self.project_brain_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Project brain not found! Run the crawler first.")
            return {}
    
    def get_intelligent_context(self, question):
        """SMART: Only send relevant code based on the question"""
        context_parts = []
        
        # Analyze question to determine what's relevant
        question_lower = question.lower()
        
        for file_path, info in self.project_map.items():
            file_relevance_score = 0
            
            # Check if question mentions specific components
            if any(word in question_lower for word in ['led', 'display', 'matrix', 'max7219']):
                if 'MAX7219' in str(info.get('classes', {})):
                    file_relevance_score += 10
                if any('display' in func.lower() for func in info.get('functions', {})):
                    file_relevance_score += 5
            
            if any(word in question_lower for word in ['sensor', 'moisture', 'temperature', 'dht']):
                if any('sensor' in func.lower() for func in info.get('functions', {})):
                    file_relevance_score += 10
                if any('calculate' in func.lower() for func in info.get('functions', {})):
                    file_relevance_score += 5
            
            if any(word in question_lower for word in ['web', 'flask', 'server', 'route']):
                if any('route' in func.lower() for func in info.get('functions', {})):
                    file_relevance_score += 10
                if 'Flask' in str(info.get('imports', [])):
                    file_relevance_score += 5
            
            # Only include relevant files
            if file_relevance_score > 0:
                context_parts.append(f"\n--- {file_path} (relevance: {file_relevance_score}) ---")
                
                if info.get('classes'):
                    context_parts.append(f"Classes: {list(info['classes'].keys())}")
                if info.get('functions'):
                    context_parts.append(f"Functions: {list(info['functions'].keys())}")
        
        return "\n".join(context_parts) if context_parts else "No specific context found for this question."
    
    def ask_ollama(self, question, context):
        """ACTUAL OLLAMA INTEGRATION - THIS IS WHERE THE MAGIC HAPPENS"""
        prompt = f"""You are CodeCraft Context, an expert AI assistant for understanding codebases.

PROJECT STRUCTURE:
{context}

USER QUESTION: {question}

IMPORTANT INSTRUCTIONS:
- Be SPECIFIC and mention exact file names, function names, and class names from the project structure above
- Give ACTIONABLE advice - tell the user exactly what to change and where
- If you're not sure about something, say so - don't hallucinate
- Focus on the architecture and relationships between components

ANSWER:"""
        
        try:
            # OLLAMA API CALL
            payload = {
                "model": "codellama:7b",
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['response'].strip()
            else:
                return f"❌ Ollama error: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Ollama. Make sure it's running with 'ollama serve'"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def ask_question(self, question):
        """Main function to ask questions about the project"""
        if not self.project_map:
            return "❌ No project brain found. Please analyze a project first!"
        
        print(f"🔍 Analyzing: '{question}'")
        context = self.get_intelligent_context(question)
        
        print("🤖 Consulting AI brain...")
        answer = self.ask_ollama(question, context)
        
        return answer

# TEST WITH REAL OLLAMA
def test_real_ai():
    """Test our REAL AI integration"""
    print("🧪 TESTING REAL OLLAMA INTEGRATION...")
    
    ai = AIHelper('projects/ecopulse/project_brain.json')
    
    test_questions = [
        "How does the LED display work in this project?",
        "Where is the plant mood calculation logic?",
        "What's the main entry point of the application?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"🎯 TEST {i}: {question}")
        print(f"{'='*60}")
        
        answer = ai.ask_question(question)
        print(f"💡 ANSWER:\n{answer}")

if __name__ == "__main__":
    test_real_ai()