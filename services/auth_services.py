async def login_user(username: str, password: str):
    # Validate user from DB
    # Return user info, token, or error
    return {"message": f"Logged in as {username}"}
