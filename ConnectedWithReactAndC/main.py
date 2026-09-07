from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from ConnectedWithReactAndC.FindThingsTheUserHas import router as things_router
from ConnectedWithReactAndC.ChatMessageApi import router as chat_router
from ConnectedWithReactAndC.FinishConversationApi  import router as finish_conversation_router
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings["localhost:3000"],
        settings["localhost:5173"]
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(things_router)
app.include_router(chat_router)
app.include_router(finish_conversation_router)

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Python API is running"
    }