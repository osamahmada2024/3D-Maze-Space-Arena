from abc import ABC, abstractmethod

class Scene(ABC):
    """
    Abstract base class for all game scenes.
    """
    
    @abstractmethod
    def initialize(self):
        """
        Initialize the scene assets and state.
        Returns:
            The player agent object if applicable, or None.
        """
        pass

    @abstractmethod
    def update(self, dt):
        """
        Update scene state.
        Args:
            dt: Time delta in seconds.
        """
        pass

    @abstractmethod
    def render(self):
        """
        Render the scene.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Clean up resources.
        """
        pass
