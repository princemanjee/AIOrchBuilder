from fastapi import FastAPI
from routers.main import router

app = FastAPI(title='p_r_prince_rehman_manjee,_ee,_mis_portfolio API')

app.include_router(router)

@app.get('/')
async def root():
    return {'message': 'Welcome to p_r_prince_rehman_manjee,_ee,_mis_portfolio API'}
