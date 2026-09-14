"""Seed a teacher and a student user into the database.

Run from the backend/ directory:

    conda activate si-proj
    python -m scripts.seed_users

Idempotent: if a user with the same email already exists, the role and
password are updated rather than duplicated. Use --reset-password to overwrite
the hashed password even when the user already exists.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

# Make `backend/` importable when running as a script.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import select  # noqa: E402

from auth.models import User  # noqa: E402
from auth.utils import hash_password  # noqa: E402
from db import async_session  # noqa: E402


@dataclass
class SeedUser:
    name: str
    email: str
    password: str
    role: str


DEFAULT_USERS: list[SeedUser] = [
    SeedUser(name="Professor Demo", email="professor@email.com", password="password123", role="teacher"),
    SeedUser(name="Estudante Demo", email="estudante@email.com", password="password123", role="student"),
]


async def upsert_user(seed: SeedUser, *, reset_password: bool) -> str:
    async with async_session() as session:
        existing = await session.execute(select(User).where(User.email == seed.email))
        user = existing.scalar_one_or_none()

        if user is None:
            user = User(
                name=seed.name,
                email=seed.email,
                hashed_password=hash_password(seed.password),
                role=seed.role,
            )
            session.add(user)
            await session.commit()
            return f"created {seed.role:7s} {seed.email}"

        changes: list[str] = []
        if user.role != seed.role:
            user.role = seed.role
            changes.append(f"role->{seed.role}")
        if user.name != seed.name:
            user.name = seed.name
            changes.append("name")
        if reset_password:
            user.hashed_password = hash_password(seed.password)
            changes.append("password")

        if not changes:
            return f"skipped {seed.role:7s} {seed.email} (unchanged)"

        await session.commit()
        return f"updated {seed.role:7s} {seed.email} ({', '.join(changes)})"


async def main(args: argparse.Namespace) -> None:
    for seed in DEFAULT_USERS:
        result = await upsert_user(seed, reset_password=args.reset_password)
        print(result)


def cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset-password",
        action="store_true",
        help="Overwrite the password of existing seeded users.",
    )
    args = parser.parse_args()
    asyncio.run(main(args))


if __name__ == "__main__":
    cli()
