import json
from neo4j import GraphDatabase
from difflib import get_close_matches

class ComponentKnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_component(self, component_name):
        """
        Add a component node to the Neo4j database.
        """
        with self.driver.session() as session:
            session.run("MERGE (:Component {name: $name})", name=component_name)

    def add_dependency(self, component, dependency):
        """
        Add a dependency relationship between two components.
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Component {name: $component}), (d:Component {name: $dependency})
                MERGE (c)-[:DEPENDS_ON]->(d)
            """, component=component, dependency=dependency)

    def populate_graph(self, components_data):
        """
        Populate the Neo4j graph with components and their dependencies.
        """
        for component, dependencies in components_data.items():
            self.add_component(component) # Add the component as a node

            for dependency in dependencies: # Add its dependencies as nodes and relationships
                self.add_component(dependency)
                self.add_dependency(component, dependency)

    def query_dependencies(self, component_name):
        """
        Query and print all dependencies for a given component.
        """
        with self.driver.session() as session:
            query = """
            MATCH (c:Component {name: $component_name})-[:DEPENDS_ON]->(d:Component)
            RETURN d.name AS dependency
            """
            result = session.run(query, component_name=component_name)
            dependencies = [record["dependency"] for record in result]
            return dependencies

    def is_valid_import(self, component_name):
        """
        Check if a component is valid based on the knowledge graph.
        """
        if not self.driver:
            raise RuntimeError("Knowledge graph driver is not initialized.")
        
        with self.driver.session() as session:
            query = """
            MATCH (c:Component {name: $component_name})
            RETURN c.name AS name
            """
            result = session.run(query, component_name=component_name)
            return result.single() is not None

    def get_all_components(self):
        """
        Retrieve all valid component names from the knowledge graph.

        Returns:
            list: A list of all valid component names.
        """
        with self.driver.session() as session:
            query = "MATCH (c:Component) RETURN c.name AS name"
            result = session.run(query)
            return [record["name"] for record in result]

    def get_all_components_with_dependencies(self):
        """
        Retrieve all components and their dependencies from the knowledge graph.

        Returns:
            dict: A dictionary where keys are components and values are lists of dependencies.
        """
        with self.driver.session() as session:
            query = """
            MATCH (c:Component)
            OPTIONAL MATCH (c)-[:DEPENDS_ON]->(dependency:Component)
            RETURN c.name AS component, collect(dependency.name) AS dependencies
            """
            result = session.run(query)

            # Organize the results into a dictionary
            components_with_dependencies = {}
            for record in result:
                component = record["component"]
                dependencies = record["dependencies"]
                components_with_dependencies[component] = [dep for dep in dependencies if dep is not None]

        return components_with_dependencies

    def suggest_string_based_alternatives(self, component_name, all_components, similarity_threshold=0.6):
        """
        Suggest alternatives based on string similarity.

        Args:
            component_name (str): The invalid component name.
            all_components (list): A list of all valid components.
            similarity_threshold (float): Minimum similarity score.

        Returns:
            list: Suggested alternatives.
        """
        return get_close_matches(component_name, all_components, n=1)