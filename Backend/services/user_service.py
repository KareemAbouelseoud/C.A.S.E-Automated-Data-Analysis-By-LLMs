from config import *

def get_repo():
    repo = UserRepository()
    return repo

class UserService:
    def __init__(self):
        self.user_repository = get_repo()
    
    async def check_login(self,username:str,password: str):
        user = await self.user_repository.get_by_username(username)
        if user ==None:
            return False
        else:
            return bcrypt.checkpw(password.encode(), user.password.encode())
    
    async def get_user_id(self,username: str):
        user = await self.user_repository.get_by_username(username)
        return str(user.id)
    
    async def get_user(self, id: str) -> Optional[User]:
        return await self.user_repository.get_by_id(id)

    async def get_users(self) -> List[User]:
        return await self.user_repository.get_all()

    async def create_user(self, x: SignUpRequest) -> User:
        
        user_data = x.model_dump()
        matchingEmails=await self.user_repository.Filter({"email":user_data["email"]})
        matchingUsernames=await self.user_repository.Filter({"username":user_data["username"]})
        print(type(matchingEmails))
        if len(matchingEmails)!=0:
            return "Email already exists."
        elif len(matchingUsernames)!=0:
            return "Username already exists."
        user_data["password"]=bcrypt.hashpw(user_data["password"].encode(), bcrypt.gensalt()).decode()
        new_user =User(**user_data, Project=[])
        return await self.user_repository.create(new_user)

    async def update_user(self, id: str, user: User) -> bool:
        return await self.user_repository.update(id, user)

    async def delete_user(self, id: str) -> bool:
        return await self.user_repository.delete(id)
    