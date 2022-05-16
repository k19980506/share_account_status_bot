# share_account_status_bot

## 目的

為了節省金錢，讓多人可以共用帳號，且為了避免部分平台設有同時登入裝置上線。
因此開發此機器人，讓親友間可以透過此 line bot 進行帳號狀態設定/查詢。

## 功能

### 初次使用時，必須先新增帳號:

1. 若您為帳號持有人，請使用 `add` 新增帳號，若您非帳號持有人請使用 `use` 使用現有帳號。
2. 第二個參數為平台服務名稱，例如: netflix, kkbox, youtube, disney...
3. 第三個參數為此平台帳號名稱，不一定要輸入帳號，只要共用的親友間輸入相同的名稱或帳號，才能綁定在一起，進行狀態查詢。
4. 範例：

```
add kkbox handsomeking506
use kkbox handsomeking506
```

### 帳號創建完畢以後，即可以用 `go/stop/search` 進行狀態管理/查詢：

- go: 將帳號狀態更改為上線，**若同一平台底下設有多組帳號，請指定帳號**

```
go kkbox
go kkbox account1
```

- stop: 將帳號狀態更改為上線，**若同一平台底下設有多組帳號，請指定帳號**

```
stop netflix
stop netflix account1
```

- search: 查詢使用相同帳號的使用者狀態，僅顯示上線中的使用者。可以指定平台

```
search kkbox
search
```
