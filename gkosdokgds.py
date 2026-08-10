users = {"alice", "bob", "carol", "dave"}

user_roles = {
    ("alice", "admin"),
    ("bob", "manager"),
    ("carol", "employee"),
    ("dave", "guest"),
}

role_permissions = {
    ("admin", "read"),
    ("admin", "write"),
    ("admin", "delete"),
    ("admin", "approve"),
    ("manager", "read"),
    ("manager", "write"),
    ("manager", "approve"),
    ("employee", "read"),
    ("employee", "write"),
    ("guest", "read"),
}


def get_permissions(user):
    role = ""
    for u in user_roles:
        if u[0] == user:
            role = u[1]
