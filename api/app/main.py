from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .core.lifespan import lifespan
from .api.router import router
from .core.config import settings
from .middleware.cors import setup_cors
from .middleware.excption_handling import global_exception_handler

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    )

app.include_router(router)

setup_cors(app=app)

# Exception handlers
app.add_exception_handler(
    Exception,
    global_exception_handler
)
 

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Google Login Test</title>
    <script src="https://accounts.google.com/gsi/client" async></script>
</head>

<body>

<h2>Google Login Test</h2>

<div id="googleButton"></div>

<script>

function handleCredentialResponse(response) {

    console.log("Google ID Token:");
    console.log(response.credential);


    fetch("http://localhost:8000/api/v1/oauth2/google/signin", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id_token: response.credential,
            web_client: true
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
    });
}


window.onload = function () {

    google.accounts.id.initialize({
        client_id: "166836859214-beg15cijcoueun48fdi5rklb93d53eup.apps.googleusercontent.com",
        callback: handleCredentialResponse
    });


    google.accounts.id.renderButton(
        document.getElementById("googleButton"),
        {
            theme: "outline",
            size: "large"
        }
    );

};

</script>

</body>
</html>
"""
@app.get("/", response_class=HTMLResponse)
async def home():
    return html