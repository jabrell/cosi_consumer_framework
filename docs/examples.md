# Examples and Tutorials

This guide provides practical examples of how to use the COSI Consumer Framework.

## Example 1: Simple Wealth Transfer Model

This example demonstrates the basic concepts of the framework through a simple model where agents can transfer wealth between each other.

### Step 1: Define Your Agent

```python
from cosi_consumer_framework import Agent, AgentPerception, ChoiceSet, Environment
from typing import Any
import random

class Person(Agent):
    """A simple agent that represents a person with wealth."""
    wealth: int = 1  # Starting wealth
    
    def perceive(self, environment: Environment) -> "WealthPerception":
        """Perceive the current state of wealth in the environment."""
        return WealthPerception.perceive(self, environment)
    
    def trigger_choice(self, perception: "WealthPerception") -> "TransferChoiceSet":
        """Determine if and how much wealth to transfer."""
        return TransferChoiceSet.trigger(self, perception)
    
    def choose(self, options: "TransferChoiceSet", perception: "WealthPerception") -> None:
        """Make a choice about wealth transfer."""
        if options.can_transfer and self.wealth > 0:
            # Find another agent to transfer to
            target_agent = random.choice(list(perception.other_agents.values()))
            # Transfer 1 unit of wealth
            self.wealth -= 1
            target_agent.wealth += 1
            print(f"{self.id} transferred 1 wealth to {target_agent.id}")
```

### Step 2: Define Perception

```python
class WealthPerception(AgentPerception):
    """Represents what an agent perceives about wealth in the environment."""
    total_wealth: int
    other_agents: dict[str, Person]
    transfer_opportunity: bool
    
    @classmethod
    def get_information_from_environment(cls, agent: Person, environment: Environment) -> dict:
        """Extract wealth information from the environment."""
        other_agents = {
            aid: a for aid, a in environment.agents.items() 
            if aid != agent.id
        }
        total_wealth = sum(a.wealth for a in environment.agents.values())
        
        # Simple rule: transfer opportunity exists if agent has wealth and others exist
        transfer_opportunity = len(other_agents) > 0 and agent.wealth > 0
        
        return {
            "total_wealth": total_wealth,
            "other_agents": other_agents,
            "transfer_opportunity": transfer_opportunity
        }
    
    def distort_information(self, agent: Person) -> None:
        """Add noise to perception (no distortion in this simple example)."""
        pass
```

### Step 3: Define Choice Set

```python
class TransferChoiceSet(ChoiceSet):
    """Represents the choice of whether to transfer wealth."""
    can_transfer: bool
    transfer_amount: int = 0
    
    @classmethod
    def trigger(cls, agent: Person, perception: WealthPerception) -> "TransferChoiceSet":
        """Determine if transfer is possible."""
        return cls(
            can_transfer=perception.transfer_opportunity,
            transfer_amount=1 if perception.transfer_opportunity else 0
        )
    
    def evaluate(self) -> None:
        """Evaluate the transfer option (simple rule-based)."""
        # In this simple example, evaluation is already done in trigger
        pass
```

### Step 4: Run the Simulation

```python
# Create environment
env = Environment(year=2024)

# Create agents
agents = [Person(id=f"person_{i}") for i in range(5)]

# Add agents to environment
env.add(agents)

# Print initial state
print("Initial wealth distribution:")
for agent_id, agent in env.agents.items():
    print(f"  {agent_id}: {agent.wealth}")

# Run simulation for 10 steps
print("\nRunning simulation...")
for step in range(10):
    print(f"\nStep {step + 1}:")
    env.step()
    
    # Print current wealth distribution
    total_wealth = sum(agent.wealth for agent in env.agents.values())
    print(f"  Total wealth: {total_wealth}")
    for agent_id, agent in env.agents.items():
        print(f"  {agent_id}: {agent.wealth}")

# Access simulation reports
reports = env.reports
print(f"\nGenerated {len(reports)} report entries")
```

## Example 2: Housing Market Model

This example shows a more complex model where agents can buy and sell houses.

### Assets: Houses

