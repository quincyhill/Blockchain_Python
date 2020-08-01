from typing import List, Callable
import functools
import os
import sqlite3
import keyboard
from colorama import init, Fore, Style
db_name = "db.sqlite3"


class User:
    def __init__(self, username: str):
        self.username = username


class Todo:
    def __init__(self, user: User, title: str, description: str):
        self.user = user
        self.title = title
        self.description = description
        self.is_done = False


user_list: List[User] = []
current_user: User
todo_list: List[Todo] = []
current_todo: Todo


def introduction() -> None:
    """This is the greeting / introduction
    """
    username: str = input(
        "Welcome to " + Fore.RED + "Quincy's Todo command line program! " + Fore.WHITE + "to get started first enter your name: ")
    if len(user_list) == 0:
        create_user(username)
        print(f"No users were found created a new user: {username}")
    else:
        for user in user_list:
            if username != user.username:
                create_user(username)
                print(f"Created new user \nHello {username}")
                # NOTE: this break is problematic
                break
            else:
                current_user = user
                print(f"Hello {username}")
                # NOTE: this break is problematic
                break


def make_connection(func: Callable) -> Callable:
    """Sqlite3 decorator for accessing the database

    Args:
        func (Callable): [description]

    Returns:
        Callable: [description]
    """
    @functools.wraps(func)
    def wrapper_make_connection(*args, **kwargs) -> Callable:
        action: Callable
        try:
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            kwargs['c'] = c
            action = func(*args, **kwargs)
            conn.commit()
        except sqlite3.DatabaseError as e:
            print(e)
        except sqlite3.DataError as e:
            print(e)
        except sqlite3.OperationalError as e:
            print(e)
        finally:
            conn.close()
        return action
    return wrapper_make_connection


@make_connection
def select_existing_user(user: User) -> None:
    # read users from database
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    # match selected user to the one in the database
    # set the current user to the selected user
    pass


@make_connection
def select_new_user() -> None:
    # create a new user
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    for row in c.execute('SELECT * FROM users'):
        print(row)
    # write use to the database
    # set the current user to the selected user
    pass


def body() -> None:
    """This is the main loop
    """
    title: str = input("Please name the todo: ")
    description: str = input("Give a short description about it: ")
    create_todo(title, description)


@make_connection
def create_user(username: str, *args, **kwargs) -> None:
    new_user = User(username)
    global current_user
    current_user = new_user
    user_list.append(new_user)
    print(f"Username is {username}")

    # Add user to database
    c: sqlite3.Cursor
    c = kwargs['c']
    c.execute(f"INSERT INTO users VALUES (?)", [current_user.username])


@make_connection
def create_todo(title: str, description: str, *args, **kwargs) -> None:
    global current_user
    new_todo = Todo(current_user, title, description)
    global current_todo
    current_todo = new_todo
    current_todo.user = current_user

    values = [current_user.username, title, description, False]

    # Add todo to database
    c: sqlite3.Cursor
    c = kwargs['c']
    c.execute("INSERT INTO todos VALUES (?,?,?,?)", values)


@make_connection
def init_users_and_todos(*args, **kwargs) -> None:
    c: sqlite3.Cursor
    c = kwargs['c']
    # Create the table for users
    c.execute("CREATE TABLE users (username text)")
    # Create the table for todos
    c.execute(
        "CREATE TABLE todos (user text, title text, description text, is_done integer)")


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
        body()
        if number == 2:
            for user in user_list:
                print("Username: ", user.username)
            has_quit = True

run()
