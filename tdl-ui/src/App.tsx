import React, {useState} from 'react';
import './App.css';
import {QueryClient, QueryClientProvider, useMutation, useQuery} from "react-query";
import axios from "axios";

const queryClient = new QueryClient();
const http = axios.create({
    baseURL: "http://localhost:5000",
});

interface ITask {
    id: number;
    text: string;
    done: boolean;
}

async function getTasks(): Promise<ITask[]> {
    const res = await http.get('/tasks/');
    return res.data;
}

async function addTask(text: string) {
    await http.put("/tasks/", {text});
}

async function updateTaskDone(task: ITask) {
    await http.post(`/tasks/${task.id}/`, {done: !task.done});
}

async function deleteTask(taskId: number) {
    await http.delete(`/tasks/${taskId}/`);
}

interface ITaskProps {
    task: ITask
}

function Task(props: ITaskProps) {
    const mutUpdateDone = useMutation(updateTaskDone, {
        onSuccess: async () => {
            await queryClient.invalidateQueries('tasks');
        }
    });
    const mutDelete = useMutation(deleteTask, {
        onSuccess: async () => {
            await queryClient.invalidateQueries('tasks');
        }
    });
    return (
        <li>
            <span style={{textDecoration: props.task.done ? "line-through" : ""}}>{props.task.text}</span>
            &nbsp;
            <button onClick={async () => {
                await mutUpdateDone.mutate(props.task);
            }}>{props.task.done ? "not done" : "done"}
            </button>
            &nbsp;
            <button onClick={async () => {
                await mutDelete.mutate(props.task.id);
            }}>X
            </button>
        </li>
    )
}

function AddTask() {
    const [value, setValue] = useState("");
    const mutAdd = useMutation(addTask, {
        onSuccess: async () => {
            await queryClient.invalidateQueries('tasks');
        }
    })
    return (
        <div>
            <h3>add task</h3>
            <input type={"text"} value={value} onChange={(e: any) => {
                setValue(e.target.value);
            }}/>
            <button onClick={async () => {
                await mutAdd.mutate(value);
                setValue("");
            }}>Submit</button>
        </div>
    );
}

function Tasks() {
    const {data, isLoading, isError} = useQuery('tasks', getTasks);

    if (isLoading) {
        return <b>Loading</b>;
    }
    if (isError) {
        return <b style={{color: "red"}}>Error code X</b>
    }
    return (
        <ul>
            {data?.map(t => (
                <Task key={t.id} task={t}/>
            ))}
        </ul>
    );
}

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <div className="App">
                <Tasks/>
                <AddTask/>
            </div>
        </QueryClientProvider>
    );
}

export default App;
