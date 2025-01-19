from neo4j import GraphDatabase
from loguru import logger
import networkx as nx
import matplotlib.pyplot as plt


class GraphRAG:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Neo4j-backed Knowledge Graph.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("GraphRAG initialized.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def store_ai_decision(self, task_id, decision_data, trust_score):
        """
        Stores an AI decision, linking it with its associated trust score.

        Args:
            task_id (str): Task ID associated with the AI decision.
            decision_data (dict): Data about the decision.
            trust_score (float): AI trust score (0-1 scale).
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (t:Task {id: $task_id})
                    SET t.decision_data = $decision_data, t.ai_trust_score = $trust_score
                    """,
                    task_id=task_id,
                    decision_data=decision_data,
                    trust_score=trust_score
                )
                logger.info(f"Stored AI decision for task {task_id} with trust score {trust_score}.")
        except Exception as e:
            logger.error(f"Error storing AI decision for task {task_id}: {e}")

    def track_decision_revision(self, task_id, previous_decision, new_decision, reason):
        """
        Logs a revision to an AI decision and updates the knowledge graph.

        Args:
            task_id (str): Task ID where the decision was revised.
            previous_decision (str): The old decision.
            new_decision (str): The revised decision.
            reason (str): The reason for the revision.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    MERGE (rev:Revision {previous: $previous_decision, new: $new_decision, reason: $reason})
                    MERGE (t)-[:HAS_REVISION]->(rev)
                    """,
                    task_id=task_id,
                    previous_decision=previous_decision,
                    new_decision=new_decision,
                    reason=reason
                )
                logger.info(f"Logged decision revision for task {task_id}: {previous_decision} → {new_decision}.")
        except Exception as e:
            logger.error(f"Error tracking decision revision for task {task_id}: {e}")

    def query_ai_decision_history(self, task_id):
        """
        Retrieves the decision history for a specific AI task.

        Args:
            task_id (str): The task ID to query.

        Returns:
            list: Decision history containing previous and revised decisions.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task {id: $task_id})-[:HAS_REVISION]->(rev:Revision)
                    RETURN rev.previous AS previous, rev.new AS new, rev.reason AS reason
                    """,
                    task_id=task_id
                )

                history = [
                    {"previous": record["previous"], "new": record["new"], "reason": record["reason"]}
                    for record in result
                ]

                logger.info(f"Retrieved decision history for task {task_id}.")
                return history
        except Exception as e:
            logger.error(f"Error retrieving AI decision history for task {task_id}: {e}")
            return []

    def update_knowledge_graph(self, task_id, decision_data):
        """
        Updates the knowledge graph with a validated AI decision.

        Args:
            task_id (str): Task ID associated with the decision.
            decision_data (dict): The updated decision data.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    SET t.decision_data = $decision_data
                    """,
                    task_id=task_id,
                    decision_data=decision_data
                )
                logger.info(f"Updated knowledge graph for task {task_id}.")
        except Exception as e:
            logger.error(f"Error updating knowledge graph for task {task_id}: {e}")

    def visualize_knowledge_graph(self, save_path=None):
        """
        Fetches decision data from Neo4j and visualizes the knowledge graph.

        Args:
            save_path (str): Optional file path to save the visualization.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (t:Task)-[r:HAS_REVISION]->(rev:Revision)
                    RETURN t.id AS task, rev.previous AS previous, rev.new AS new, rev.reason AS reason
                    """
                )

                graph_data = [
                    {"task": record["task"], "previous": record["previous"], "new": record["new"], "reason": record["reason"]}
                    for record in result
                ]
                logger.info(f"Fetched {len(graph_data)} decision revisions from Neo4j.")

                # Create graph visualization
                graph = nx.DiGraph()
                for entry in graph_data:
                    graph.add_edge(entry["previous"], entry["new"], label=entry["reason"])

                plt.figure(figsize=(12, 8))
                pos = nx.spring_layout(graph)
                nx.draw(graph, pos, with_labels=True, node_size=700, node_color="lightblue", font_size=10, font_weight="bold")
                nx.draw_networkx_edge_labels(graph, pos, edge_labels={(u, v): d["label"] for u, v, d in graph.edges(data=True)})

                if save_path:
                    plt.savefig(save_path)
                    logger.info(f"Graph visualization saved to {save_path}.")
                else:
                    plt.show()
        except Exception as e:
            logger.error(f"Error visualizing knowledge graph: {e}")

if __name__ == "__main__":
    graph_rag = GraphRAG()

    # Example: Store an AI decision
    graph_rag.store_ai_decision("task_123", {"outcome": "approve"}, trust_score=0.85)

    # Example: Log a decision revision
    graph_rag.track_decision_revision("task_123", "approve", "deny", "Counterfactual testing failed.")

    # Example: Retrieve decision history
    history = graph_rag.query_ai_decision_history("task_123")
    print("Decision History:", history)

    # Example: Update knowledge graph
    graph_rag.update_knowledge_graph("task_123", {"outcome": "deny"})

    # Example: Visualize the knowledge graph
    graph_rag.visualize_knowledge_graph(save_path="decision_graph.png")

    graph_rag.close()