```python
from cosi_consumer_framework import Asset

class House(Asset):
    """Represents a house that can be bought and sold."""
    price: float
    size: int  # square meters
    location: str
    owner_id: str | None = None
    
    @property
    def is_available(self) -> bool:
        """Check if house is available for purchase."""
        return self.owner_id is None
    
    def sell_to(self, buyer_id: str) -> None:
        """Transfer ownership to a buyer."""
        self.owner_id = buyer_id
    
    def report(self) -> dict[str, dict[str, Any]]:
        """Custom reporting for houses."""
        report = super().report()
        report[self.class_name]["is_available"] = self.is_available
        return report
```

### Agents: Home Buyers

```python
class HomeBuyer(Agent):
    """An agent that can buy houses."""
    budget: float
    preferred_size: int
    current_house_id: str | None = None
    
    def perceive(self, environment: Environment) -> "HousingPerception":
        return HousingPerception.perceive(self, environment)
    
    def trigger_choice(self, perception: "HousingPerception") -> "HouseChoiceSet":
        return HouseChoiceSet.trigger(self, perception)
    
    def choose(self, options: "HouseChoiceSet", perception: "HousingPerception") -> None:
        if options.affordable_houses and self.current_house_id is None:
            # Choose the house closest to preferred size within budget
            best_house = min(
                options.affordable_houses,
                key=lambda h: abs(h.size - self.preferred_size)
            )
            
            if best_house.price <= self.budget:
                # Buy the house
                best_house.sell_to(self.id)
                self.budget -= best_house.price
                self.current_house_id = best_house.id
                print(f"{self.id} bought {best_house.id} for ${best_house.price:,.0f}")

class HousingPerception(AgentPerception):
    """Perception of the housing market."""
    available_houses: list[House]
    average_price: float
    
    @classmethod
    def get_information_from_environment(cls, agent: HomeBuyer, environment: Environment) -> dict:
        available_houses = [
            house for house in environment.assets.values()
            if isinstance(house, House) and house.is_available
        ]
        
        avg_price = (
            sum(h.price for h in available_houses) / len(available_houses)
            if available_houses else 0
        )
        
        return {
            "available_houses": available_houses,
            "average_price": avg_price
        }
    
    def distort_information(self, agent: HomeBuyer) -> None:
        """Add some noise to price perception."""
        noise_factor = random.uniform(0.95, 1.05)
        self.average_price *= noise_factor

class HouseChoiceSet(ChoiceSet):
    """Choice set for house purchases."""
    affordable_houses: list[House]
    
    @classmethod
    def trigger(cls, agent: HomeBuyer, perception: HousingPerception) -> "HouseChoiceSet":
        affordable = [
            house for house in perception.available_houses
            if house.price <= agent.budget
        ]
        return cls(affordable_houses=affordable)
    
    def evaluate(self) -> None:
        """Evaluate houses by price and size preference."""
        # Evaluation logic could be more sophisticated
        pass
```

### Running the Housing Market Simulation

```python
# Create environment
env = Environment(year=2024)

# Create houses
houses = [
    House(id=f"house_{i}", price=200000 + i*50000, size=100 + i*20, location=f"District_{i%3}")
    for i in range(10)
]

# Create home buyers
buyers = [
    HomeBuyer(
        id=f"buyer_{i}", 
        budget=250000 + i*100000, 
        preferred_size=120 + i*10
    )
    for i in range(5)
]

# Add to environment
env.add(houses + buyers)

# Run simulation
print("Housing Market Simulation")
print("=" * 40)

for step in range(5):
    print(f"\nStep {step + 1}:")
    env.step()
    
    # Show market status
    available = [h for h in houses if h.is_available]
    sold = [h for h in houses if not h.is_available]
    print(f"  Available houses: {len(available)}")
    print(f"  Sold houses: {len(sold)}")
```

## Example 3: Energy System Model

This example demonstrates how to model energy production and consumption.

### Energy Assets

```python
class PowerPlant(Asset):
    """A power plant that generates electricity."""
    capacity: float  # MW
    fuel_type: str
    efficiency: float
    current_output: float = 0.0
    
    def generate_power(self, demand: float) -> float:
        """Generate power up to capacity."""
        self.current_output = min(demand, self.capacity)
        return self.current_output

class Battery(Asset):
    """Energy storage system."""
    capacity: float  # MWh
    current_charge: float = 0.0
    charge_rate: float  # MW
    
    def charge(self, power: float, hours: float = 1.0) -> float:
        """Charge the battery and return power actually stored."""
        max_charge = min(power * hours, self.charge_rate * hours)
        available_capacity = self.capacity - self.current_charge
        actual_charge = min(max_charge, available_capacity)
        self.current_charge += actual_charge
        return actual_charge
    
    def discharge(self, power_needed: float, hours: float = 1.0) -> float:
        """Discharge the battery and return power provided."""
        max_discharge = min(power_needed * hours, self.charge_rate * hours)
        available_power = min(max_discharge, self.current_charge)
        self.current_charge -= available_power
        return available_power
```

