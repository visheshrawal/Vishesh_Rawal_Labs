from flask import Flask, render_template, request, jsonify
import os
import json
from backend.code_crawler import CodeCrawler
from backend.ai_helper import AIHelper

app = Flask(__name__)

class ProjectManager:
    def __init__(self):
        self.projects_dir = "projects"
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def get_projects(self):
        """Get all saved projects"""
        projects = []
        for project_name in os.listdir(self.projects_dir):
            project_path = os.path.join(self.projects_dir, project_name)
            if os.path.isdir(project_path):
                projects.append({
                    'name': project_name,
                    'brain_file': os.path.join(project_path, 'project_brain.json')
                })
        return projects

project_manager = ProjectManager()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = project_manager.get_projects()
    return jsonify(projects)

@app.route('/api/analyze_project', methods=['POST'])
def analyze_project():
    data = request.json
    project_path = data['project_path']
    project_name = data.get('project_name', 'default_project')
    
    # Create project directory
    project_dir = os.path.join('projects', project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Build project brain
    crawler = CodeCrawler(project_path)
    project_map = crawler.build_project_map()
    
    # Save to project-specific brain file
    brain_file = os.path.join(project_dir, 'project_brain.json')
    with open(brain_file, 'w') as f:
        json.dump(project_map, f, indent=2)
    
    return jsonify({
        'status': 'success',
        'message': f'Project {project_name} analyzed successfully!',
        'files_analyzed': len(project_map)
    })

@app.route('/api/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    question = data['question']
    project_name = data['project_name']
    
    brain_file = os.path.join('projects', project_name, 'project_brain.json')
    ai = AIHelper(brain_file)
    answer = ai.ask_question(question)
    
    return jsonify({
        'question': question,
        'answer': answer
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)