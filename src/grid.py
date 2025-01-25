import json
from loguru import logger

class GridManager:
    def __init__(self):
        """
        Initializes the Grid Manager.
        """
        logger.info("GridManager initialized.")

    def validate_grid(self, grid):
        """
        Validates the structure and content of a grid.

        Args:
            grid (list): 2D list representing the grid.

        Returns:
            bool: True if the grid is valid, False otherwise.
        """
        try:
            if not isinstance(grid, list) or not all(isinstance(row, list) for row in grid):
                raise ValueError("Grid must be a 2D list.")

            row_length = len(grid[0])
            for row in grid:
                if len(row) != row_length:
                    raise ValueError("All rows in the grid must have the same length.")

            logger.info("Grid validated successfully.")
            return True
        except Exception as e:
            logger.error(f"Grid validation failed: {e}")
            return False

    def transform_grid(self, grid, transformation):
        """
        Applies a transformation to the grid.

        Args:
            grid (list): 2D list representing the grid.
            transformation (str): Type of transformation to apply.

        Returns:
            list: Transformed grid.
        """
        try:
            if not self.validate_grid(grid):
                raise ValueError("Invalid grid format.")

            if transformation == "invert":
                transformed = [[1 - cell if isinstance(cell, int) and 0 <= cell <= 1 else cell for cell in row] for row in grid]
            elif transformation == "rotate":
                transformed = [list(row) for row in zip(*grid[::-1])]
            elif transformation == "mirror":
                transformed = [row[::-1] for row in grid]
            else:
                raise ValueError(f"Unknown transformation: {transformation}")

            logger.info(f"Transformation '{transformation}' applied successfully.")
            return transformed

        except Exception as e:
            logger.error(f"Error applying transformation: {e}")
            return grid

    def to_json(self, grid):
        """
        Converts a grid to JSON format.

        Args:
            grid (list): 2D list representing the grid.

        Returns:
            str: JSON string representation of the grid.
        """
        try:
            grid_json = json.dumps(grid)
            logger.info("Grid converted to JSON successfully.")
            return grid_json
        except Exception as e:
            logger.error(f"Error converting grid to JSON: {e}")
            return "{}"

    def from_json(self, grid_json):
        """
        Parses a JSON string to recreate a grid.

        Args:
            grid_json (str): JSON string representation of the grid.

        Returns:
            list: 2D list representing the grid.
        """
        try:
            grid = json.loads(grid_json)
            if self.validate_grid(grid):
                logger.info("Grid parsed from JSON successfully.")
                return grid
            else:
                raise ValueError("Invalid grid format in JSON.")
        except Exception as e:
            logger.error(f"Error parsing grid from JSON: {e}")
            return []

if __name__ == "__main__":
    # Example usage
    manager = GridManager()

    grid = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    print("Original Grid:", grid)

    transformed = manager.transform_grid(grid, "invert")
    print("Inverted Grid:", transformed)

    grid_json = manager.to_json(transformed)
    print("Grid JSON:", grid_json)

    parsed_grid = manager.from_json(grid_json)
    print("Parsed Grid:", parsed_grid)
