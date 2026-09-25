from jose import jwt
from datetime import datetime,timedelta
from ..core.config import settings

class Jwt_service:    

    def create_access_token(self,data:dict):
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = data.copy()
        to_encode.update({"exp":expire, "type":"access"})
        encode_jwt = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
        return encode_jwt
    
    def create_refresh_token(self,data:dict):
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = data.copy()
        to_encode.update({"exp":expire, "type":"refresh"})
        encode_jwt = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
        return encode_jwt 
 