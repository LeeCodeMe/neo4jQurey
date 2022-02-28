# -*- coding: utf-8 -*-

from py2neo import Graph,Node, Relationship,NodeMatcher,RelationshipMatcher
import json
import re


class Neo4jToJson(object):
    """知识图谱数据接口"""

    def __init__(self):
        """初始化数据"""
        # 与neo4j服务器建立连接
        self.graph = Graph("http://10.68.74.239:60003", auth=("neo4j", "bigdata316316"))

        self.nodematcher=NodeMatcher(self.graph)
        self.links = []
        self.nodes = []



    def select_by_node(self,node_name):
        """通过单个节点查询"""

        # 取出所有节点数据
        nodes_data_all = self.graph.run("MATCH (n) RETURN n").data()
        # node名存储
        nodes_list = []
        for node in nodes_data_all:
            nodes_list.append(node['n']['name'])
        # 根据搜索变量，判断搜索的关键字是否在nodes_list中存在，如果存在返回相应数据，否则返回全部数据
        if node_name in nodes_list:
            # 获取知识图谱中相关节点数据
            nodes_data = self.graph.run("MATCH (n)--(b) where n.name='" + node_name + "' return n,b").data()
            links_data = self.graph.run("MATCH (n)-[r]-(b) where n.name='" + node_name + "' return r").data()
            self.get_nodes(nodes_data)
            print("\n")
        else:
            # 获取知识图谱中所有节点数据
            links_data = self.graph.run("MATCH ()-[r]->() RETURN r").data()
            nodes_data = self.graph.run("MATCH (n) RETURN n").data()
            self.get_nodes(nodes_data)
            print("\n")
        print("The links relationship as follows:\n")
        self.get_links(links_data)

        # 数据格式转换
        neo4j_data = {'links': self.links, 'nodes': self.nodes}
        neo4j_data_json = json.dumps(neo4j_data, ensure_ascii=False).replace(u'\xa0', u'')
        return neo4j_data_json

    def get_links(self, links_data):
        """知识图谱关系数据获取"""
        links_data_str = str(links_data)
        links = []
        i = 1
        dict = {}
        # 正则匹配
        links_str = re.sub("[\!\%\[\]\,\。\{\}\-\:\'\(\)\>]", " ", links_data_str).split(' ')
        for link in links_str:
            if len(link) > 1:
                if i == 1:
                    dict['relationship'] = link
                elif i == 3:
                    dict['label_A'] = link
                elif i == 5:
                    dict['name_A'] = link
                elif i==7:
                    dict['label_B']=link
                elif i==9:
                    dict['name_B']=link
                    self.links.append(dict)
                    dict = {}
                    i = 0
                i += 1
        return self.links


    def get_nodes(self, nodes_data):
        """获取知识图谱中所选择的节点数据"""
        nodes_data_str=str(nodes_data)
        nodes=[]
        i=1
        dict_node = {}
        nodes_str = re.sub("[\!\%\[\]\,\。\{\}\-\:\'\(\)\>]", " ", nodes_data_str).split(' ')
        for node in nodes_str:
            if len(node)>1:
                if i==2:
                    dict_node['Label']=node
                elif i==4:
                    dict_node['name']=node
                    self.nodes.append(dict_node)
                    dict_node={}
                    i=0
                i+=1
        return self.nodes

    def get_match_nodes(self,nodes_data):
        """获取匹配的节点数据"""
        nodes_data_str = str(nodes_data)
        nodes = []
        i = 1
        dict_node = {}
        nodes_str = re.sub("[\!\%\[\]\,\。\{\}\-\:\'\(\)\>]", " ", nodes_data_str).split(' ')
        for node in nodes_str:
            if len(node) > 1:
                if i == 1:
                    dict_node['Label'] = node
                elif i == 3:
                    dict_node['name'] = node
                    self.nodes.append(dict_node)
                    dict_node = {}
                    i = 0
                i += 1
        return self.nodes

    def select_by_relationship(self, r_type):
        """通过关系查询"""

        # 取出所有节点数据
        links_data_all = self.graph.run("match (n) -[r]-(b) return r").data()
        # node名存储
        links_list = []
        for link in links_data_all:
            links_list.append(link['n']['name'])
        # 根据搜索变量，判断搜索的关键字是否在nodes_list中存在，如果存在返回相应数据，否则返回全部数据
        if r_type in links_list:
            # 获取知识图谱中相关节点数据
            links_data = self.graph.run("MATCH p=()-[r:"+"\`"+r_type+"\`"+"]->() RETURN p").data()
            # links_data = self.graph.run("MATCH (n)-[r]-(b) where n.name='" + node_name + "' return r").data()
            print("The links relationship as follows:\n")
            self.get_links(links_data)
            print("\n")
        else:
            # 获取知识图谱中所有节点数据
            links_data = self.graph.run("MATCH ()-[r]->() RETURN r").data()
            # nodes_data = self.graph.run("MATCH (n) RETURN n").data()
            print("The links relationship as follows:\n")
            self.get_links(links_data)
            print("\n")


        # 数据格式转换
        neo4j_data = {'links': self.links}
        neo4j_data_json = json.dumps(neo4j_data, ensure_ascii=False).replace(u'\xa0', u'')
        return neo4j_data_json



    def select_by_label(self,label):
        match=self.nodematcher.match(label)
        print("The nodes in the class of %s include:\n",label)
        return self.get_match_nodes(list(match))

    def select_by_nodeId_or_relation(self,node_id,r_type=None,limit=None):
        """通过节点ID和关系类型（非必须）查询节点信息"""
        nodes=self.select_node_by_id(node_id)
        match=self.graph.match({nodes},r_type,limit)
        return list(match)

    def select_by_label_and_node_name_like(self,name_like,label="super"):
        """通过节点标签(默认为“super”)和名称前缀的模糊查询查询节点"""
        match = self.nodematcher.match(label).where("_.name=~ '"+name_like+".*'")
        return list(match)
    def select_node_by_id(self,node_id):
        """通过node ID查找node"""
        return self.nodematcher.get(node_id)

    def select_by_node_relation(self,node_id,r_type):
        """通过node ID和关系类型查找"""
        node=self.select_node_by_id(node_id)
        relationshipmatcher = RelationshipMatcher(self.graph)
        result=relationshipmatcher.match((node,),r_type)
        return list(result)



