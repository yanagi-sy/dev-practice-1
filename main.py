from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# FastAPI アプリ本体を作成
# この app を uvicorn から参照してサーバーを起動する（例: uvicorn main:app --reload）
app = FastAPI()


# ユーザー情報の「型（モデル）」を定義
# - id: ユーザーを区別するための番号（整数）
# - name: ユーザーの名前（文字列）
# - age: ユーザーの年齢（整数）
# BaseModel を継承すると、この形に沿ったデータのチェック（バリデーション）を自動でしてくれる
class User(BaseModel):
    id: int
    name: str
    age: int


# 実際のユーザーデータを入れておく「入れ物」
# 本来はデータベースを使うが、ここでは学習用に Python のリストを使っている
users: List[User] = []


# ルートパス（http://127.0.0.1:8000/）にアクセスされたときの処理
@app.get("/")
def read_root():
    # ブラウザでアクセスすると、この JSON がそのまま表示される
    return {"message": "Hello, World!"}


# 新しいユーザーを登録するエンドポイント
# - メソッド: POST
# - パス: /users/
# - body で User 型の JSON を受け取り、そのままリストに追加して返す
@app.post("/users/", response_model=User)
def create_user(user: User):
    users.append(user)
    return user


# すべてのユーザーを取得するエンドポイント
# - メソッド: GET
# - パス: /users/
# - users リストの中身をそのまま返す
@app.get("/users/", response_model=List[User])
def read_users():
    return users


# 特定の ID のユーザー 1人分の情報を取得するエンドポイント
# - メソッド: GET
# - パス: /users/{user_id}
# - URL の {user_id} の部分に入った数字を使って検索する
@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    # リストの中を先頭から順番に調べる
    for user in users:
        # id が一致したユーザーが見つかったら、そのユーザーを返す
        if user.id == user_id:
            return user
    # 見つからなかったときはエラー内容の JSON を返す
    # ※ response_model=User を付けているため、本番コードでは別のエラーハンドリングをするのが望ましい
    return {"error": "User not found"}  # type: ignore[return-value]


# 特定の ID のユーザー情報を更新するエンドポイント
# - メソッド: PUT
# - パス: /users/{user_id}
# - URL の id で指定されたユーザーの name と age を、新しく送られてきた情報で上書きする
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    for user in users:
        if user.id == user_id:
            # 見つかったユーザーの name と age を更新
            user.name = updated_user.name
            user.age = updated_user.age
            return user
    # 見つからなかった場合
    return {"error": "User not found"}  # type: ignore[return-value]


# 特定の ID のユーザーを削除するエンドポイント
# - メソッド: DELETE
# - パス: /users/{user_id}
# - 指定した ID と一致するユーザーを、users リストから取り除く
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    global users
    # リスト内包表記を使って、
    #   user.id != user_id（指定した id ではないユーザー）
    # だけを残した新しいリストを作り、それを users に代入している
    # その結果、指定した id のユーザーはすべて削除される
    users = [user for user in users if user.id != user_id]
    return {"message": "User deleted"}