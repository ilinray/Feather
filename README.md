# Feather <img src="http://files.suheugene.ru/b_icon.png" alt="Feather app icon" height="25" width="25">
*The best messenger ever!*

It's a messenger wrote on **Flask** and **JS** *(because send/recieve messages with flask is a big problem)*

## Pages
- Promotion -> `/`
- Login -> `/login`
- Registration -> `/registration`
- All chats -> `/all`
- Chat with user -> `/chat/[chat_id]`

## Tables
- users
  - id
  - login
  - email
  - hashed_password
  - created_date
- dialogs
  - id
  - name
  - file
  - created_date
  - many_people
  - hashed_password

## REST API

### Auth
**[GET] `/api/auth`**

Authorization. Returns user's id.

**[POST] `/api/auth`**

Registration. Adds user to DB.

### User
**[GET] `/api/user/[id]`**

Returns *User* object

**[PATCH] `/api/user/[id]`**

Modification one of *User*'s fields


### Chat
**[GET] `/api/chat/[id]`**

Returns -------------

**[POST] `/api/chat/[id]`**

Sends message to chat
