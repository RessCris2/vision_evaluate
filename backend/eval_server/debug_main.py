import uvicorn

if __name__ == "__main__":
    env_file_path = "/home/zwuser/app/vision/vision_eval/backend/eval_server/.env.development"
    # uvicorn.run("main:app", host="localhost", port=8019, reload=True, env_file=env_file_path)
    # env_file_path = "/home/zwuser/app/vision/vision_evaluate/backend/eval_server/.env.test"
    uvicorn.run("main:app", host="localhost", port=8990, reload=True, env_file=env_file_path)