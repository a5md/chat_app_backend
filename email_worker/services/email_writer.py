from jinja2 import Environment, FileSystemLoader

class Email_writer:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader("email_worker/services/email_templates"))

        self.handlers = {
            "registration_otp": self.registration_otp,
            "forgot_password_otp": self.reset_password_otp,
            "account_created": self.welcome,
        }

    def render(self, template_name: str, subject: str, **context):
        template = self.env.get_template(template_name)
        html = template.render(**context)
        return html, subject

    def registration_otp(self, otp: str, expire_minutes: int):
        return self.render(
            template_name="registration_otp.html",
            subject="Verify Your Email",
            otp=otp,
            expire_minutes=expire_minutes,
        )

    def reset_password_otp(self,user_name:str, otp: str, expire_minutes: int):
        return self.render(
            template_name="forgot_password_otp.html",
            subject="Reset Your Password",
            otp=otp,
            name=user_name,
            expire_minutes=expire_minutes,
        )

    def welcome(self, name: str):
        return self.render(
            template_name="account_created.html",
            subject="Welcome!",
            name=name,
        )

    def write(self, job: dict):
        email_type = job["type"]

        handler = self.handlers.get(email_type)
        if handler is None:
            raise ValueError(f"Unknown email type: {email_type}")

        if email_type == "registration_otp":
            return handler(
                otp=job["otp"],
                expire_minutes=job["ex"],
            )

        if email_type == "forgot_password_otp":
            return handler(
                otp=job["otp"],
                expire_minutes=job["ex"],
                user_name=job["user_name"]
            )

        if email_type == "account_created":
            return handler(
                name=job["user_name"],
            )
