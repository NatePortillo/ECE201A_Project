import json
from neo4j import GraphDatabase
from glayout.flow.pdk.sky130_mapped.grules import grulesobj

class Sky130KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_layer(self, layer_name):
        with self.driver.session() as session:
            session.run("MERGE (:Layer {name: $name})", name=layer_name)

    def add_constraint(self, layer1, layer2, constraint):
        with self.driver.session() as session:
            session.run("""
                MATCH (l1:Layer {name: $layer1}), (l2:Layer {name: $layer2})
                MERGE (l1)-[r:CONSTRAINS]->(l2)
                SET r.rules_json = $rules_json
            """, layer1=layer1, layer2=layer2, rules_json=constraint["rules_json"])

    def query_neo4j(self):
        with self.driver.session() as session:
            query = """
            MATCH (l1:Layer {name: $layer1})-[r:CONSTRAINS]->(l2:Layer {name: $layer2}) 
            RETURN r.rules_json AS rules_json
            """
            
            result = session.run(query, layer1="dnwell", layer2="nwell") # Execute the query
            
            for record in result:
                print(f"Rules JSON: {record['rules_json']}")

kg = Sky130KnowledgeGraph("neo4j+s://37447c78.databases.neo4j.io", "neo4j", "cUoYzRehyPFlauBOhekoJolfVDVUOGrTuAwLIZywZy4")

for layer1, interactions in grulesobj.items(): # Parse grulesobj and populate the knowledge graph with PDK
    kg.add_layer(layer1)
    for layer2, rules in interactions.items():
        kg.add_layer(layer2)
        if rules:  # Add constraints only if there are rules between constraints
            print(rules)
            rules_json = json.dumps(rules)
            kg.add_constraint(layer1, layer2, {"rules_json": rules_json})

kg.query_neo4j()
kg.close()
