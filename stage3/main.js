const { app, BrowserWindow } = require('electron');
const isDev = require("electron-is-dev")

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
        },
    });
    if(isDev) {
        mainWindow.loadURL("http://localhost:3000/index.html")
    }
    else{
        // Production時のPathは要確認
        mainWindow.loadURL(`file://${__dirname}/..index.html`);
    }
    mainWindow.on("closed",()=>{
        mainWindow=null;
    });
    if(isDev){
        require("electron-reload")(__dirname,{
            electron:require(`${__dirname}/node_modules/electron`)
        })
    }
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});
