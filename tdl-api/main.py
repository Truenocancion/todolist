from fastapi import FastAPI, HTTPException
import uvicorn
from tortoise.models import Model
from tortoise import fields, Tortoise
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware


class Task(Model):
    id = fields.BigIntField(pk=True)
    text = fields.TextField()
    done = fields.BooleanField(default=False)
    deleted = fields.BooleanField(default=False)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.on_event('startup')
async def on_startup():
    await Tortoise.init(
        db_url='postgres://dev:dev@127.0.0.1:5432/todolist',
        modules={'models': ['main']}
    )
    await Tortoise.generate_schemas()


@app.get('/tasks/')
async def get_tasks():
    tasks = await Task.filter(deleted=False).all().order_by('done', 'id')
    return [{'id': t.id, 'text': t.text, 'done': t.done} for t in tasks]


# for future
@app.get('/tasks/{task_id}/')
async def get_task(task_id: int):
    task = await Task.filter(deleted=False).get_or_none(id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        'id': task.id,
        'text': task.text,
        'done': task.done
    }


class PutTaskRequest(BaseModel):
    text: str


@app.put('/tasks/')
async def put_task(req: PutTaskRequest):
    task = Task()
    task.text = req.text
    await task.save()
    return {'id': task.id}


class UpdateTaskRequest(BaseModel):
    text: Optional[str]
    done: Optional[bool]


@app.post('/tasks/{task_id}/')
async def update_task(task_id: int, req: UpdateTaskRequest):
    task = await Task.filter(deleted=False).get_or_none(id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    update_fields = []
    if req.text is not None:
        task.text = req.text
        update_fields.append('text')
    if req.done is not None:
        task.done = req.done
        update_fields.append('done')
    if len(update_fields) > 0:
        await task.save(update_fields=update_fields)
    return {'id': task_id}


@app.delete('/tasks/{task_id}/')
async def delete_task(task_id: int):
    task = await Task.filter(deleted=False).get_or_none(id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.deleted = True
    await task.save(update_fields=['deleted'])
    return {}


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=5000, reload=True)
