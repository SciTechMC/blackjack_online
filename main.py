from fastapi import FastAPI
import socketio
from routes import http_routes, socketio_routes

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI()
fastapi_app.include_router(http_routes.router)
socketio_routes.register_handlers(sio)
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")