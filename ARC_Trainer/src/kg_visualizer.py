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
        logger.info("KGVisualizer initialized with multi-domain support.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def fetch_graph_data(self, domain="general"):
        """
        Fetch ontology graph data from Neo4j.

        Args:
            domain (str): The ontology domain to filter (e.g., legal, healthcare, AI ethics).

        Returns:
            list: Graph data containing nodes and relationships.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (n:OntologyRule)-[r]->(m:OntologyRule)
                    WHERE n.domain = $domain AND m.domain = $domain
                    RETURN n.cnl_rule AS source, m.cnl_rule AS target, type(r) AS relationship
                    """,
                    domain=domain
                )
                graph_data = [
                    {
                        "source": record["source"],
                        "target": record["target"],
                        "relationship": record["relationship"]
                    }
                    for record in result
                ]
                logger.info(f"Fetched {len(graph_data)} ontology relationships for domain '{domain}'.")
                return graph_data
        except Exception as e:
            logger.error(f"Error fetching graph data: {e}")
            return []

    def build_graph(self, graph_data):
        """
        Build a NetworkX graph from Neo4j ontology data.

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
        Visualize the knowledge graph using Matplotlib.

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
                logger.info(f"Ontology visualization saved to {save_path}.")
            else:
                plt.show()
        except Exception as e:
            logger.error(f"Error visualizing ontology graph: {e}")

    def fetch_and_visualize(self, domain="general", save_path=None):
        """
        Fetch ontology data from Neo4j, build a graph, and visualize it.

        Args:
            domain (str): The ontology domain to filter (e.g., legal, healthcare, AI ethics).
            save_path (str): Optional file path to save the visualization.
        """
        graph_data = self.fetch_graph_data(domain=domain)
        graph = self.build_graph(graph_data)
        self.visualize_graph(graph, save_path)

    def fetch_cross_domain_graph_data(self, domain1, domain2):
        """
        Fetch relationships between two ontology domains.

        Args:
            domain1 (str): First ontology domain.
            domain2 (str): Second ontology domain.

        Returns:
            list: Cross-domain relationships.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (n:OntologyRule)-[r]->(m:OntologyRule)
                    WHERE n.domain = $domain1 AND m.domain = $domain2
                    RETURN n.cnl_rule AS source, m.cnl_rule AS target, type(r) AS relationship
                    """,
                    domain1=domain1, domain2=domain2
                )
                graph_data = [
                    {
                        "source": record["source"],
                        "target": record["target"],
                        "relationship": record["relationship"]
                    }
                    for record in result
                ]
                logger.info(f"Fetched {len(graph_data)} cross-domain relationships between '{domain1}' and '{domain2}'.")
                return graph_data
        except Exception as e:
            logger.error(f"Error fetching cross-domain graph data: {e}")
            return []

    def visualize_cross_domain_ontology(self, domain1, domain2, save_path=None):
        """
        Visualize ontology relationships between two domains.

        Args:
            domain1 (str): First ontology domain.
            domain2 (str): Second ontology domain.
            save_path (str): Optional file path to save the visualization.
        """
        graph_data = self.fetch_cross_domain_graph_data(domain1, domain2)
        graph = self.build_graph(graph_data)
        self.visualize_graph(graph, save_path)

if __name__ == "__main__":
    logger.info("Initializing KGVisualizer")

    visualizer = KGVisualizer(uri="bolt://localhost:7687", user="neo4j", password="password")

    # Fetch and visualize the legal ontology
    visualizer.fetch_and_visualize(domain="legal", save_path="legal_ontology.png")

    # Fetch and visualize the healthcare ontology
    visualizer.fetch_and_visualize(domain="healthcare", save_path="healthcare_ontology.png")

    # Cross-domain visualization: AI Ethics ↔ Legal
    visualizer.visualize_cross_domain_ontology(domain1="ai_ethics", domain2="legal", save_path="ai_legal_ontology.png")

    visualizer.close()
