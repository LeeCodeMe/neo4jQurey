# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import neo4jOp

if __name__ == '__main__':
    data_neo4j = neo4jOp.Neo4jToJson()
    node_name="企事业单位"
    r_type="属性"
    label="super"
    node_id=0
    name_like="存款"

    print(data_neo4j.select_by_node(node_name))
    print(data_neo4j.select_by_label(label))
    print(data_neo4j.select_by_label_and_node_name_like(name_like, label="entity"))
    print(data_neo4j.select_node_by_id(node_id))
    print(data_neo4j.select_by_node_relation(node_id, r_type))
    print(data_neo4j.select_by_nodeId_or_relation(node_id, r_type, limit=None))

    # ?print(data_neo4j.select_by_relationship(r_type))
# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.

# if __name__ == '__main__':
#     print_hi('PyCharm')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
