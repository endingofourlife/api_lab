from typing import Optional, List, Dict, Any
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.tables import Game, User


def _get_winner(user_symbol: str, enemy_symbol: str) -> Optional[str]:
    """Return 'user' if user wins, 'enemy' if enemy wins, or 'draw' if it's a tie."""
    if user_symbol == enemy_symbol:
        return "draw"
    if (user_symbol == "rock" and enemy_symbol == "scissors") or \
       (user_symbol == "scissors" and enemy_symbol == "paper") or \
       (user_symbol == "paper" and enemy_symbol == "rock"):
        return "user"  # user wins
    return "enemy"  # enemy wins


class GameRepository:

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def get_all_games(self) -> list[dict[str, Any]]:
        query = select(Game, User.name).join(
            User, Game.user_id == User.id).where(Game.result == None)
        result = await self._session.execute(query)

        # Each item in `games` is a tuple (Game instance, user_name)
        games = result.all()

        # Format the results to include user_name with each game
        return [{
            "id": game.id,
            "bet": round(game.bet, 2),
            "symbol": game.symbol,
            "result": game.result,
            "user_id": game.user_id,
            "user_name": user_name
        } for game, user_name in games]

    async def create_game(self, user_id: int, bet: float,
                          symbol: str) -> Game | None:
        correct_bet = round(bet, 2)
        new_game = Game(user_id=user_id, bet=correct_bet, symbol=symbol)
        # check if user has enough balance
        user = await self._session.get(User, user_id)
        if user.balance < bet:
            print('Not enough balance')
            return None
        user.balance -= bet
        self._session.add(new_game)
        await self._session.commit()
        await self._session.refresh(new_game)
        return new_game

    async def delete_game_by_id(self, game_id: int):
        game = await self._session.get(Game, game_id)
        if game is not None:
            query = delete(Game).where(Game.id == game_id)
            await self._session.execute(query)
            await self._session.commit()
        return game

    async def finish_game(self, game_id: int, enemy_id: int,
                          enemy_symbol: str) -> str:
        game = await self._session.get(Game, game_id)
        if game is None:
            return "Game not found"
        if game.result:
            return "Game already finished"

        user_symbol = game.symbol
        winner = _get_winner(user_symbol, enemy_symbol)
        enemy = await self._session.get(User, enemy_id)
        user = await self._session.get(User, game.user_id)

        # Set game result based on winner
        if winner == "draw":
            game.result = "draw"
            user.balance += game.bet

        elif winner == "user":
            game.result = "win"
            if user:
                user.balance += 2 * game.bet
                enemy.balance -= game.bet
                user.won_games += 1
            else:
                print("User not found for the game")

        elif winner == "enemy":
            game.result = "lose"
            if enemy:
                enemy.balance += game.bet
                enemy.won_games += 1
            else:
                print("Enemy user not found")

        await self._session.commit()

        return game.result
