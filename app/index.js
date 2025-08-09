// Tauri API imports
const { invoke } = window.__TAURI__.tauri;
const { platform, arch, version } = window.__TAURI__.os;
const { appName, appVersion } = window.__TAURI__.app;

// DOM elements
const greetButton = document.getElementById('greet-button');
const infoButton = document.getElementById('info-button');
const output = document.getElementById('output');

// Event listeners
greetButton.addEventListener('click', async () => {
    try {
        const response = await invoke('greet', { name: 'Tauri User' });
        output.innerHTML = `<strong>🎉 ${response}</strong>`;
    } catch (error) {
        output.innerHTML = `<strong>❌ Error:</strong> ${error}`;
    }
});

infoButton.addEventListener('click', async () => {
    try {
        const [platformName, archName, osVersion, name, version] = await Promise.all([
            platform(),
            arch(),
            version(),
            appName(),
            appVersion()
        ]);
        
        output.innerHTML = `
            <div style="text-align: left;">
                <strong>📱 System Info:</strong><br>
                • Platform: ${platformName}<br>
                • Architecture: ${archName}<br>
                • OS Version: ${osVersion}<br>
                • App Name: ${name}<br>
                • App Version: ${version}
            </div>
        `;
    } catch (error) {
        output.innerHTML = `<strong>❌ Error:</strong> ${error}`;
    }
});

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    output.innerHTML = '🚀 App ready! Click a button to test functionality.';
});
