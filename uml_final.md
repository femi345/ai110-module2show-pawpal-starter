# PawPal+ — Final UML Diagram

```mermaid
classDiagram
    class Task {
        +str description
        +str time
        +int duration_minutes
        +str frequency
        +str priority
        +bool completed
        +date due_date
        +str id
        +mark_complete() Task | None
        +__str__() str
    }

    class Pet {
        +str name
        +str species
        +List~Task~ tasks
        +add_task(task: Task) None
        +remove_task(task_id: str) bool
        +task_count() int
        +__str__() str
    }

    class Owner {
        +str name
        +List~Pet~ pets
        +add_pet(pet: Pet) None
        +remove_pet(pet_name: str) bool
        +get_all_tasks() List~tuple~
        +__str__() str
    }

    class Scheduler {
        +Owner owner
        +all_tasks() List~tuple~
        +sort_by_time(pairs) List~tuple~
        +sort_by_priority(pairs) List~tuple~
        +filter_tasks(pet_name, completed, due_date) List~tuple~
        +detect_conflicts() List~str~
        +mark_task_complete(pet, task) Task | None
        +todays_schedule() List~tuple~
        +format_schedule(pairs) str
    }

    Owner "1" --> "0..*" Pet : has
    Pet "1" --> "0..*" Task : owns
    Scheduler "1" --> "1" Owner : queries
```

## Relationship notes

- `Owner` **has** zero or more `Pet` objects (composition — pets belong to one owner).
- `Pet` **owns** zero or more `Task` objects (composition — tasks are attached to a pet).
- `Scheduler` **queries** the `Owner` to retrieve all `(Pet, Task)` pairs without storing them — it is stateless beyond holding a reference to the owner.
- `mark_complete()` on a `Task` returns a *new* `Task` instance for recurring tasks (daily/weekly), ensuring the original is immutably closed and the follow-up is a first-class object.
