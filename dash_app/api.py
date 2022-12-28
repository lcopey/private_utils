from typing import Dict

import pandas as pd
from fastapi import FastAPI

app = FastAPI()


def remove_nan(items: dict):
    result = {}
    for key, value in items.items():
        if isinstance(value, dict):
            value = remove_nan(value)

        if not pd.isna(value):
            result[key] = value

    return result


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/compute')
async def compute(data: Dict):
    data = pd.DataFrame(data)
    response = data / data.sum(axis=0)
    return remove_nan(response.to_dict())


if __name__ == '__main__':
    app()
