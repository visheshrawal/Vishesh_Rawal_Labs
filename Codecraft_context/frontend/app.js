// Load projects on startup
loadProjects();

async function loadProjects() {
    const response = await fetch('/api/projects');
    const projects = await response.json();
    
    const select = document.getElementById('projectSelect');
    select.innerHTML = '<option value="">Select a project...</option>';
    
    projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project.name;
        option.textContent = project.name;
        select.appendChild(option);
    });
}

async function analyzeProject() {
    const projectPath = document.getElementById('projectPath').value;
    const projectName = document.getElementById('projectName').value;
    
    if (!projectPath || !projectName) {
        alert('Please enter both project path and name!');
        return;
    }
    
    const statusDiv = document.getElementById('projectStatus');
    statusDiv.style.display = 'block';
    statusDiv.textContent = '🕷️ Analyzing project structure...';
    
    try {
        const response = await fetch('/api/analyze_project', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                project_path: projectPath,
                project_name: projectName
            })
        });
        
        const result = await response.json();
        statusDiv.textContent = `✅ ${result.message} (${result.files_analyzed} files analyzed)`;
        
        // Reload projects list
        loadProjects();
        
    } catch (error) {
        statusDiv.textContent = `❌ Error: ${error.message}`;
    }
}

async function askQuestion() {
    const question = document.getElementById('questionInput').value;
    const projectName = document.getElementById('projectSelect').value;
    
    if (!question || !projectName) {
        alert('Please select a project and enter a question!');
        return;
    }
    
    const chatHistory = document.getElementById('chatHistory');
    
    // Add question to chat
    const questionDiv = document.createElement('div');
    questionDiv.className = 'message question';
    questionDiv.textContent = `You: ${question}`;
    chatHistory.appendChild(questionDiv);
    
    // Clear input
    document.getElementById('questionInput').value = '';
    
    try {
        const response = await fetch('/api/ask_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                project_name: projectName
            })
        });
        
        const result = await response.json();
        
        // Add answer to chat
        const answerDiv = document.createElement('div');
        answerDiv.className = 'message answer';
        answerDiv.textContent = `AI: ${result.answer}`;
        chatHistory.appendChild(answerDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
    } catch (error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message answer';
        errorDiv.textContent = `AI: Error - ${error.message}`;
        chatHistory.appendChild(errorDiv);
    }
}