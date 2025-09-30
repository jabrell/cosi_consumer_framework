import pytest

from cosi_consumer_framework import Asset, ConsumerModel, Environment
from .conftest import SampleAgent, SampleAsset


def test_consumer_model_initialization():
    """Test that ConsumerModel can be initialized with and without an environment."""
    # With default environment
    model = ConsumerModel(year=2025)
    assert model.year == 2025
    assert isinstance(model.environment, Environment)
    
    # With provided environment
    env = Environment(year=2030)
    model2 = ConsumerModel(environment=env)
    assert model2.year == 2030
    assert model2.environment is env


def test_add_agents(agent_list: list[SampleAgent]):
    """Test that agents can be added to the model."""
    model = ConsumerModel()
    model.add_agents(agent_list)
    
    for agent in agent_list:
        assert model.agent_is_in(agent)
    
    assert model.get_agent_list(SampleAgent) == agent_list
    assert model.get_agent_list("SampleAgent") == agent_list
    assert model.get_agent_list() == agent_list


def test_add_single_agent(agent1: SampleAgent):
    """Test that a single agent can be added to the model."""
    model = ConsumerModel()
    model.add_agents(agent1)
    
    assert model.agent_is_in(agent1)
    assert agent1 in model.get_agent_list()


def test_add_agents_with_asset_dependency():
    """Test that agents with asset dependencies are checked."""
    model = ConsumerModel()
    
    class House(Asset):
        pass
    
    class Household(SampleAgent):
        house_id: str
    
    # Agent references an asset not in the environment
    household = Household(id="household1", house_id="House.house1")
    with pytest.raises(ValueError, match="not registered in the environment"):
        model.add_agents(household)
    
    # Add the asset first
    house = House(id="house1")
    model.environment.add(house)
    household.house_id = house.id
    model.add_agents(household)
    
    assert model.agent_is_in(household)
    
    # Clean up
    household.destroy()
    house.destroy()


def test_delete_single_agent(agent1: SampleAgent):
    """Test that a single agent can be deleted from the model."""
    model = ConsumerModel()
    model.add_agents(agent1)
    assert model.agent_is_in(agent1)
    
    model.delete_agents(agent1)
    assert not model.agent_is_in(agent1)


def test_delete_agent_list(agent_list: list[SampleAgent]):
    """Test that a list of agents can be deleted from the model."""
    model = ConsumerModel()
    model.add_agents(agent_list)
    
    for agent in agent_list:
        assert model.agent_is_in(agent)
    
    model.delete_agents(agent_list)
    
    for agent in agent_list:
        assert not model.agent_is_in(agent)


def test_get_agent(agent1: SampleAgent):
    """Test that an agent can be retrieved by ID."""
    model = ConsumerModel()
    model.add_agents(agent1)
    
    retrieved = model.get_agent(agent1.id)
    assert retrieved is agent1
    
    # Non-existent agent
    with pytest.raises(ValueError):
        model.get_agent("SampleAgent.non_existent")


def test_add_nested_agent_lists(agent_list: list[SampleAgent]):
    """Test that nested lists of agents can be added."""
    model = ConsumerModel()
    
    agent_list2 = [SampleAgent(id=f"nested_agent{i}") for i in range(3)]
    nested_agents = [agent_list, agent_list2]
    
    model.add_agents(nested_agents)
    
    for agent in agent_list:
        assert model.agent_is_in(agent)
    for agent in agent_list2:
        assert model.agent_is_in(agent)
    
    # Clean up
    for agent in agent_list2:
        agent.destroy()


def test_delete_nested_agent_lists(agent_list: list[SampleAgent]):
    """Test that nested lists of agents can be deleted."""
    model = ConsumerModel()
    
    agent_list2 = [SampleAgent(id=f"nested_agent{i}") for i in range(3)]
    nested_agents = [agent_list, agent_list2]
    
    model.add_agents(nested_agents)
    model.delete_agents(nested_agents)
    
    for agent in agent_list:
        assert not model.agent_is_in(agent)
    for agent in agent_list2:
        assert not model.agent_is_in(agent)
    
    # Clean up
    for agent in agent_list2:
        agent.destroy()