# if __name__ == '__main__':
#     data_neo4j = neo4jOp.Neo4jToJson()
#     print(data_neo4j.select_by_node('单位'))
#
# The links relationship as follows:
#
# {"links": [{"relationship": "包含", "label_A": "super", "name_A": "客户", "label_B": "entity", "name_B": "单位"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "纳税人信用评级"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "营业执照号"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "贡献度"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "客户评级"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "高风险客户标签"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "战略客户标签"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "网银客户标签"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "结算客户标签"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "网银签约标签"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "供应链核心客户标签"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "金融客户标签"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "APP浏览习惯"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "网页浏览习惯"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "访问地点"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "访问时间"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "高管"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "一般雇员"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "业务经办"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "财务负债"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "法定代表"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "互持股分"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "家族企业"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "集团关系"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业对外投资"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "管理人信息"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "出资人信息"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "股东信息"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业类型"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "注册日期"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业证照信息"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业增值税"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "法人姓名"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业姓名"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "证件类型"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "统一社会信用代码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "经营许可证"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "组织机构代码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "证件号码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "经营范围"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "行业分类"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "行业分类"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "经济类型"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业规模"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "注册资本"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "注册地址"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "办公室地址"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "控股股东名称"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "注册资本"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "实收资本"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "政府机关"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企事业单位"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "社会团体"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "民间组织"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "营业收入"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "利润总额"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "资产状况"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "负债状况"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "银行卡磁道"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "卡片验证码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "CVN"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "CVN2"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "卡片有效期"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "银行卡密码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "支付密码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "支付账号"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "网络支付业务"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "登录用户"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "证券账户"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "保险账户"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "登陆密码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "交易密码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "查询密码"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业借贷信息"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业还款信息"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企业欠款信息"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "被执行人信息"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "失信人"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "开庭公告"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "立案公告"}, {"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "纳税情况"}, {"relationship": "同义", "label_A": "entity", "name_A": "单位", "label_B": "entity", "name_B": "对公"}, {"relationship": "关联", "label_A": "entity", "name_A": "个人", "label_B": "entity", "name_B": "单位"}, {"relationship": "关联", "label_A": "entity", "name_A": "贷款", "label_B": "entity", "name_B": "单位"}, {"relationship": "关联", "label_A": "entity", "name_A": "单位", "label_B": "entity", "name_B": "员工信息"}, {"relationship": "关联", "label_A": "entity", "name_A": "单位", "label_B": "entity", "name_B": "个人"}, {"relationship": "关联", "label_A": "entity", "name_A": "单位", "label_B": "entity", "name_B": "应用研发"}, {"relationship": "包含", "label_A": "label_2", "name_A": "单位", "label_B": "label_3", "name_B": "单位标签信息"}, {"relationship": "包含", "label_A": "label_2", "name_A": "单位", "label_B": "label_3", "name_B": "单位行为信息"}, {"relationship": "包含", "label_A": "label_2", "name_A": "单位", "label_B": "label_3", "name_B": "单位关系信息"}, {"relationship": "包含", "label_A": "label_2", "name_A": "单位", "label_B": "label_3", "name_B": "单位资讯信息"}, {"relationship": "包含", "label_A": "label_2", "name_A": "单位", "label_B": "label_3", "name_B": "单位身份鉴别信息"}, {"relationship": "包含", "label_A": "label_2", "name_A": "单位", "label_B": "label_3", "name_B": "单位基本信息"}, {"relationship": "包含", "label_A": "label_1", "name_A": "客户", "label_B": "label_2", "name_B": "单位"}], "nodes": [{"Label": "entity", "name": "单位"}, {"Label": "super", "name": "客户"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "纳税人信用评级"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "营业执照号"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "贡献度"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "客户评级"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "高风险客户标签"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "战略客户标签"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "网银客户标签"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "结算客户标签"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "网银签约标签"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "供应链核心客户标签"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "金融客户标签"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "APP浏览习惯"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "网页浏览习惯"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "访问地点"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "访问时间"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "高管"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "一般雇员"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "业务经办"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "财务负债"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "法定代表"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "互持股分"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "家族企业"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "集团关系"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业对外投资"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "管理人信息"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "出资人信息"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "股东信息"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业类型"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "注册日期"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业证照信息"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业增值税"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "法人姓名"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业姓名"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "证件类型"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "统一社会信用代码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "经营许可证"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "组织机构代码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "证件号码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "经营范围"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "行业分类"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "行业分类"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "经济类型"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业规模"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "注册资本"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "注册地址"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "办公室地址"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "控股股东名称"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "注册资本"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "实收资本"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "政府机关"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企事业单位"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "社会团体"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "民间组织"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "营业收入"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "利润总额"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "资产状况"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "负债状况"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "银行卡磁道"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "卡片验证码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "CVN"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "CVN2"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "卡片有效期"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "银行卡密码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "支付密码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "支付账号"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "网络支付业务"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "登录用户"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "证券账户"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "保险账户"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "登陆密码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "交易密码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "查询密码"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业借贷信息"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业还款信息"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "企业欠款信息"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "被执行人信息"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "失信人"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "开庭公告"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "立案公告"}, {"Label": "entity", "name": "单位"}, {"Label": "attr", "name": "纳税情况"}, {"Label": "entity", "name": "单位"}, {"Label": "entity", "name": "对公"}, {"Label": "entity", "name": "单位"}, {"Label": "entity", "name": "个人"}, {"Label": "entity", "name": "单位"}, {"Label": "entity", "name": "贷款"}, {"Label": "entity", "name": "单位"}, {"Label": "entity", "name": "员工信息"}, {"Label": "entity", "name": "单位"}, {"Label": "entity", "name": "个人"}, {"Label": "entity", "name": "单位"}, {"Label": "entity", "name": "应用研发"}, {"Label": "label_2", "name": "单位"}, {"Label": "label_3", "name": "单位标签信息"}, {"Label": "label_2", "name": "单位"}, {"Label": "label_3", "name": "单位行为信息"}, {"Label": "label_2", "name": "单位"}, {"Label": "label_3", "name": "单位关系信息"}, {"Label": "label_2", "name": "单位"}, {"Label": "label_3", "name": "单位资讯信息"}, {"Label": "label_2", "name": "单位"}, {"Label": "label_3", "name": "单位身份鉴别信息"}, {"Label": "label_2", "name": "单位"}, {"Label": "label_3", "name": "单位基本信息"}, {"Label": "label_2", "name": "单位"}, {"Label": "label_1", "name": "客户"}]}
#
#     print(data_neo4j.select_by_node('企事业单位'))
# The links relationship as follows:
#
# {"links": [{"relationship": "属性", "label_A": "entity", "name_A": "单位", "label_B": "attr", "name_B": "企事业单位"}], "nodes": [{"Label": "attr", "name": "企事业单位"}, {"Label": "entity", "name": "单位"}]}
