const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow;
let backendProcess;
const PORT = 8000;

function checkBackendHealth(retries = 20, delay = 500) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const interval = setInterval(() => {
      attempts++;
      http.get(`http://127.0.0.1:${PORT}/health`, (res) => {
        if (res.statusCode === 200) {
          clearInterval(interval);
          resolve(true);
        }
      }).on('error', () => {
        if (attempts >= retries) {
          clearInterval(interval);
          reject(new Error('Backend server failed to start within timeout.'));
        }
      });
    }, delay);
  });
}

function startBackend() {
  const pythonExecutable = process.platform === 'win32'
    ? path.join(__dirname, '..', '.venv', 'Scripts', 'python.exe')
    : path.join(__dirname, '..', '.venv', 'bin', 'python');

  const backendScript = path.join(__dirname, '..', 'backend', 'app', 'main.py');

  backendProcess = spawn(pythonExecutable, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', `${PORT}`], {
    cwd: path.join(__dirname, '..', 'backend'),
    env: { ...process.env, PYTHONPATH: path.join(__dirname, '..', 'backend') }
  });

  backendProcess.stdout.on('data', (data) => console.log(`[Backend]: ${data}`));
  backendProcess.stderr.on('data', (data) => console.error(`[Backend Err]: ${data}`));
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1340,
    height: 880,
    minWidth: 1020,
    minHeight: 680,
    title: 'TRINETRA — Modular OSINT & Footprint Intelligence Platform',
    backgroundColor: '#080d1a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  try {
    await checkBackendHealth();
    mainWindow.loadURL(`http://127.0.0.1:${PORT}`);
  } catch (err) {
    dialog.showErrorBox('TRINETRA Initialization Error', err.message);
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
