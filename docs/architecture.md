# Architecture Guide

This guide explains the design principles and architecture of the COSI Consumer Framework.

## Design Philosophy

The COSI Consumer Framework is built around several key principles:

1. **Agent-Based Modeling**: The framework centers around autonomous agents that can perceive, decide, and act
2. **Separation of Concerns**: Clear separation between perception, decision-making, and action
3. **Extensibility**: Abstract base classes allow for easy customization and extension
4. **Type Safety**: Heavy use of type hints and runtime validation
5. **Dependency Management**: Automatic tracking of object relationships and dependencies

## Core Architecture

### The Simulation Loop

```
Environment.step()
├── For each Agent:
│   ├── Agent.act(environment)
│   │   ├── perception = agent.perceive(environment)
│   │   ├── options = agent.trigger_choice(perception)
│   │   ├── options.evaluate()
│   │   └── agent.choose(options, perception)
│   └── ...
└── environment.report()
```

### Class Hierarchy

```
Registrable (SQLModel)
├── Agent (ABC)
│   └── [Your Agent Classes]
└── Asset (ABC)
    └── [Your Asset Classes]

AgentPerception (SQLModel, ABC)
└── [Your Perception Classes]

ChoiceSet (ABC, Generic)
└── [Your ChoiceSet Classes]

Environment
├── ObjectRegistry[Registrable]
└── Reports System
```

## Key Design Patterns

### 1. Registration Pattern

All objects that exist in the environment inherit from `Registrable`, which provides:
- Automatic unique ID generation (class-prefixed)
- Lifecycle management
- Reporting capabilities
- Type validation

```python
class MyAgent(Agent):
    wealth: int = 100

agent = MyAgent(id="1")  # Becomes "MyAgent.1"
```

### 2. Perception-Action Cycle

Agents follow a structured perception-action cycle:

1. **Perceive**: Gather information from environment
2. **Choose**: Determine available options
3. **Evaluate**: Assess options
4. **Act**: Make decisions and modify state

This separation allows for:
- Modular testing of each component
- Easy modification of decision-making logic
- Realistic modeling of bounded rationality

### 3. Generic Type System

The framework uses Python's generic types for type safety:

```python
class MyChoiceSet(ChoiceSet[MyOption, MyAgent, MyPerception]):
    # Type-safe implementation
    pass
```

### 4. Dependency Injection

The environment automatically manages object dependencies:
- Objects can reference other objects by ID
- Automatic validation of dependencies on registration
- Support for complex object relationships

## Data Flow

### 1. Object Registration
```
Object Creation → Validation → ID Assignment → Registry Storage → Dependency Check
```

### 2. Simulation Step
```
Environment.step() → Agent.act() → Perception → Choice → Evaluation → Action → Report
```

### 3. Reporting
```
Object.report() → Environment.reports → Data Collection → Analysis
```

## Extension Points

### Creating Custom Agents

```python
from cosi_consumer_framework import Agent, AgentPerception, ChoiceSet

class MyAgent(Agent):
    # Add your attributes
    balance: float = 0.0
    
    def perceive(self, environment) -> "MyPerception":
        # Implement perception logic
        return MyPerception.perceive(self, environment)
    
    def trigger_choice(self, perception) -> "MyChoiceSet":
        # Implement choice triggering
        return MyChoiceSet.trigger(self, perception)
    
    def choose(self, options, perception) -> None:
        # Implement decision-making
        pass
```

### Creating Custom Assets

```python
from cosi_consumer_framework import Asset

class Building(Asset):
    address: str
    value: float
    
    # Assets can have custom behavior and reporting
```

### Creating Custom Perceptions

```python
from cosi_consumer_framework import AgentPerception

class MyPerception(AgentPerception):
    market_price: float
    available_options: list[str]
    
    @classmethod
    def get_information_from_environment(cls, agent, environment):
        # Extract relevant information
        return {
            "market_price": environment.get_market_price(),
            "available_options": environment.get_options_for(agent)
        }
    
    def distort_information(self, agent):
        # Add noise or bias to perception
        self.market_price *= (1 + agent.perception_noise)
```

### Creating Custom Choice Sets

```python
from cosi_consumer_framework import ChoiceSet

class PurchaseChoiceSet(ChoiceSet):
    options: list[PurchaseOption]
    
    @classmethod
    def trigger(cls, agent, perception):
        # Determine available options
        options = determine_purchase_options(agent, perception)
        return cls(options=options)
    
    def evaluate(self):
        # Evaluate each option
        for option in self.options:
            option.utility = calculate_utility(option)
```

## Best Practices

### 1. Use Type Hints
Always provide type hints for better IDE support and runtime validation:

```python
def my_method(self, environment: Environment) -> AgentPerception:
    pass
```

### 2. Implement Proper Validation
Use Pydantic validators for custom validation:

```python
from pydantic import field_validator

class MyAgent(Agent):
    balance: float
    
    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v):
        if v < 0:
            raise ValueError('Balance cannot be negative')
        return v
```

### 3. Handle Dependencies Carefully
When objects reference each other, ensure proper registration order:

```python
# Create assets first
building = Building(id="main_building")
env.add(building)

# Then create agents that reference assets
agent = MyAgent(id="agent1", building_id="Building.main_building")
env.add(agent)
```

### 4. Use Meaningful IDs
Choose descriptive IDs that make debugging easier:

```python
agent = MyAgent(id="household_downtown_family_4")
```

### 5. Implement Comprehensive Reporting
Override the `report()` method to provide detailed state information:

```python
def report(self) -> dict[str, dict[str, Any]]:
    report = super().report()
    report[self.class_name]["custom_metrics"] = self.calculate_metrics()
    return report
```

## Performance Considerations

### 1. Object Creation
- Objects are validated on creation, which has some overhead
- Batch object creation when possible
- Use `create_from_dataframe()` for bulk creation

### 2. Simulation Steps
- The simulation loop calls methods on all agents each step
- Consider implementing early exit conditions
- Use efficient data structures for large populations

### 3. Reporting
- Reports are generated each step for all reporting objects
- Set `is_reporting=False` for objects that don't need tracking
- Consider periodic rather than continuous reporting for large simulations

## Error Handling

The framework provides several layers of error handling:

1. **Pydantic Validation**: Automatic validation of data types and constraints
2. **Registration Validation**: Checks for unique IDs and dependencies
3. **Runtime Checks**: Validation during simulation execution

Common error patterns and solutions:

```python
# ID conflicts
try:
    agent = MyAgent(id="duplicate_id")
except ValueError as e:
    # Handle duplicate ID

# Missing dependencies
try:
    env.add(agent_with_building_reference)
except ValueError as e:
    # Ensure referenced building exists first

# Type validation
try:
    agent.balance = "invalid"  # Should be float
except ValidationError as e:
    # Handle validation error
```