"""ADK multi-agent definitions for MedTour AI."""

__all__ = ["root_agent"]


def __getattr__(name: str):
    if name == "root_agent":
        from medtour_ai.agents.agent import root_agent

        return root_agent
    raise AttributeError(name)
