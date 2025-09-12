# API Reference

This document provides detailed documentation for all classes and methods in the COSI Consumer Framework.

## Core Classes

### Environment

The `Environment` class is the central container that manages all agents and assets in the simulation.

#### Constructor

```python
Environment(year: int = 2020)
```

**Parameters:**
- `year` (int): The starting year of the simulation. Default: 2020

#### Properties

- `year` (int): The current year of the simulation
- `assets` (dict[str, Registrable]): Dictionary of all registered assets with their IDs as keys
- `agents` (dict[str, Registrable]): Dictionary of all registered agents with their IDs as keys  
- `reports` (dict[str, list[dict[str, Any]]]): Reports from all registered objects, with object IDs as keys and lists of report data as values

#### Methods

##### `add(objects)`
Register objects (assets or agents) within the environment.

**Parameters:**
- `objects`: A single object, list of objects, or nested list of objects to be registered. Can be assets, agents, or a mix of both.

**Raises:**
- `TypeError`: If objects are not Asset or Agent instances
- `ValueError`: If object dependencies are not met

##### `delete(objects)`
Delete objects (assets or agents) from the environment.

**Parameters:**
- `objects`: A single object, list of objects, or nested list of objects to be deleted

##### `get(id: str)`
Get an object (asset or agent) from the environment by ID.

**Parameters:**
- `id` (str): The ID of the object to retrieve

**Returns:**
- The object with the specified ID, or None if not found

##### `is_in(obj)`
Check if an object is registered in the environment.

**Parameters:**
- `obj`: The object to check, can be an Asset, Agent, or a string representing the ID

**Returns:**
- `bool`: True if the object is registered, False otherwise

##### `get_list(class_name=None)`
Get all registered objects of a certain type.

**Parameters:**
- `class_name` (str | type | None): The class name of the objects to retrieve. If None, returns all objects.

**Returns:**
- `list`: A list of all registered objects of the specified type

##### `step()`
Advance the environment by one year. This method:
1. Calls `act()` on all agents
2. Generates reports from all reporting objects
3. Increments the year

##### `report()`
Generate reports from all objects that have `is_reporting=True`.

---

### Agent

Abstract base class for any object that can perform actions during a simulation step.

#### Abstract Methods

##### `perceive(environment: Environment) -> AgentPerception`
Perceive the environment and return an AgentPerception object.

**Parameters:**
- `environment` (Environment): The environment in which the agent operates

**Returns:**
- `AgentPerception`: An object containing the agent's perception of the environment

##### `trigger_choice(perception: Any) -> ChoiceSet`
Given the agent's perception, determine the set of available options.

**Parameters:**
- `perception` (AgentPerception): The agent's perception of the environment

**Returns:**
- `ChoiceSet`: A choice set containing the available options for the agent

##### `choose(options: Any, perception: Any) -> None`
Make a choice based on the available options.

**Parameters:**
- `options` (ChoiceSet): The choice set containing the available options
- `perception` (AgentPerception): The agent's perception of the environment

#### Methods

##### `act(environment: Environment)`
Perform a step in the simulation. This method orchestrates the agent's behavior:
1. Perceive the environment to get the current state
2. Trigger a choice set based on the perception  
3. Evaluate the options in the choice set
4. Make a choice based on the evaluation

**Parameters:**
- `environment` (Environment): The environment in which the agent is located

---

### Asset

Abstract base class for any object that can be registered as an asset in the environment. Assets represent various entities in the simulation, such as buildings, heating systems, or other components.

Assets inherit all functionality from `Registrable` and can be registered in the environment, tracked, and report their state.

---

### AgentPerception

Abstract class for perceptions of an agent. Perceptions take place in two steps:
1. The agent perceives the environment and creates a perception object
2. The perception object can be distorted to simulate noise in the perception

#### Class Methods

##### `perceive(agent: Any, environment: Environment) -> Any`
Create a perception from the environment.

**Parameters:**
- `agent`: The agent that is perceiving
- `environment` (Environment): The environment in which the agent is located

**Returns:**
- An AgentPerception object containing the relevant information

#### Abstract Methods

##### `get_information_from_environment(agent: Any, environment: Environment) -> dict`
Get information from the environment and instantiate the perception.

**Parameters:**
- `agent`: The agent that is perceiving the environment
- `environment` (Environment): The environment in which the agent is located

**Returns:**
- `dict`: Dictionary containing the relevant information for creating the perception

##### `distort_information(agent: Any) -> None`
Distort the information in the perception to simulate noise.

**Parameters:**
- `agent`: The agent that is perceiving the environment

---

### ChoiceSet

A class to represent a choice set for an agent. A choice set contains a list of options that the agent can choose from and performs their evaluation.

#### Abstract Methods

##### `trigger(agent: Any, perception: Any) -> ChoiceSet`
Trigger function to determine the available options for the agent.

**Parameters:**
- `agent`: The agent for which the choice set is created
- `perception`: The perception of the agent, containing information about the environment and the agent's state

**Returns:**
- `ChoiceSet`: A choice set containing the available options

##### `evaluate() -> None`
Evaluate the available options in the choice set.

This method should be implemented by subclasses to perform the evaluation of the options based on the agent's preferences and the environment.

---

### Registrable

Base class that allows registration in the environment. The ID provided to the constructor is automatically prefixed with the class name to ensure uniqueness across different classes.

#### Attributes

- `id` (str): The ID of the object, automatically prefixed with class name
- `is_reporting` (bool): Flag to indicate if the object is reporting. Default: True

#### Properties

##### `class_name` (str)
Get the class name of the object.

##### `is_active` (bool)
Check if the object is active.

#### Methods

##### `destroy()`
Delete the object and remove its ID from the used IDs set.

##### `report() -> dict[str, dict[str, Any]]`
Report the object as a dictionary.

**Returns:**
- `dict`: A dictionary with the class name as key and the object's attributes as value

##### `create_from_dataframe(df: pd.DataFrame) -> list[Registrable]`
Class method to create instances from a DataFrame.

**Parameters:**
- `df` (pd.DataFrame): A DataFrame containing the data to create instances

**Returns:**
- `list[Registrable]`: List of instances created from the DataFrame

---

### ObjectRegistry

A registry for objects that can be registered and deleted. Manages object storage and retrieval by ID and class.

#### Methods

##### `add(objects: T | list[T]) -> None`
Register an object or list of objects in the registry.

##### `delete(objects: T | list[T]) -> None`
Delete an object or list of objects from the registry.

##### `object_is_registered(object: Registrable | str) -> bool`
Check if an object is registered in the registry.

##### `list_objects(class_name: str | type | None = None) -> list[Any]`
List all registered objects of a certain type.

##### `get_item(id: str) -> T`
Get an item from the registry by ID.

---

## Utility Functions

### Discounting

#### `discounted_sum(values: list[int | float], delta: float, initial_period: int = 0)`

Calculate the discounted sum of a list of numbers.

**Parameters:**
- `values` (list[int | float]): The list of numbers to be discounted
- `delta` (float): The discount factor
- `initial_period` (int): The initial period of the list. Default: 0

**Returns:**
- `float`: The discounted sum of the values

**Formula:**
```
sum(values[i] * delta^(i + initial_period) for i in range(len(values)))
```

## Type Annotations

The framework makes extensive use of Python type hints and generic types:

- `Generic[T]` classes allow for type-safe specialization
- `TYPE_CHECKING` imports prevent circular dependencies
- All public methods include full type annotations
- Pydantic/SQLModel integration provides runtime validation