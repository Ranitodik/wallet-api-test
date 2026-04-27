from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, select, insert
from app.models import Base, Wallet
import os
import asyncio
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/wallets")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Ждём готовности БД и создаём таблицы
@asynccontextmanager
async def lifespan(app: FastAPI):
    while True:
        try:
            async with engine.connect() as conn:
                await conn.execute(select(1))
            break
        except Exception:
            await asyncio.sleep(2)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/api/v1/wallets/{wallet_id}/operation")
async def operate_wallet(wallet_id: str, op: dict, db: AsyncSession = Depends(get_db)):
    operation_type = op.get("operation_type")
    amount = op.get("amount")

    if not isinstance(amount, (int, float)) or amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    if operation_type not in ("DEPOSIT", "WITHDRAW"):
        raise HTTPException(400, "Operation must be DEPOSIT or WITHDRAW")

    # Получаем или создаём кошелёк
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    if wallet is None:
        wallet = Wallet(id=wallet_id, balance=0.00)
        db.add(wallet)
        await db.commit()  #  фиксируем создание
        await db.refresh(wallet)  #  обновляем объект

    # Считаем новый баланс
    delta = amount if operation_type == "DEPOSIT" else -amount
    new_balance = float(wallet.balance) + delta

    if new_balance < 0:
        raise HTTPException(400, "Insufficient funds")

    # Обновляем баланс
    wallet.balance = new_balance
    await db.commit()

    return {"balance": new_balance}

@app.get("/api/v1/wallets/{wallet_id}")
async def get_balance(wallet_id: str, db: AsyncSession = Depends(get_db)):
    wallet = await db.get(Wallet, wallet_id)
    if not wallet:
        raise HTTPException(404, "Wallet not found")
    return {"balance": float(wallet.balance)}