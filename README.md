# Online Chat Messenger
## リンクと起動方法
### リンク
[react-electron-app-darwin-x64-0.1.0.zip](https://drive.google.com/file/d/1wir_OvYZX8QBIex5TKCJWEu6cKehPHtd/view?usp=sharing)
### 起動方法
https://support.apple.com/ja-jp/guide/mac-help/mh40616/mac

## Description
Node.jsでソケットを通じて非同期の通信を行うチャットアプリケーションを作成しました。

## 使用技術
使用技術 Javascript/React/Node.js/socket.io

## 期間
2023年9月23日から2週間。3名で開発しました。

## 作成の経緯
クライアントサーバ分散型アプリケーションを作成して、サーバー操作の基本を身に着けたいと思ったからです。

また、自分自身で低レベルネットワーキングをアプリケーションにすることで、ネットワーキングの基礎の知識・技術の獲得を目標としました。

## こだわった点
### ①操作性が高いUI
初めて利用する人でも簡単に利用できるようなUIを意識して作成しました。

### ②オブジェクト指向の設計
クライアントの情報をまとめてオブジェクト化して情報を扱いやすくしました。

チャットルームクラスを作成して、チャットルーム別にパスワードやクライアント情報を持たせることで、単一責任の原則に従うような設計にしました。

### ③アプリのセキュリティ
チャットルームにパスワードの機能を実装して、アプリケーションとしてのセキュリティ部分も考慮しました。

## これからの改善点、拡張案
メッセージの暗号化を実装する予定でしたが、ライブラリを上手く読み込めず実装ができなかったので、原因を見つけて実装したいです。

## Usage
ユーザー名、部屋の名前、部屋のパスワードを入力。

Icon Imageに画像をドラッグアンドドロップすると、自分のアイコン画像を設定できます。

新しく部屋を作成したい場合はCreate Roomを選択、部屋に参加したい場合はJoin roomを選択。

Type a messageにメッセージを入力してSendボタンを押すと、メッセージを送信できます。

30秒以上メッセージを送信しないと、自動的にチャットルームから退出させられます。

## Demo
### 入室
https://github.com/recursion-b/Online_Chat_Messenger/assets/91725975/b2790e8a-2550-4817-9e10-b82b469d199e
### チャット
https://github.com/recursion-b/Online_Chat_Messenger/assets/91725975/eec15868-f6e8-47bc-b526-7f9458496c6b
### 退室
https://github.com/recursion-b/Online_Chat_Messenger/assets/91725975/16b500cd-9d48-48e5-94f9-959dc4c8ae8e



