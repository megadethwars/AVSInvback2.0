from src.fastapi_app import create_app


app = create_app("local")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)