### Energy Manager Agent

```python
class EnergyManager(Agent):
    """Manages energy production and storage."""
    total_demand: float = 100.0  # MW
    
    def perceive(self, environment: Environment) -> "EnergyPerception":
        return EnergyPerception.perceive(self, environment)
    
    def trigger_choice(self, perception: "EnergyPerception") -> "EnergyChoiceSet":
        return EnergyChoiceSet.trigger(self, perception)
    
    def choose(self, options: "EnergyChoiceSet", perception: "EnergyPerception") -> None:
        # Simple strategy: use cheapest sources first
        remaining_demand = self.total_demand
        
        # First, try to use stored energy
        for battery in perception.batteries:
            if remaining_demand <= 0:
                break
            power_used = battery.discharge(remaining_demand)
            remaining_demand -= power_used
        
        # Then use power plants
        for plant in perception.power_plants:
            if remaining_demand <= 0:
                break
            power_generated = plant.generate_power(remaining_demand)
            remaining_demand -= power_generated
        
        print(f"Energy demand: {self.total_demand} MW, Unmet: {remaining_demand} MW")

class EnergyPerception(AgentPerception):
    """Perception of energy system state."""
    power_plants: list[PowerPlant]
    batteries: list[Battery]
    total_capacity: float
    
    @classmethod
    def get_information_from_environment(cls, agent: EnergyManager, environment: Environment) -> dict:
        power_plants = [
            asset for asset in environment.assets.values()
            if isinstance(asset, PowerPlant)
        ]
        batteries = [
            asset for asset in environment.assets.values()
            if isinstance(asset, Battery)
        ]
        
        total_capacity = sum(p.capacity for p in power_plants)
        
        return {
            "power_plants": power_plants,
            "batteries": batteries,
            "total_capacity": total_capacity
        }
    
    def distort_information(self, agent: EnergyManager) -> None:
        """No distortion in this example."""
        pass

class EnergyChoiceSet(ChoiceSet):
    """Choices for energy management."""
    strategy: str = "cost_minimization"
    
    @classmethod
    def trigger(cls, agent: EnergyManager, perception: EnergyPerception) -> "EnergyChoiceSet":
        return cls()
    
    def evaluate(self) -> None:
        """Evaluate energy management strategies."""
        pass
```

## Tips for Building Your Own Models

### 1. Start Simple
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

### 2. Use Composition
Build complex behaviors by combining simple components:

```python
class ComplexAgent(Agent):
    """Combine multiple behaviors."""
    financial_behavior: FinancialBehavior
    social_behavior: SocialBehavior
    
    def choose(self, options, perception):
        # Combine insights from different behaviors
        financial_score = self.financial_behavior.evaluate(options)
        social_score = self.social_behavior.evaluate(options)
        # Make decision based on combined scores
```

### 3. Test Components Separately
Test perception, choice sets, and decision-making independently:

```python
def test_perception():
    env = Environment()
    agent = MyAgent(id="test")
    env.add(agent)
    
    perception = agent.perceive(env)
    assert perception.some_property == expected_value

def test_choice_set():
    perception = MyPerception(...)
    choices = MyChoiceSet.trigger(agent, perception)
    assert len(choices.options) > 0
```

### 4. Use Meaningful Metrics
Implement comprehensive reporting to understand your model:

```python
class MyAgent(Agent):
    def report(self):
        report = super().report()
        report[self.class_name].update({
            "efficiency": self.calculate_efficiency(),
            "satisfaction": self.calculate_satisfaction(),
            "interactions": self.interaction_count
        })
        return report
```

### 5. Handle Edge Cases
Always consider boundary conditions:

```python
def choose(self, options, perception):
    if not options.available_options:
        # Handle case with no options
        return
    
    if self.budget <= 0:
        # Handle case with no resources
        return
    
    # Normal decision-making logic
```

These examples demonstrate the flexibility and power of the COSI Consumer Framework for building agent-based models across various domains.