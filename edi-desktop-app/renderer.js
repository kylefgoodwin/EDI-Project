const { ipcRenderer } = require('electron');

const ediInput = document.getElementById('ediInput');
const results = document.getElementById('results');
const aiResults = document.getElementById('aiResults');
const processBtn = document.getElementById('processBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');

function syntaxHighlight(json) {
    if (typeof json !== 'string') json = JSON.stringify(json, null, 2);
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'json-number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) cls = 'json-key';
            else cls = 'json-string';
        } else if (/true|false/.test(match)) cls = 'json-boolean';
        else if (/null/.test(match)) cls = 'json-null';
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

clearBtn.addEventListener('click', () => {
    ediInput.value = '';
    results.innerHTML = '';
    aiResults.innerHTML = '<p class="text-gray-600 italic mt-10 text-center">Waiting for analysis...</p>';
});

// RAW PARSE BUTTON (Fast, no AI)
processBtn.addEventListener('click', async () => {
    const rawData = ediInput.value;
    if (!rawData.trim()) return;
    results.innerHTML = '<span class="text-blue-400">Parsing...</span>';
    
    try {
        // Send command: 'parse'
        const data = await ipcRenderer.invoke('parse-edi', { content: rawData, command: 'parse' });
        results.innerHTML = syntaxHighlight(data);
    } catch (err) {
        results.innerText = "Error: " + err;
    }
});

// ANALYZE BUTTON (Slower, calls AI)
analyzeBtn.addEventListener('click', async () => {
    const rawData = ediInput.value;
    if (!rawData.trim()) return;
    
    aiResults.innerHTML = '<span class="text-purple-400 animate-pulse">AI is thinking...</span>';
    results.innerHTML = '<span class="text-gray-500">Parsing structure for AI...</span>';

    try {
        // Send command: 'analyze'
        const data = await ipcRenderer.invoke('parse-edi', { content: rawData, command: 'analyze' });
        
        // 1. Show the JSON (it comes back inside the data object now)
        if (data.parsed) {
            results.innerHTML = syntaxHighlight(data.parsed);
        }

        // 2. Show the AI Text
        if (data.ai_analysis) {
            aiResults.innerHTML = data.ai_analysis;
        } else {
            aiResults.innerHTML = "No AI response.";
        }
    } catch (err) {
        aiResults.innerHTML = '<span class="text-red-400">AI Error: ' + err + '</span>';
    }
});

class EDICloudClient {
    constructor(baseUrl = "http://127.0.0.1:8000") {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem("edi_token");
    }

    async login(username, password) {
        // FastAPI expects form-data for OAuth2 login
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${this.baseUrl}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!response.ok) {
            throw new Error("Login failed");
        }

        const data = await response.json();
        this.token = data.access_token;
        localStorage.setItem("edi_token", this.token);
        return true;
    }

    async analyze(ediContent) {
        if (!this.token) {
            throw new Error("Please log in first.");
        }

        const response = await fetch(`${this.baseUrl}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify({ content: ediContent })
        });

        if (response.status === 401) {
            this.logout();
            throw new Error("Session expired. Please log in again.");
        }
        
        if (response.status === 403) {
            throw new Error("Upgrade Required: You need a Pro subscription.");
        }

        return await response.json();
    }

    logout() {
        this.token = null;
        localStorage.removeItem("edi_token");
    }
}