from neo4j import GraphDatabase
from loguru import logger
from src.llm_client import LLMClient
from src.PrologRuleGenerator  import PrologRuleGenerator

class LearningAgent:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Learning Agent with Neo4j for ontology storage and refinement.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.llm_client = LLMClient()
        self.prolog_generator = PrologRuleGenerator()

        logger.info("LearningAgent initialized with multi-domain ontology support.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def refine_ontology_rule(self, rule_id, domain):
        """
        Refines an ontology rule based on AI-driven learning.

        Args:
            rule_id (str): Unique identifier of the ontology rule.
            domain (str): Ontology category (e.g., legal, healthcare, AI ethics, finance).

        Returns:
            dict: Updated rule details.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r:OntologyRule {id: $rule_id}) WHERE r.domain = $domain
                    RETURN r.cnl_rule AS cnl_rule, r.prolog_rule AS prolog_rule
                    """,
                    rule_id=rule_id, domain=domain
                )

                record = result.single()
                if not record:
                    return {"error": "Ontology rule not found"}

                cnl_rule = record["cnl_rule"]
                prolog_rule = record["prolog_rule"]

                # AI-powered improvement of the ontology rule
                refined_cnl = self.llm_client.query_llm(f"Improve this ontology definition: {cnl_rule}")
                refined_prolog = self.llm_client.query_llm(f"Convert this improved definition into Prolog: {refined_cnl['response']}")

                # Store the updated rule
                session.run(
                    """
                    MATCH (r:OntologyRule {id: $rule_id})
                    SET r.cnl_rule = $refined_cnl, r.prolog_rule = $refined_prolog
                    """,
                    rule_id=rule_id, refined_cnl=refined_cnl["response"], refined_prolog=refined_prolog["response"]
                )

                logger.info(f"Ontology rule {rule_id} refined in domain '{domain}'.")

                return {
                    "rule_id": rule_id,
                    "cnl_rule": refined_cnl["response"],
                    "prolog_rule": refined_prolog["response"]
                }

        except Exception as e:
            logger.error(f"Error refining ontology rule {rule_id}: {e}")
            return {"error": "Ontology refinement failed"}

    def analyze_session(self, domain="general"):
        """
        Analyzes ontology rules for contradictions and inconsistencies in a given domain.

        Args:
            domain (str): Ontology category to analyze.

        Returns:
            dict: Summary of inconsistencies found.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r1:OntologyRule)-[:CONTRADICTS]->(r2:OntologyRule)
                    WHERE r1.domain = $domain AND r2.domain = $domain
                    RETURN r1.cnl_rule AS rule1, r2.cnl_rule AS rule2
                    """,
                    domain=domain
                )

                inconsistencies = [{"rule1": record["rule1"], "rule2": record["rule2"]} for record in result]

                if inconsistencies:
                    logger.warning(f"Found {len(inconsistencies)} inconsistencies in domain '{domain}'.")
                    return {"status": "inconsistent", "conflicts": inconsistencies}
                else:
                    logger.info(f"Ontology consistency check passed for domain '{domain}'.")
                    return {"status": "consistent"}
        except Exception as e:
            logger.error(f"Error analyzing ontology session: {e}")
            return {"status": "error"}

    def validate_and_store_rule(self, cnl_rule, domain):
        """
        Validates and stores a new ontology rule in the system.

        Args:
            cnl_rule (str): Human-readable ontology rule.
            domain (str): Ontology domain.

        Returns:
            dict: Validation and storage result.
        """
        try:
            prolog_rule = self.llm_client.query_llm(f"Convert this into Prolog: {cnl_rule}")
            if not prolog_rule.get("response"):
                return {"error": "Prolog conversion failed"}

            rule_id = f"{domain}_rule_{hash(cnl_rule) % 100000}"
            with self.driver.session() as session:
                session.run(
                    """
                    CREATE (r:OntologyRule {id: $rule_id, cnl_rule: $cnl_rule, prolog_rule: $prolog_rule, domain: $domain})
                    """,
                    rule_id=rule_id, cnl_rule=cnl_rule, prolog_rule=prolog_rule["response"], domain=domain
                )

            logger.info(f"New ontology rule stored under domain '{domain}'.")

            return {
                "rule_id": rule_id,
                "cnl_rule": cnl_rule,
                "prolog_rule": prolog_rule["response"],
                "status": "stored"
            }

        except Exception as e:
            logger.error(f"Error validating and storing rule: {e}")
            return {"error": "Ontology rule storage failed"}

if __name__ == "__main__":
    learning_agent = LearningAgent()

    # Example: Store a new legal rule
    cnl_rule = "A contract is a legally binding agreement between two or more parties."
    response = learning_agent.validate_and_store_rule(cnl_rule, domain="legal")
    print(response)

    # Example: Store a healthcare rule
    cnl_rule = "Vaccines are preventive treatments that protect against infectious diseases."
    response = learning_agent.validate_and_store_rule(cnl_rule, domain="healthcare")
    print(response)

    # Example: Refine an existing ontology rule in AI Ethics
    refinement_result = learning_agent.refine_ontology_rule(rule_id="ai_ethics_rule_002", domain="ai_ethics")
    print(refinement_result)

    # Example: Analyze contradictions in finance rules
    consistency_report = learning_agent.analyze_session(domain="finance")
    print(consistency_report)

    learning_agent.close()
