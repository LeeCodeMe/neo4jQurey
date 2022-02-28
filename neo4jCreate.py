# coding:utf-8
import os
import pandas as pd
import re
from py2neo import Graph, Node, Relationship

# https://www.freesion.com/article/2392500608/
'''
MATCH (n)
OPTIONAL MATCH (n)-[r]-()
DELETE n,r
#删库demo
'''


def creat_node(file, graph):
    if not os.path.exists(file):
        print('{} 文件不存在'.format(file))
    df = pd.read_csv(file)
    df = df.fillna(value=str('不存在'))
    # for column in list(df.columns)[:]:
    #     a = df[column]
    #     for i in zip(a):
    #         #print(i)
    #         reg = "[^0-9A-Za-z\u4e00-\u9fa5]"
    #         i = re.sub(reg, '', str(i))
    #         #print(i)
    #         node = Node(column,name=i)
    #         if not graph.find_one(label=column, property_key='name', property_value=i):
    #             graph.create(node)
    #             print('创建了新 结点 ： {}'.format(node))
    name, shortname = df.name, df.shortname
    province, city = df.province, df.city
    manager, chairman = df.manager, df.chairman

    for name, shortname, province, city, manager, chairman in zip(df.name, df.shortname,
                                                                  df.province, df.city,
                                                                  df.manager, df.chairman):
        name_node = Node('名字',
                         name=name,
                         shortname=shortname,
                         )
        province_node = Node('所在地',
                             name=province,
                             city=city,
                             )
        manager_node = Node('总经理', name=manager)
        chairman_node = Node('法人代表', name=chairman)

        if not graph.find_one(label='名字', property_key='name', property_value=name):
            graph.create(name_node)
        if not graph.find_one(label='所在地', property_key='name', property_value=province):
            graph.create(province_node)
        if not graph.find_one(label='总经理', property_key='name', property_value=manager):
            graph.create(manager_node)
        if not graph.find_one(label='法人代表', property_key='name', property_value=chairman):
            graph.create(chairman_node)
        print('创建了新的结点：{}{}{}{}'.format(name_node, province_node, manager_node, chairman_node))
        name_node = graph.find_one(label='名字', property_key='name', property_value=name)
        province_node = graph.find_one(label='所在地', property_key='name', property_value=province)
        manager_node = graph.find_one(label='总经理', property_key='name', property_value=manager)
        chairman_node = graph.find_one(label='法人代表', property_key='name', property_value=chairman)

        relationship1 = Relationship(name_node, '地址', province_node)
        graph.create(relationship1)
        print('新建关系： {}'.format(relationship1))

        relationship2 = Relationship(name_node, '经理人', manager_node)
        graph.create(relationship2)
        print('新建关系： {}'.format(relationship2))

        relationship3 = Relationship(name_node, '法人', chairman_node)
        graph.create(relationship3)
        print('新建关系： {}'.format(relationship3))


if __name__ == '__main__':
    # graph = Graph(password="")
    graph = Graph("http://localhost:7474", auth=("neo4j", "ConnectA"))
    chess_file = 'jijin.csv'
    creat_node(chess_file, graph)