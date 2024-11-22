import json
from neo4j import GraphDatabase

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


# Testing
if __name__ == "__main__":
    uri = "neo4j+s://37447c78.databases.neo4j.io"
    user = "neo4j"
    password = "cUoYzRehyPFlauBOhekoJolfVDVUOGrTuAwLIZywZy4"

    json_file = r"C:\Users\natha\Desktop\ECE201A_Project\scripts\component_graph.json"  # Replace with your JSON file path
    with open(json_file, "r") as file:
        components_data = json.load(file)


    kg = ComponentKnowledgeGraph(uri, user, password)

    kg.populate_graph(components_data) # Populate the graph with components and dependencies

    # Testing
    component_to_query = "DFlipFlop"
    dependencies = kg.query_dependencies(component_to_query)
    print(f"{component_to_query} depends on: {dependencies}")
    kg.close()