from database import init_db  # Adjust import as necessary
from routes import router as api_router
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, constr

app = FastAPI()
# FIXME:on_event deprecated
@app.on_event("startup")
async def startup_event():
    await init_db()
app.include_router(api_router)


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

@app.middleware("http")
async def check_path(request: Request, call_next):
    # Check the request path is not a invalid string  
    path = request.url.path
    if any(char in path for char in "`@$#%^*=<>[]|\\~"):
        return JSONResponse({"error": "format error"}, status_code=400)

    # If the path is valid, continue to the actual request handler
    response = await call_next(request)
    return response
 