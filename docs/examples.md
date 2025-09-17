# Examples and Tutorials

This guide provides practical examples of how to use the COSI Consumer Framework.

## Basic Usage Example: Temperature-Based Drink Choice

This example demonstrates the basic concepts of the framework through a simple model where agents choose drinks based on temperature.

### Step 1: Setup and Imports

```python
# Add parent folder to Python path
import sys
sys.path.insert(0, "..")

from typing import Any
import numpy as np
from pydantic import Field

from cosi_consumer_framework import (
    Environment, 
    Agent, 
    AgentPerception, 
    ChoiceSet
)
```

### Step 2: Define Environment

The environment holds all objective information and coordinates the simulation. Here we create a temperature environment that randomly changes temperature each year:

```python
class TemperatureEnvironment(Environment):
    temperature: float = Field(15.0, description="Current temperature in degrees Celsius")

    def step(self):
        self.temperature = np.random.randint(0,40)
        print(f"{self.year}: Environment temperature changed to: {self.temperature}")
        super().step()
```

### Step 3: Define Perception

Perception is a two-part process: extracting information from the environment and then distorting it based on agent characteristics:

```python
class TemperaturePerception(AgentPerception):
    temperature: float = Field(..., description="Perceived temperature in degrees Celsius")
    
    @classmethod
    def get_information_from_environment(
            cls, agent: Any, environment: TemperatureEnvironment
        ) -> dict:
        """Extract information from the environment.
        
        Args:
            agent: The agent that is perceiving the information.
            environment: The environment in which the agent is located.

        Returns:
            Dictionary with the relevant information
        """
        return {"temperature": environment.temperature}
    
    def distort_information(self, agent: Any) -> None:
        """Distort the perceived information.
        
        Args:
            agent: The agent that is perceiving the information.
        """
        self.temperature += agent.temperature_bias
```

### Step 4: Define Choice Set

The choice set is triggered by perception and evaluates available options:

```python
class DrinkChoice(ChoiceSet):
    options: list[str] = Field(..., description="Available drink options")
    scores: dict[str, float] = Field(
        default_factory=dict, 
        description="Scores for each drink option"
    )
    temperature: float = Field(..., description="Perceived temperature in degrees Celsius")
    agent: Any = Field(..., description="The agent making the choice")

    @classmethod
    def trigger(cls, agent: Any, perception: TemperaturePerception) -> "DrinkChoice":
        """Trigger the choice set based on the agent's perception.
        
        Args:
            agent: The agent making the choice.
            perception: The agent's perception of the environment.

        Returns:
            An instance of the DrinkChoice class.
        """
        options = ["hot chocolate", "iced tea"]
        return cls( 
            options=options,
            agent=agent,
            temperature=perception.temperature
        )
    
    def evaluate(self):
        """Create evaluation score for each drink option"""
        self.scores = {
            o: (
                self.agent.drink_preference[o] 
                + self.agent.temperature_adjustment[o] * self.temperature
            ) 
            for o in self.options
        }
```

### Step 5: Define Agent

The agent ties everything together with its attributes and decision-making logic:

```python
class Person(Agent):
    drink_preference: dict[str, float] = Field(
        ...,
        description="Score for each drink option at zero degree Celsius"
    )
    temperature_adjustment: dict[str, float] = Field(
        ..., 
        description="Adjustment factor for drink preference based on temperature"
    )
    temperature_bias: float = Field(
        0.0, description="Bias in temperature perception (e.g., due to clothing)"
    )

    def perceive(self, environment: Environment) -> TemperaturePerception:
        return TemperaturePerception.perceive(self, environment)
    
    def trigger_choice(self, perception: TemperaturePerception):
        return DrinkChoice.trigger(agent=self, perception=perception)
    
    def choose(self, options: Any, perception: Any):
        best_option = max(options.scores, key=options.scores.get)
        print(
            f"{self.id}: It is {perception.temperature} of felt temperature!"
            f"I drink: {best_option}"
        )
```

### Step 6: Run the Simulation

```python
# Create environment and agent
my_env = TemperatureEnvironment()
me = Person(
    id="Alice",
    drink_preference={"hot chocolate": 20.0, "iced tea": 0},
    temperature_adjustment={"hot chocolate": -1, "iced tea": 1},
    temperature_bias=2.0
)
my_env.add(me)

# Run simulation for 20 steps
for i in range(20):
    print(f"\n--- Simulation step {i+1} ---")
    my_env.step()
```

This will produce output like:
```
--- Simulation step 1 ---
2020: Environment temperature changed to: 38
Person.Alice: It is 40.0 of felt temperature!I drink: iced tea

--- Simulation step 2 ---
2021: Environment temperature changed to: 6
Person.Alice: It is 8.0 of felt temperature!I drink: hot chocolate
```

## Key Framework Concepts

### Understanding the Framework Structure

The temperature example above demonstrates the four core components of the COSI Consumer Framework:

1. **Environment**: Holds the objective state of the world and coordinates agent interactions
2. **Perception**: How agents extract and potentially distort information from the environment  
3. **Choice Set**: The options available to agents and how they're evaluated
4. **Agent**: The decision-making entity that perceives, evaluates choices, and acts

### The Agent Decision Cycle

Each simulation step follows this pattern:
1. **Perceive**: Agent extracts information from environment and applies personal biases
2. **Trigger**: Agent determines what choices are available based on perception
3. **Evaluate**: Agent scores the available options  
4. **Choose**: Agent selects and executes the best option

### Tips for Building Your Own Models

#### Start Simple
Begin with basic agent behaviors and gradually add complexity:

```python
class SimpleAgent(Agent):
    """Start with minimal behavior."""
    def perceive(self, environment):
        return SimplePerception.perceive(self, environment)
    
    def trigger_choice(self, perception):
        return SimpleChoiceSet.trigger(self, perception)
    
    def choose(self, options, perception):
        # Implement simple rule-based decision
        pass
```

#### Test Components Separately
Test perception, choice sets, and decision-making independently:

```python
def test_perception():
    env = TemperatureEnvironment()
    agent = Person(id="test", drink_preference={"hot chocolate": 10, "iced tea": 5}, 
                   temperature_adjustment={"hot chocolate": -1, "iced tea": 1})
    env.add(agent)
    
    perception = agent.perceive(env)
    assert perception.temperature == env.temperature + agent.temperature_bias

def test_choice_set():
    perception = TemperaturePerception(temperature=25)
    agent = Person(id="test", drink_preference={"hot chocolate": 10, "iced tea": 5},
                   temperature_adjustment={"hot chocolate": -1, "iced tea": 1})
    choices = DrinkChoice.trigger(agent, perception)
    assert len(choices.options) == 2
```

#### Handle Edge Cases
Always consider boundary conditions and validate your model logic:

```python
def choose(self, options, perception):
    if not options.options:
        # Handle case with no options
        print(f"{self.id}: No drink options available!")
        return
    
    options.evaluate()
    if not options.scores:
        # Handle case where evaluation failed
        print(f"{self.id}: Could not evaluate options!")
        return
    
    # Normal decision-making logic
    best_option = max(options.scores, key=options.scores.get)
    print(f"{self.id}: Choosing {best_option}")
```

This simple but complete example demonstrates the power and flexibility of the COSI Consumer Framework for building agent-based models. You can extend this pattern to model complex systems across various domains by adding more sophisticated environments, perception mechanisms, and decision-making logic.