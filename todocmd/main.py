from typing import List
import os
import sqlite3
import keyboard
from colorama import init, Fore, Style
db_name = "db.sqlite3"


class User:
    def __init__(self, username: str):
        self.username = username
        self.todos: List[Todo] = []


class Todo:
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
        self.is_done = False


user_list: List[User] = []
current_user: User


def introduction() -> None:
    username: str = input(
        "Welcome to " + Fore.RED + " Quincy's Todo command line program!" + Fore.WHITE + " to get started first enter your name: ")
    if len(user_list) == 0:
        create_user(username)
        print(f"No users found created a new user: {username}")
    else:
        for user in user_list:
            if username != user.username:
                create_user(username)
                print(f"Created new user \nHello {username}")
                break
            else:
                current_user = user
                print(f"Hello there: {username}")
                break


def create_user(username: str) -> None:
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Create a new user
    c.execute(f"INSERT INTO users VALUES ('{username}')")

    conn.commit()
    conn.close()

    new_user = User(username)
    current_user = new_user
    user_list.append(new_user)


def create_todo(title: str, description: str) -> None:
    new_task = Todo(title, description)


def init_users_and_todos() -> None:
    try:
        conn = sqlite3.connect(db_name)
    except sqlite3.Error as e:
        print(e)
    c = conn.cursor()
    # Create the table for users
    c.execute('''CREATE TABLE users (username text)
    ''')
    # Create the table for todos
    c.execute('''CREATE TABLE todos (name text, description text)
    ''')
    conn.commit()
    conn.close()


def init_database() -> None:
    if not os.path.exists(db_name):
        with open(db_name, 'w') as f:
            init_users_and_todos()
    else:
        pass


def run() -> None:
    """Runs the program
    """
    init_database()
    has_quit = False
    number = 0
    while not has_quit:
        number += 1
        introduction()
        if number == 4:
            for user in user_list:
                print(user.username)
            has_quit = True


run()
