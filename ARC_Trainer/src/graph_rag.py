from neo4j import GraphDatabase
from loguru import logger

class GraphRAG:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initializes the Neo4j-backed Knowledge Graph for multi-domain ontologies.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("GraphRAG initialized with multi-domain ontology support.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def store_ontology(self, rule_id, cnl_rule, prolog_rule, domain="general"):
        """
        Stores an ontology rule in Neo4j under a specified domain.

        Args:
            rule_id (str): Unique identifier for the rule.
            cnl_rule (str): Human-readable ontology definition.
            prolog_rule (str): Prolog equivalent of the ontology.
            domain (str): Domain category (e.g., legal, healthcare, education, AI ethics, warfare).
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
                logger.info(f"Ontology rule {rule_id} stored successfully under domain '{domain}'.")
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
                logger.info(f"Retrieved {len(rules)} ontology rules for domain '{domain}'.")
                return rules
        except Exception as e:
            logger.error(f"Error retrieving ontology rules: {e}")
            return []

    def validate_ontology_consistency(self, domain="general"):
        """
        Checks for contradictions or inconsistencies in stored ontology rules for a given domain.

        Args:
            domain (str): The domain to check for inconsistencies.

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
            logger.error(f"Error validating ontology consistency: {e}")
            return {"status": "error"}

    def store_domain_ontology(self, rule_id, cnl_rule, prolog_rule, domain):
        """
        Stores an ontology rule in the specified domain.

        Args:
            rule_id (str): Unique identifier for the rule.
            cnl_rule (str): Human-readable ontology definition.
            prolog_rule (str): Prolog equivalent of the ontology.
            domain (str): Domain of the ontology.
        """
        self.store_ontology(rule_id, cnl_rule, prolog_rule, domain=domain)

    def retrieve_domain_ontology(self, domain):
        """
        Retrieves ontology rules for a specified domain.

        Args:
            domain (str): The domain to fetch ontology rules.

        Returns:
            list: Ontology rules.
        """
        return self.retrieve_ontology(domain=domain)

    def cross_domain_analysis(self, domain1, domain2):
        """
        Analyzes connections between two different ontology domains.

        Args:
            domain1 (str): First ontology domain.
            domain2 (str): Second ontology domain.

        Returns:
            list: Cross-domain relationships found.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (r1:OntologyRule)-[r]->(r2:OntologyRule)
                    WHERE r1.domain = $domain1 AND r2.domain = $domain2
                    RETURN r1.cnl_rule AS rule1, r2.cnl_rule AS rule2, type(r) AS relationship
                    """,
                    domain1=domain1, domain2=domain2
                )
                connections = [{"rule1": record["rule1"], "rule2": record["rule2"], "relationship": record["relationship"]}
                               for record in result]

                logger.info(f"Found {len(connections)} cross-domain relationships between '{domain1}' and '{domain2}'.")
                return connections
        except Exception as e:
            logger.error(f"Error in cross-domain analysis: {e}")
            return []

if __name__ == "__main__":
    graph_rag = GraphRAG()

    # Example: Store a legal ontology rule
    rule_id = "legal_rule_001"
    cnl_rule = "A contract is a legally binding agreement between two or more parties."
    prolog_rule = "contract(X, Y) :- legally_binding_agreement(X, Y)."

    graph_rag.store_domain_ontology(rule_id, cnl_rule, prolog_rule, domain="legal")

    # Example: Store a healthcare ontology rule
    rule_id = "healthcare_rule_001"
    cnl_rule = "A vaccine is a preventive treatment that helps protect against infectious diseases."
    prolog_rule = "vaccine(X) :- preventive_treatment(X), protects_against(infectious_diseases)."

    graph_rag.store_domain_ontology(rule_id, cnl_rule, prolog_rule, domain="healthcare")

    # Example: Retrieve stored legal ontology rules
    legal_rules = graph_rag.retrieve_domain_ontology(domain="legal")
    print("Retrieved Legal Rules:", legal_rules)

    # Example: Validate ontology consistency for healthcare
    consistency_report = graph_rag.validate_ontology_consistency(domain="healthcare")
    print("Ontology Consistency Report (Healthcare):", consistency_report)

    # Example: Cross-domain analysis between legal and healthcare
    connections = graph_rag.cross_domain_analysis(domain1="legal", domain2="healthcare")
    print("Cross-Domain Relationships (Legal ↔ Healthcare):", connections)

    graph_rag.close()
