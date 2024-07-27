from database import init_db  # Adjust import as necessary
from routes import router as api_router
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Initialize the database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()

# Include the API router
app.include_router(api_router)

# Add CORS middleware to allow all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Custom validation exception handler (commented out for now)
# async def validation_exception_handler(request: Request, exc: ValidationError):
#     details = exc.errors()
#     modified_details = []
#     for error in details:
#         modified_details.append({
#             "loc": error["loc"],
#             "message": error["msg"],
#             "type": error["type"],
#         })
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content=jsonable_encoder({"detail": modified_details}),
#     )

# app.add_exception_handler(ValidationError, validation_exception_handler)

# Middleware to check the request path for invalid characters
@app.middleware("http")
async def check_path(request: Request, call_next):
    # Check if the request path contains invalid characters
    path = request.url.path
    if any(char in path for char in "`@$#%^*=<>[]|\\~"):
        return JSONResponse({"error": "format error"}, status_code=400)

    # If the path is valid, continue to the actual request handler
    response = await call_next(request)
    return response
