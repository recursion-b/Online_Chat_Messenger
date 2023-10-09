# Online Chat Messenger

## 概要

クライアントサーバモデルのアーキテクチャを採用したオンラインチャットアプリです。  
CLI 版と Tkinter で作成したデスクトップアプリ版を作成しました。

クライアントは、自分のチャットルームを作成することができ、他のクライアントは作成されたチャットルームに参加して、メッセージのやりとりをすることができます。  
また、チャットルームにはパスワードをかけることができ、入室時には正確なパスワードを入力しないと参加できません。

チャットルームの作成・参加時には、TCP 接続が用いられます。サーバは一意のトークンを生成してクライアントへ送信し、TCP 接続を終了します。その後、クライアントは UDP を使用して、チャットルームへ自動的に接続され、他のユーザーとのメッセージのやりとりができるようになります。

クライアントとサーバ間で送受信されるメッセージは、公開鍵暗号方式（RSA）で暗号化され、保護されています。

## 学習目標

- サーバ操作・ネットワークの基礎を身につけ、サーバサイドのアプリケーション開発のスキルアップを目指す。
- TCP/UDP やプロトコルの概念を理解して、独自の低レベルネットワーキングアプリケーションを作成できるようになる。

上記の目標を達成するため、Python の低水準ネットワークインターフェースである socket モジュールを使用して、独自のプロトコルを作成し、クライアントとサーバ間で通信を行うチャットアプリを開発しました。

## 使用技術

Python, tkinter, socket（ソケット通信）, PyCryptodome（メッセージ暗号化）

## 期間

9 月 23 日から 2 週間。3 名で開発。

## 使用方法
### 手順
1. stage2 ディレクトリで、サーバとクライアントを起動します。

- Server の起動

```
python server.py
```

- Client の起動

```
python client.py
```

2. CIL版とデスクトップ版のどちらを使用するか選択します。

![select_cli_or_tkinter](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/7e691158-87d6-4ce2-9331-09bffe55ab3b)

2. ユーザー名を入力します。

![input_username](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/78dc6839-cd94-4b3c-aa2c-8ae21074a6c4)

3. 新たに部屋を作成するか、既存の部屋に参加するかを選択することができます。  
   作成は 1、参加は 2 を入力します。

![enter_operation_code](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/bb19d1dc-df89-43f0-827a-2abe01d8380a)

4. （作成の場合）新たに部屋名と設定するパスワードを入力します。  
   （参加の場合）参加する部屋名と設定されたパスワードを入力します。

![enter_password](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/16560688-0ba2-4388-9e1f-f710648a569a)

5. 部屋の作成・参加が完了すると、メッセージを送信することができるようになります。

![entry_room](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/5175824c-06e8-44bb-91a4-8a61f27d280c)

### CLI

- クライアント

![chat](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/cab01da5-8f48-46cb-b9ac-55cb37964ae7)

- サーバ

![server](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/fcceab3c-f645-46ed-919d-d3854b592a5b)

### デスクトップ

- ユーザ情報入力画面

![tkinter_user_info](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/9649d97a-2934-4319-93e4-c4f8daf25a04)

- チャットルーム

![tkinter_chat_room](https://github.com/recursion-b/Online_Chat_Messenger/assets/96802323/f306277d-e351-430c-abd9-11713b4eb4cd)