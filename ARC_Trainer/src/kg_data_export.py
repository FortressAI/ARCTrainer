from flask import Flask, jsonify, request, send_file
from neo4j import GraphDatabase
import pandas as pd
import json
import networkx as nx
import os
from loguru import logger

app = Flask(__name__)

class KGDataExport:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="mysecurepassword", export_dir="exports/"):
        """
        Initializes the Knowledge Graph Data Export module.

        Args:
            uri (str): URI for connecting to Neo4j.
            user (str): Username for Neo4j authentication.
            password (str): Password for Neo4j authentication.
            export_dir (str): Directory where exported files are saved.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)

        logger.info("KGDataExport initialized with multi-domain ontology support.")

    def close(self):
        """Closes the connection to the Neo4j database."""
        self.driver.close()

    def fetch_ontology_data(self, domain="general"):
        """
        Fetch ontology data for a specific domain.

        Args:
            domain (str): The ontology domain to filter.

        Returns:
            list: Nodes and relationships in the ontology.
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (n:OntologyRule)-[r]->(m:OntologyRule)
                    WHERE n.domain = $domain AND m.domain = $domain
                    RETURN n.id AS source, m.id AS target, type(r) AS relationship
                    """,
                    domain=domain
                )
                data = [{"source": record["source"], "target": record["target"], "relationship": record["relationship"]}
                        for record in result]

                logger.info(f"Fetched {len(data)} ontology relationships for domain '{domain}'.")
                return data
        except Exception as e:
            logger.error(f"Error fetching ontology data: {e}")
            return []

    def export_to_csv(self, domain="general"):
        """
        Exports ontology data to CSV.

        Args:
            domain (str): Ontology domain to export.

        Returns:
            str: File path of the exported CSV.
        """
        data = self.fetch_ontology_data(domain)
        if not data:
            return None

        file_path = os.path.join(self.export_dir, f"{domain}_ontology.csv")
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

        logger.info(f"Ontology exported to CSV: {file_path}")
        return file_path

    def export_to_json(self, domain="general"):
        """
        Exports ontology data to JSON.

        Args:
            domain (str): Ontology domain to export.

        Returns:
            str: File path of the exported JSON.
        """
        data = self.fetch_ontology_data(domain)
        if not data:
            return None

        file_path = os.path.join(self.export_dir, f"{domain}_ontology.json")
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        logger.info(f"Ontology exported to JSON: {file_path}")
        return file_path

    def export_to_graphml(self, domain="general"):
        """
        Exports ontology data to GraphML for visualization.

        Args:
            domain (str): Ontology domain to export.

        Returns:
            str: File path of the exported GraphML.
        """
        data = self.fetch_ontology_data(domain)
        if not data:
            return None

        graph = nx.DiGraph()
        for entry in data:
            graph.add_edge(entry["source"], entry["target"], relationship=entry["relationship"])

        file_path = os.path.join(self.export_dir, f"{domain}_ontology.graphml")
        nx.write_graphml(graph, file_path)

        logger.info(f"Ontology exported to GraphML: {file_path}")
        return file_path

    def export_to_neo4j_dump(self, domain="general"):
        """
        Exports ontology data to a Neo4j Cypher dump.

        Args:
            domain (str): Ontology domain to export.

        Returns:
            str: File path of the exported Neo4j dump.
        """
        data = self.fetch_ontology_data(domain)
        if not data:
            return None

        file_path = os.path.join(self.export_dir, f"{domain}_ontology.cypher")

        with open(file_path, "w") as f:
            for entry in data:
                f.write(f"CREATE (:OntologyRule {{id: '{entry['source']}'}});\n")
                f.write(f"CREATE (:OntologyRule {{id: '{entry['target']}'}});\n")
                f.write(f"MATCH (a:OntologyRule {{id: '{entry['source']}'}}), (b:OntologyRule {{id: '{entry['target']}'}}) "
                        f"CREATE (a)-[:{entry['relationship']}]->(b);\n")

        logger.info(f"Ontology exported to Neo4j dump: {file_path}")
        return file_path

@app.route("/export", methods=["GET"])
def export_data():
    """
    API endpoint to export ontology data in various formats.

    Query Parameters:
        domain (str): Ontology domain to export.
        format (str): Export format (csv, json, graphml, neo4j).
    
    Returns:
        JSON response with file path or error message.
    """
    domain = request.args.get("domain", "general")
    export_format = request.args.get("format", "csv").lower()

    manager = KGDataExport()
    file_path = None

    if export_format == "csv":
        file_path = manager.export_to_csv(domain)
    elif export_format == "json":
        file_path = manager.export_to_json(domain)
    elif export_format == "graphml":
        file_path = manager.export_to_graphml(domain)
    elif export_format == "neo4j":
        file_path = manager.export_to_neo4j_dump(domain)

    manager.close()

    if file_path:
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "Export failed or no data available"}), 400

if __name__ == "__main__":
    logger.info("Starting KG Data Export API")
    app.run(host="0.0.0.0", port=5005)
