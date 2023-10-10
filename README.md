# Online Chat Messenger

## 成果物と起動方法

### 成果物

[react-electron-app-darwin-x64-0.1.0.zip](https://drive.google.com/file/d/1wir_OvYZX8QBIex5TKCJWEu6cKehPHtd/view?usp=sharing)

### 起動方法

https://support.apple.com/ja-jp/guide/mac-help/mh40616/mac

## 概要

Express と Socket.io を使用したリアルタイム・双方向非同期通信を行うオンラインチャットアプリです。  
クライアントには Electron を使用し、デスクトップアプリケーションとして作成しました。

クライアントは自分のチャットルームを作成することができ、他のクライアントは作成されたチャットルームに参加して、メッセージのやりとりをすることができます。  
チャットルームにはパスワードをかけることができ、入室時には正確なパスワードを入力しないと参加できません。

ホストが部屋を退室すると他のクライアントも自動的に退室させられ、トップページに戻ります。

## 作成の経緯

[Python でチャットアプリ](stage2)を作成したことで、TCP/UDP やプロトコルの概念を理解し、独自の低レベルネットワーキングアプリケーションを作成できるようになりました。

それを踏まえ、Express や Socket.IO のようなライブラリを使用したクライアントサーバ分散型アプリケーションを作成することで、さらなるサーバサイドアプリケーション開発のスキル向上を目指しました。

## 使用技術

- Client

  - React + JavaScript
  - React Bootstrap
  - Socket.io-client
  - Electron

- Server

  - Express + JavaScript
  - Socket.io

- Hosting

  - Render

## 期間

2023 年 9 月 23 日から 2 週間。3 名で開発しました。

## こだわった点

### オブジェクト指向の設計

クライアントの情報をオブジェクト化したことで情報を扱いやすくしました。

チャットルームクラスを作成して、チャットルーム別にパスワードや参加中のクライアント情報を持たせることで、単一責任の原則に従うような設計にしました。

### 30 分ごとの自動退出処理

30 分ごとにクライアントの最終更新時間を追跡し、一定時間更新がない場合、クライアントは自動的に退出させられるようになっています。その際、退室情報は他のクライアントにも送信されます。

また、ホストが退室した場合、チャットルームは閉じられ、他のクライアントには 10 秒後にトップページに戻るアナウンスが表示されます。

### セキュリティ

チャットルームにはパスワードをかけることができ、正しいパスワードを入力しないと入室できないようになっています。  
その際、パスワードはサーバでハッシュ化されて、安全に格納されます。

## これからの改善点、拡張案

送受信されるメッセージを暗号化する予定でしたが、ライブラリを上手く読み込めず実装できなかったため、今後、原因を特定して実装したいです。

## 使用方法

1. ユーザー名、部屋の名前、部屋のパスワードを入力します。

2. Icon Image に画像をドラッグアンドドロップすると、自分のアイコン画像を設定できます。

3. （部屋を作成したい場合）Create Room を選択します。  
   （部屋に参加したい場合）Join room を選択します。

4. Type a message にメッセージを入力して Send ボタンを押すと、メッセージを送信できます。

5. 30 分以上メッセージを送信しないと、自動的にチャットルームから退出します。

## Demo

### 入室

https://github.com/recursion-b/Online_Chat_Messenger/assets/91725975/b2790e8a-2550-4817-9e10-b82b469d199e

### チャット

https://github.com/recursion-b/Online_Chat_Messenger/assets/91725975/eec15868-f6e8-47bc-b526-7f9458496c6b

### 退室

https://github.com/recursion-b/Online_Chat_Messenger/assets/91725975/16b500cd-9d48-48e5-94f9-959dc4c8ae8e
