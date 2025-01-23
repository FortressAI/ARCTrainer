from neo4j import GraphDatabase
from loguru import logger
from llm_client import LLM  # Uses LLM for reasoning analysis

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

    # ==============================
    # ONTOLOGY RULE STORAGE & RETRIEVAL
    # ==============================

    def store_ontology(self, rule_id, cnl_rule, prolog_rule, domain="general"):
        """
        Stores a CNL ontology rule and its equivalent Prolog rule in Neo4j.

        Args:
            rule_id (str): Unique identifier for the rule.
            cnl_rule (str): Human-readable ontology definition.
            prolog_rule (str): Prolog equivalent of the ontology.
            domain (str): Domain category (e.g., warfare, healthcare, legal).
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

        Args:
            domain (str): The domain to filter ontology rules.

        Returns:
            list: Retrieved ontology rules.
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

    # ==============================
    # CONSISTENCY CHECKING (CONTRADICTION DETECTION)
    # ==============================

    def validate_ontology_consistency(self):
        """
        Checks for contradictions or inconsistencies in stored ontology rules.

        Returns:
            dict: Summary of inconsistencies found.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r1:OntologyRule)-[:CONTRADICTS]->(r2:OntologyRule)
                    RETURN r1.cnl_rule AS rule1, r2.cnl_rule AS rule2
                    """
                )
                inconsistencies = [{"rule1": record["rule1"], "rule2": record["rule2"]} for record in result]

                if inconsistencies:
                    logger.warning(f"Found {len(inconsistencies)} ontology inconsistencies.")
                    return {"status": "inconsistent", "conflicts": inconsistencies}
                else:
                    logger.info("Ontology consistency check passed.")
                    return {"status": "consistent"}
        except Exception as e:
            logger.error(f"Error validating ontology consistency: {e}")
            return {"status": "error"}

    # ==============================
    # WITTGENSTEINIAN LANGUAGE GAMES (MEANING EVOLUTION)
    # ==============================

    def update_graph(self, rule, validation_results):
        """
        Updates the knowledge graph with rule validity and semantic meaning.
        Tracks how the meaning of rules evolves over time (Wittgensteinian Language Games).
        """
        meaning_variation = self.analyze_semantics(rule)
        refinement = self.analyze_feedback(rule, validation_results)

        logger.info(f"Updating rule '{rule}' with semantic shift data: {meaning_variation} and refinement: {refinement}")

        with self.driver.session() as session:
            query = """
            MERGE (r:Rule {name: $rule})
            SET r.meaning_variation = $meaning_variation, r.refinement = $refinement
            """
            session.run(query, rule=rule, meaning_variation=meaning_variation, refinement=refinement)

    def analyze_semantics(self, rule):
        """
        Uses LLM to track how rule meaning shifts based on contextual use.
        """
        query = f"How has the meaning of '{rule}' evolved in different logical contexts?"
        return LLM.ask(query)

    # ==============================
    # COUNTERFACTUAL REASONING & FEEDBACK LOOP
    # ==============================

    def generate_counterfactuals(self, rule):
        """
        Uses LLM to generate counterfactual scenarios to test rule robustness.
        """
        query = f"If {rule} were false, what consequences would follow?"
        return LLM.ask(query)

    def refine_rule_from_feedback(self, rule, feedback):
        """
        Uses feedback to adjust rule meaning dynamically.
        """
        logger.info(f"Refining rule '{rule}' based on feedback: {feedback}")
        semantic_adjustment = self.analyze_feedback(rule, feedback)

        with self.driver.session() as session:
            query = """
            MATCH (r:Rule {name: $rule})
            SET r.semantic_adjustment = $semantic_adjustment
            """
            session.run(query, rule=rule, semantic_adjustment=semantic_adjustment)

    def analyze_feedback(self, rule, feedback):
        """
        Uses LLM to determine how rule meaning should shift based on user feedback.
        """
        query = f"How should the meaning of '{rule}' adapt based on this feedback: {feedback}?"
        return LLM.ask(query)
 
    def track_near_enemy(self, rule):
        """
        Stores "near enemy" rules in Neo4j for further analysis.
        """
        logger.info(f"Tracking potential near enemy: {rule}")
        with self.driver.session() as session:
            query = """
            MERGE (r:Rule {name: $rule})
            SET r.near_enemy_flag = TRUE
            """
            session.run(query, rule=rule)
