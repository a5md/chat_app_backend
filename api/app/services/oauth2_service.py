from google.oauth2 import id_token
from google.auth.transport import requests
from beanie.operators import Or
from fastapi import Response
from ..core.config import settings
from ..core.exceptions import bad_request_exception,conflict_exception
from ..schemas.user_schema import Oauth2_register
from ..schemas.oauth2_schema import GoogleSignInRequest
from ..schemas.internal.token_schema import Token_payload
from ..models.user import User,GoogleAuth,AuthProviders
from ..services.token_service import Token_service
from ..services.email_service import Email_service

class Oauth2_service:  
    def __init__(
            self,
            token_service:Token_service,
            email_service:Email_service
    ):
        self.token_service =token_service
        self.email_service=email_service

    async def verify_google_token(
            self, 
            req:GoogleSignInRequest,
            response:Response
        ):

        try:
            google_user = id_token.verify_oauth2_token(
                req.id_token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            print(google_user)
            return await self._after_oauth2(
                web_client=req.web_client,
                response=response,
                user_data=Oauth2_register(
                    email=google_user["email"],
                    sub=google_user["sub"],
                    avatar=google_user["picture"]
                )
            )
        except Exception as e:
            print(e)
            raise bad_request_exception(
                "Invalid Google token"
            )

    async def _after_oauth2(
            self,
            web_client : bool,
            response:Response,
            user_data:Oauth2_register
    ):
        # 1 find user in DB
        user = await User.find_one(Or(
            User.email == user_data.email,
            User.auth.google.sub == user_data.sub
            ))
        if user:
            google_sub = None
            if user.auth.google:
                google_sub = user.auth.google.sub
            # 2.1 update user if found with the same sub
            if google_sub == user_data.sub:
                user.email = user_data.email
                user.avatar = user_data.avatar
                await user.save()

            # 2.2 update user if found with the same email and None sub
            elif google_sub == None:
                user.auth.google = GoogleAuth(sub=user_data.sub)
                user.avatar = user_data.avatar
                user.password_hash = None
                await user.save()

        # 3 create user if not found
        else:
            user = User(
                user_name=None,
                email=user_data.email,
                avatar=user_data.avatar,
                password_hash=None,
                auth=AuthProviders(google=GoogleAuth(sub=user_data.sub))
            )
            await user.insert()
            await self.email_service.send_account_created(
                email=user_data.email , user_name=user_data.email ,
            )

        # 4 create session
        payload = Token_payload(
            id=str(user.id),
            role=user.role,
            is_complete= user.user_name is not None
            )
        return await self.token_service.create_session(
                payload=payload ,response=response, web_client=web_client
            )
            
            
       
    
  