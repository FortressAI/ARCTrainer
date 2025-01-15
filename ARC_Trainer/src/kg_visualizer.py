from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt
from loguru import logger

class KGVisualizer:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Knowledge Graph Visualizer with Neo4j integration.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("KGVisualizer initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def fetch_graph_data(self):
        """
        Fetch graph data from Neo4j.

        Returns:
            dict: Graph data containing nodes and relationships.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)-[r]->(m)
                    RETURN n.id AS source, m.id AS target, type(r) AS relationship
                    """
                )
                graph_data = [
                    {
                        "source": record["source"],
                        "target": record["target"],
                        "relationship": record["relationship"]
                    }
                    for record in result
                ]
                logger.info(f"Fetched {len(graph_data)} relationships from Neo4j.")
                return graph_data
        except Exception as e:
            logger.error(f"Error fetching graph data: {e}")
            return []

    def build_graph(self, graph_data):
        """
        Build a NetworkX graph from Neo4j graph data.

        Args:
            graph_data (list): Graph data containing nodes and relationships.

        Returns:
            nx.DiGraph: NetworkX directed graph.
        """
        try:
            graph = nx.DiGraph()

            for entry in graph_data:
                graph.add_edge(entry["source"], entry["target"], relationship=entry["relationship"])

            logger.info(f"Built graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")
            return graph
        except Exception as e:
            logger.error(f"Error building graph: {e}")
            return nx.DiGraph()

    def visualize_graph(self, graph, save_path=None):
        """
        Visualize the graph using Matplotlib.

        Args:
            graph (nx.DiGraph): The NetworkX graph to visualize.
            save_path (str): Optional file path to save the visualization.
        """
        try:
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(graph)
            nx.draw(
                graph, pos, with_labels=True, node_size=700, node_color="lightblue",
                font_size=10, font_weight="bold"
            )
            nx.draw_networkx_edge_labels(
                graph, pos, edge_labels={(u, v): d["relationship"] for u, v, d in graph.edges(data=True)}
            )

            if save_path:
                plt.savefig(save_path)
                logger.info(f"Graph visualization saved to {save_path}.")
            else:
                plt.show()
        except Exception as e:
            logger.error(f"Error visualizing graph: {e}")

    def fetch_and_visualize(self, save_path=None):
        """
        Fetch graph data from Neo4j, build a graph, and visualize it.

        Args:
            save_path (str): Optional file path to save the visualization.
        """
        graph_data = self.fetch_graph_data()
        graph = self.build_graph(graph_data)
        self.visualize_graph(graph, save_path)

if __name__ == "__main__":
    logger.info("Initializing KGVisualizer")

    visualizer = KGVisualizer(uri="bolt://localhost:7687", user="neo4j", password="password")

    # Fetch and visualize the knowledge graph
    visualizer.fetch_and_visualize(save_path="kg_visualization.png")

    visualizer.close()