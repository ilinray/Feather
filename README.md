# Feather <img src="http://files.suheugene.ru/b_icon.png" alt="Feather app icon" height="25" width="25">
*The best messenger ever!*

It's a messenger wrote on **Flask** and **JS** *(because send/recieve messages with flask - a big problem)*

### Pages
- Promotion -> /
- Login -> /login
- Registration -> /registration
- All chats -> /all
- Chat with __user__ -> /chat/__[user's id]__

### Tables
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

