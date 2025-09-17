# COSI Consumer Framework

An illustrative implementation of the SWEET COSI Framework in Python for agent-based modeling and simulation.

## Overview

The COSI Consumer Framework is a flexible Python library designed for building agent-based models (ABM) that simulate consumer behavior and decision-making processes. The framework provides a structured approach to modeling environments where agents (consumers) interact with assets and make choices based on their perceptions of the environment.

### Key Features

- **Agent-Based Modeling**: Create autonomous agents that perceive, decide, and act within an environment
- **Flexible Architecture**: Extensible base classes for agents, assets, and environments
- **Choice Modeling**: Built-in support for choice sets and decision-making processes
- **Perception System**: Model how agents perceive and potentially distort environmental information
- **Registration System**: Automatic object tracking and dependency management
- **Reporting**: Built-in data collection and reporting capabilities
- **Type Safety**: Built with modern Python type hints and Pydantic validation

### Core Components

1. **Environment**: The container that manages all agents and assets in the simulation
2. **Agent**: Abstract base class for entities that can perceive and act
3. **Asset**: Base class for objects that exist in the environment (buildings, resources, etc.)
4. **AgentPerception**: Handles how agents perceive environmental information
5. **ChoiceSet**: Manages the set of options available to agents and their evaluation
6. **Registrable**: Base class providing unique identification and lifecycle management

## Quick Start

### Installation

```bash
# Install from source
git clone <repository-url>
cd cosi_consumer_framework
pip install -e .
```

## Requirements

- Python >= 3.13
- NumPy >= 2.3.3
- Pandas >= 2.3.2
- SQLModel >= 0.0.24

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy cosi_consumer_framework/
```

### Coverage

```bash
coverage run -m pytest
coverage report
```

## License

This project is licensed under the terms found in the LICENSE file.