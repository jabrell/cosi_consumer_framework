import pytest
from cosi_consumer_framework import Asset, Agent, ChoiceSet


class SampleAsset(Asset):
    pass


class SampleAgent(Agent):
    def perceive(self, environment):
        pass

    def trigger_choice(self, perception):
        pass

    def choose(self, options, perception):
        pass


class SampleChoiceSet(ChoiceSet):
    def trigger(self, perception):
        pass

    def evaluate(self):
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
