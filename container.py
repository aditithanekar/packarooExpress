from typing import Optional

class Container:
    def __init__(self,
                 position: Optional[int] = None,
                 weight: Optional[float] = None,
                 description: Optional[str] = None) -> None:
        
        self.position = position
        self.weight = weight
        self.description = description

    def get_weight(self):
        return self.weight

    def get_description(self):
        return self.description
    
    def get_position(self):
        return self.position

    def print_node_description(self):
        return f"Node(weight={self.weight}, description={self.description}, position={self.position})"

