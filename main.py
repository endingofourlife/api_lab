from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

from database import Database
from starlette import status

from database.repository.leaderboard_repo import LeaderboardRepository
from database.repository.task_repo import TaskRepository
from database.repository.user_repo import UserRepository
from database.repository.game_repo import GameRepository
from database.tables import User, Task, Game
from pydantic import BaseModel
from typing import List, Optional

from aiogram import Bot
from aiogram.types import LabeledPrice

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allow all origins. Change this to specific origins if needed.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods.
    allow_headers=["*"],  # Allow all headers.
)

# Initialize the database
database = Database()


# Dependency to get a database session
async def get_db() -> AsyncSession:
    async with database.get_session() as session:
        yield session


# Request Models


class UserRequest(BaseModel):
    user_name: str
    telegram_id: int
    referrer_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserBalanceRequest(BaseModel):
    telegram_id: int
    reward: int

    class Config:
        from_attributes = True


class TaskRequest(BaseModel):
    name: str
    expired_at: datetime
    reward: float
    repeat_count: int = 1

    class Config:
        from_attributes = True


class GameRequest(BaseModel):
    user_id: int
    bet: float
    symbol: str

    class Config:
        from_attributes = True


class GameFinishRequest(BaseModel):
    game_id: int
    enemy_id: int
    enemy_symbol: str

    class Config:
        from_attributes = True


class TaskFinishRequest(BaseModel):
    user_id: int
    task_id: int

    class Config:
        from_attributes = True


# User Endpoints
@app.get('/users/', response_model=None)
async def get_users(db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    users = await user_repo.get_all_users()
    return users


@app.get('/user/{user_id}', response_model=None)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_id)
    user.balance = round(user.balance, 2)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@app.delete('/user/game/{game_id}', response_model=None)
async def delete_game(game_id: int, db: AsyncSession = Depends(get_db)):
    game_repo = GameRepository(db)
    game = await game_repo.delete_game_by_id(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail='Game not found')
    return game


class UserResponse(BaseModel):
    id: int
    name: str
    balance: float
    referrer_id: Optional[int]

    class Config:
        from_attributes = True


@app.get('/user/{user_id}/games', response_model=None)
async def get_user_games(user_id: int, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    games = await user_repo.get_user_games(user_id)
    if not games:
        raise HTTPException(status_code=404,
                            detail='No games found for the user')
    return [{
        "id": game.id,
        "bet": round(game.bet, 2),
        "symbol": game.symbol,
        "result": game.result,
        "user_id": game.user_id,
        "created_at": game.created_at,
    } for game in games]
    # return games


@app.get('/user/{user_id}/friends', response_model=None)
async def get_user_friends(user_id: int, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    friends = await user_repo.get_user_friends(user_id)
    print(friends)
    return friends


@app.get('/user/{user_id}/tasks', response_model=None)
async def get_user_tasks(user_id: int, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    tasks = await user_repo.get_user_tasks(user_id)
    return tasks


@app.get('/user/{user_id}/top_place')
async def get_user_top_place(user_id: int, db: AsyncSession = Depends(get_db)):
    leaderboard_repo = LeaderboardRepository(db)
    place = await leaderboard_repo.get_user_place(user_id)
    if place is None:
        raise HTTPException(status_code=404, detail='User not found')
    return place


@app.post('/user/register',
          response_model=None,
          status_code=status.HTTP_201_CREATED)
async def post_register_user(user_data: UserRequest,
                             db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    new_user = await user_repo.create_user(user_data.user_name,
                                           user_data.telegram_id,
                                           user_data.referrer_id)
    return new_user


@app.post('/user/finish_task', status_code=status.HTTP_204_NO_CONTENT)
async def post_finish_task(request: TaskFinishRequest,
                           db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    await user_repo.finish_task(request.user_id, request.task_id)


@app.put('/user/balance', status_code=status.HTTP_204_NO_CONTENT)
async def put_user_balance(data: UserBalanceRequest,
                           db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    await user_repo.update_user_balance(data.telegram_id, data.reward)


# Task Endpoints
@app.get('/tasks/', response_model=None)
async def get_tasks(db: AsyncSession = Depends(get_db)):
    task_repo = TaskRepository(db)
    tasks = await task_repo.get_all_tasks()
    return tasks


@app.post('/tasks/', response_model=None, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskRequest,
                      db: AsyncSession = Depends(get_db)):
    task_repo = TaskRepository(db)
    new_task = await task_repo.create_task(task_data.name,
                                           task_data.expired_at,
                                           task_data.reward,
                                           task_data.repeat_count)
    return new_task


@app.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task_repo = TaskRepository(db)
    await task_repo.delete_task(task_id)


# Game Endpoints
@app.get('/game/', response_model=None)
async def get_games(db: AsyncSession = Depends(get_db)):
    game_repo = GameRepository(db)
    games = await game_repo.get_all_games()
    return games


@app.post('/game/create',
          response_model=None,
          status_code=status.HTTP_201_CREATED)
async def create_game(game_data: GameRequest,
                      db: AsyncSession = Depends(get_db)):
    game_repo = GameRepository(db)
    round_bet = round(game_data.bet, 2)
    print(round_bet)
    new_game = await game_repo.create_game(game_data.user_id, round_bet,
                                           game_data.symbol)
    if new_game is None:
        raise HTTPException(status_code=400, detail='Not enough balance')
    return new_game


@app.put('/game/finish/{game_id}',
         status_code=status.HTTP_200_OK,
         response_model=Optional[dict])
async def finish_game(game_data: GameFinishRequest,
                      db: AsyncSession = Depends(get_db)):
    game_repo = GameRepository(db)
    result = await game_repo.finish_game(game_data.game_id, game_data.enemy_id,
                                         game_data.enemy_symbol)
    if result is None:
        raise HTTPException(status_code=404, detail='Game not found')
    elif result == 'Game already finished':
        raise HTTPException(status_code=400, detail='Game already finished')
    return {"result": result}


# Leaderboard Endpoint
@app.get('/leaderboard/top_10', response_model=None)
async def get_top_10_leaderboard(db: AsyncSession = Depends(get_db)):
    leaderboard_repo = LeaderboardRepository(db)
    top_10 = await leaderboard_repo.get_leaderboard_top_10()
    return top_10


class PaymentRequest(BaseModel):
    price: int

    class Config:
        from_attributes = True


@app.post('/payment', response_model=None)
async def payment(request: PaymentRequest, db: AsyncSession = Depends(get_db)):
    bot = Bot(token="7890394661:AAGWGeUWx8xM7GaHRixezTEabM217Aq7a_0")
    payment_link = await bot.create_invoice_link(
        title='Пополнение баланса',
        description='Пополнение игрового баланса',
        payload='game_payload',
        provider_token='',
        currency='XTR',
        prices=[LabeledPrice(label='XTR', amount=request.price)],
    )
    return {"paymentLink": payment_link}
