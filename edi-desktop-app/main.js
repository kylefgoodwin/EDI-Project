const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
const Store = require('electron-store');

const store = new Store();

function createWindow() {
  const win = new BrowserWindow({
    width: 1400, // Wider for the split screen
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    backgroundColor: '#1e1e1e' 
  });

  win.loadFile('index.html');
}

app.whenReady().then(createWindow);

// --- LICENSE VERIFICATION ---
ipcMain.handle('verify-license', async (event, licenseKey) => {
    // DEV BACKDOOR
    if (licenseKey === 'DEV-KEY-1234') {
        store.set('license_key', licenseKey); 
        return { success: true, message: "Dev Mode Activated!" };
    }
    // ... (Keep your existing Gumroad logic here) ...
    return { success: true }; 
});

// --- UPDATED PARSING HANDLER ---
ipcMain.handle('parse-edi', async (event, payload) => {
  // payload is now: { content: "...", command: "parse" | "analyze" }

  // 1. License Check
  if (!store.get('license_key')) {
      throw new Error("Please activate your license first.");
  }

  let options = {
    mode: 'text',
    pythonPath: 'python3', // Ensure python3 is in your system PATH
    scriptPath: path.join(__dirname, 'python'), // Or just __dirname depending on folder structure
    args: []
  };

  return new Promise((resolve, reject) => {
    // Note: If server.py is in root, use 'server.py'. If in python folder, use 'python/server.py'
    let pyshell = new PythonShell('server.py', options);
    
    // Send the full object (content + command)
    pyshell.send(JSON.stringify(payload));

    pyshell.on('message', function (message) {
      try {
        resolve(JSON.parse(message));
      } catch (e) {
        reject("Failed to parse Python output");
      }
    });

    pyshell.end(function (err) {
      if (err) reject(err);
    });
  });
});