def test_step_executes_agents():
    """Test that the step method executes agents and advances time."""
    model = ConsumerModel(year=2020)
    
    class TestAgent(SampleAgent):
        acted: bool = False
        
        def act(self, environment: Environment):
            self.acted = True
    
    agent = TestAgent(id="test_agent")
    model.add_agents(agent)
    
    assert agent.acted is False
    assert model.year == 2020
    
    model.step()
    
    assert agent.acted is True
    assert model.year == 2021
    
    # Clean up
    agent.destroy()


def test_agent_reporting():
    """Test that agent reporting works correctly."""
    model = ConsumerModel()
    
    agent1 = SampleAgent(id="reporting_agent")
    agent2 = SampleAgent(id="non_reporting_agent")
    agent2.is_reporting = False
    
    model.add_agents([agent1, agent2])
    model.step()
    
    reports = model.reports
    assert agent1.class_name in reports
    assert len(reports[agent1.class_name]) == 1
    
    # Check that only agent1's report is present, not agent2's
    # Both agents have the same class name, so we check the actual report IDs
    report_ids = [r['id'] for r in reports[agent1.class_name]]
    assert agent1.id in report_ids
    assert agent2.id not in report_ids
    
    # Clean up
    agent1.destroy()
    agent2.destroy()


def test_combined_asset_and_agent_reporting():
    """Test that both asset and agent reports are combined."""
    model = ConsumerModel()
    
    asset = SampleAsset(id="test_asset")
    agent = SampleAgent(id="test_agent")
    
    model.environment.add(asset)
    model.add_agents(agent)
    
    model.step()
    
    reports = model.reports
    assert asset.class_name in reports
    assert agent.class_name in reports
    assert len(reports[asset.class_name]) == 1
    assert len(reports[agent.class_name]) == 1
    
    # Clean up
    asset.destroy()
    agent.destroy()


def test_add_invalid_agent_type():
    """Test that adding invalid types as agents raises TypeError."""
    model = ConsumerModel()
    
    asset = SampleAsset(id="not_an_agent")
    with pytest.raises(TypeError, match="Expected Agent"):
        model.add_agents(asset)
    
    with pytest.raises(TypeError):
        model.add_agents("invalid")
    
    with pytest.raises(TypeError):
        model.add_agents(123)
    
    # Clean up
    asset.destroy()


def test_add_agent_twice():
    """Test that adding the same agent twice raises an error."""
    model = ConsumerModel()
    agent = SampleAgent(id="duplicate_agent")
    
    model.add_agents(agent)
    with pytest.raises(ValueError, match="already registered"):
        model.add_agents(agent)
    
    # Clean up
    agent.destroy()


def test_multiple_steps():
    """Test that multiple steps work correctly and time advances."""
    model = ConsumerModel(year=2020)
    
    class CountingAgent(SampleAgent):
        step_count: int = 0
        
        def act(self, environment: Environment):
            self.step_count += 1
    
    agent = CountingAgent(id="counting_agent")
    model.add_agents(agent)
    
    for i in range(1, 6):
        model.step()
        assert agent.step_count == i
        assert model.year == 2020 + i
    
    # Clean up
    agent.destroy()


def test_agents_access_environment():
    """Test that agents can access and perceive the environment."""
    model = ConsumerModel()
    
    class House(Asset):
        value: int = 100
    
    class Household(SampleAgent):
        perceived_value: int = 0
        
        def act(self, environment: Environment):
            house = environment.get("House.my_house")
            self.perceived_value = house.value
    
    house = House(id="my_house", value=250)
    household = Household(id="household1")
    
    model.environment.add(house)
    model.add_agents(household)
    
    model.step()
    
    assert household.perceived_value == 250
    
    # Clean up
    house.destroy()
    household.destroy()


def test_empty_model_step():
    """Test that stepping an empty model doesn't cause errors."""
    model = ConsumerModel(year=2020)
    
    model.step()
    assert model.year == 2021
    assert len(model.reports) == 0
