import pytest
from cosi_consumer_framework import Asset, Agent, AgentPerception, ChoiceSet


class SampleAsset(Asset):
    pass


class SamplePerception(AgentPerception):
    """Minimal perception for testing."""
    
    @classmethod
    def get_information_from_environment(cls, agent, environment):
        return {}
    
    def distort_information(self, agent):
        pass


class SampleChoiceSet(ChoiceSet):
    """Minimal choice set for testing."""
    
    @classmethod
    def trigger(cls, agent, perception):
        return cls()
    
    def evaluate(self):
        pass


class SampleAgent(Agent):
    def perceive(self, environment):
        return SamplePerception.perceive(self, environment)

    def trigger_choice(self, perception):
        return SampleChoiceSet.trigger(self, perception)

    def choose(self, options, perception):
        pass


@pytest.fixture(scope="function")
def asset1():
    obj1 = SampleAsset(id="obj1")
    yield obj1
    obj1.destroy()


@pytest.fixture(scope="function")
def asset2():
    obj2 = SampleAsset(id="obj2")
    yield obj2
    obj2.destroy()


@pytest.fixture(scope="function")
def asset_list():
    obj_list = [SampleAsset(id=f"obj{i}") for i in range(3)]
    yield obj_list
    for obj in obj_list:
        obj.destroy()


@pytest.fixture(scope="function")
def agent_list():
    agent_list = [SampleAgent(id=f"agent{i}") for i in range(3)]
    yield agent_list
    for agent in agent_list:
        agent.destroy()


@pytest.fixture(scope="function")
def agent1():
    agent1 = SampleAgent(id="agent1")
    yield agent1
    agent1.destroy()


@pytest.fixture(scope="function")
def agent2():
    agent2 = SampleAgent(id="agent2")
    yield agent2
    agent2.destroy()
