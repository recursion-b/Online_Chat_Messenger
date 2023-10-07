const { app, BrowserWindow } = require('electron');

function createWindow () {
  // ウインドウ作成
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
  });

  // index.htmlの内容でウィンドウ表示
  mainWindow.loadFile('./build/index.html'); // パス変更
}

// Electronの初期化完了時に呼ばれる
app.whenReady().then(() => {
  createWindow();

  // Mac用処理
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  })
});

// (Mac以外は)ウインドウが全部閉じられたら終了
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
