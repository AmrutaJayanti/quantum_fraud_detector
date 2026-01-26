import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import transaction_routes,graph_routes,predict_routes
from routes.ws_routes import router as ws_router


app = FastAPI(title="Quantum Fraud Detection API")

app.include_router(transaction_routes.router)
app.include_router(graph_routes.router)
app.include_router(predict_routes.router)
app.include_router(ws_router)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,
    allow_methods=["*"],        
    allow_headers=["*"],        
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
