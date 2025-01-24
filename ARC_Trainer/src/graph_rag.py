from neo4j import GraphDatabase
from loguru import logger

class GraphRAG:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Neo4j-backed Knowledge Graph with AI debate tracking.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("GraphRAG initialized with AI debate tracking.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def store_debate(self, rule, agent1_response, agent2_response, contradiction_found):
        """
        Stores an AI debate session in the Neo4j knowledge graph.
        """
        with self.driver.session() as session:
            session.run(
                """
                MERGE (d:Debate {rule: $rule})
                SET d.agent1 = $agent1_response, d.agent2 = $agent2_response, d.contradiction = $contradiction_found
                """, 
                rule=rule, agent1_response=agent1_response, agent2_response=agent2_response, contradiction_found=contradiction_found
            )
            logger.info(f"Stored debate for rule '{rule}'")

    def retrieve_debate_history(self, rule):
        """
        Retrieves past debate sessions for a given rule.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Debate {rule: $rule})
                RETURN d.agent1 AS agent1, d.agent2 AS agent2, d.contradiction AS contradiction
                """, 
                rule=rule
            )
            debates = [{"agent1": record["agent1"], "agent2": record["agent2"], "contradiction": record["contradiction"]}
                       for record in result]
            return debates

    def store_ontology(self, rule_id, cnl_rule, prolog_rule, domain="general"):
        """
        Stores a CNL ontology rule and its equivalent Prolog rule in Neo4j.
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (r:OntologyRule {id: $rule_id})
                    SET r.cnl_rule = $cnl_rule, r.prolog_rule = $prolog_rule, r.domain = $domain
                    """, 
                    rule_id=rule_id, cnl_rule=cnl_rule, prolog_rule=prolog_rule, domain=domain
                )
                logger.info(f"Ontology rule {rule_id} stored successfully under domain {domain}.")
        except Exception as e:
            logger.error(f"Error storing ontology rule {rule_id}: {e}")

    def retrieve_ontology(self, domain="general"):
        """
        Retrieves all ontology rules for a given domain.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r:OntologyRule) WHERE r.domain = $domain
                    RETURN r.id AS id, r.cnl_rule AS cnl_rule, r.prolog_rule AS prolog_rule
                    """, 
                    domain=domain
                )
                rules = [{"id": record["id"], "cnl_rule": record["cnl_rule"], "prolog_rule": record["prolog_rule"]}
                         for record in result]
                logger.info(f"Retrieved {len(rules)} ontology rules for domain {domain}.")
                return rules
        except Exception as e:
            logger.error(f"Error retrieving ontology rules: {e}")
            return []

if __name__ == "__main__":
    graph_rag = GraphRAG()

    # Example: Store a debate session
    rule = "All humans are mortal."
    agent1_response = "This rule holds based on observed mortality rates."
    agent2_response = "Exceptions exist in mythology and hypothetical scenarios."
    contradiction_found = "Yes"

    graph_rag.store_debate(rule, agent1_response, agent2_response, contradiction_found)

    # Example: Retrieve stored debates
    debates = graph_rag.retrieve_debate_history(rule)
    print("Retrieved Debate History:", debates)

    graph_rag.close()
