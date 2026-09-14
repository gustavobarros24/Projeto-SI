import uuid
import functools
from typing import Final, TypeVar

from pydantic import BaseModel

MAX_IRRELEVANT_MSGS: Final[int] = 3 
MAX_HISTORY_MSGS: Final[int] = 10

ModelT = TypeVar("ModelT", bound=BaseModel)

def node(model):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Find the state arg: first arg that is a dict or model instance.
            # Preceding args (e.g. self) go in prefix, following args (e.g. config, store) in suffix.
            prefix = []
            state_input = None
            suffix = ()
            for i, arg in enumerate(args):
                if isinstance(arg, (model, dict)):
                    state_input = arg
                    suffix = args[i + 1:]
                    break
                prefix.append(arg)

            if isinstance(state_input, model):
                state = state_input
            else:
                state = model(**state_input)

            new_state = func(*prefix, state, *suffix, **kwargs)
            return new_state.model_dump()

        return wrapper

    return decorator

def generate_uuid():
    return str(uuid.uuid4())
