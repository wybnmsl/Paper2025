import networkx as nx
import random
import json
from tqdm import tqdm

# 读取txt文件并创建图
def read_graph_from_file(file_path):
    G = nx.Graph()
    
    with open(file_path, 'r') as file:
        for line in file:
            nodes = line.strip().split()
            if len(nodes) == 2:
                G.add_edge(int(nodes[0]), int(nodes[1]))
    
    return G

# 1. 检查图中是否有环
def has_cycle(graph):
    return not nx.is_tree(graph)

# 2. 获取图中边的个数
def number_of_edges(graph):
    return graph.number_of_edges()

# 3. 检查图中是否存在特定的边
def edge_exists(graph, edge):
    return graph.has_edge(*edge)

# 4. 获取特定节点的度
def node_degree(graph, node):
    return graph.degree(node)

# 5. 计算每个节点的三角形数量
def count_triangles(graph):
    triangle_counts = nx.triangles(graph)
    total_triangles = sum(triangle_counts.values()) // 3
    return total_triangles

# 6. 计算两个节点之间的最短路径
def shortest_path(graph, source, target):
    try:
        # 使用 nx.shortest_path_length 计算最短路径长度
        length = nx.shortest_path_length(graph, source=source, target=target)
        return length
    except nx.NetworkXNoPath:
        # 如果不存在路径，返回 0
        return 0

# 7. 检查某两个节点之间是否存在可达路径
def is_reachable(graph, source, target):
    return nx.has_path(graph, source, target)

# 8. 检查某个特定节点是否存在于图中
def node_exists(graph, node):
    return node in graph.nodes()

# 9. 获取图中共有多少个节点
def number_of_nodes(graph):
    return graph.number_of_nodes()

# 10. 计算最大团的节点数量
def max_clique_size(graph):
    # 使用networkx的近似算法计算最大团大小
    return len(nx.approximation.max_clique(graph))

# 11. 计算图密度（保留四位小数）
def graph_density(graph):
    return round(nx.density(graph), 4)

# 修改后的随机游走采样函数，采样固定数量的节点
def random_walk_sampling(G, num_nodes_to_sample):
    while True:  # 使用无限循环，直到成功生成子图
        sampled_edges = set()  # 使用集合来避免重复边
        visited_nodes = set()  # 记录已访问的节点
        start_node = random.choice(list(G.nodes()))  # 随机选择一个起始节点
        current_node = start_node
        visited_nodes.add(current_node)  # 将起始节点标记为已访问

        # 创建子图
        H = nx.Graph()

        # 初始化循环计数器
        loop_counter = 0

        while len(visited_nodes) < num_nodes_to_sample:
            loop_counter += 1  # 增加循环计数器
            
            # 如果循环次数超过 10000，则重新开始采样
            if loop_counter > 100000:
                print("超过最大循环次数，重新开始采样...")
                break  # 退出当前循环，重新开始采样

            neighbors = list(G.neighbors(current_node))  # 获取当前节点的邻居
            if not neighbors:  # 如果没有邻居，随机选择新的起始节点
                # 从未访问的节点中选择一个新的起始节点
                unvisited_nodes = list(set(G.nodes()) - visited_nodes)
                if not unvisited_nodes:  # 如果没有未访问的节点，退出循环
                    break
                current_node = random.choice(unvisited_nodes)
                visited_nodes.add(current_node)  # 将新起始节点标记为已访问
                continue
            
            next_node = random.choice(neighbors)  # 随机选择一个邻居节点
            edge = (current_node, next_node) if (current_node, next_node) in G.edges() else (next_node, current_node)
            
            if edge not in sampled_edges:  # 确保边不重复
                sampled_edges.add(edge)  # 添加边到集合中
                H.add_edge(current_node, next_node)  # 直接将边添加到子图中
                visited_nodes.add(next_node)  # 将新节点标记为已访问
            
            current_node = next_node  # 移动到下一个节点

        print(f"Sampled {len(visited_nodes)} nodes and {len(H.edges())} edges")
        # 如果成功生成子图，返回结果
        if len(visited_nodes) >= num_nodes_to_sample:
            return H  # 返回包含采样节点的子图

# 主程序
file_path = '/home/data2t1/tempuser/GTAgent/Social/1912.txt'  # 替换为你的文件路径
G = read_graph_from_file(file_path)

# 随机采样生成十个子图
num_subgraphs = 100
num_nodes_to_sample = 500  # 现在采样固定数量的节点

# 存储每个函数的结果
datasets = {
    "Cycle_Detection": [],
}

for i in tqdm(range(num_subgraphs), desc="Generating subgraphs"):
    # 使用随机游走采样节点
    H = random_walk_sampling(G, num_nodes_to_sample)

    # 获取节点列表
    node_list = list(H.nodes())

    # 初始化描述和边信息
    output_descriptions = []
    edge_infos = []
    current_description = []
    current_edges = []

    for u, v in H.edges():
        current_description.append(f"Page {u} is linked to Page {v}")
        current_edges.append((u, v))

        # 检查描述长度是否达到50
        if len(current_description) >= 50:
            edge_infos.append(current_edges)
            output_descriptions.append([", ".join(current_description)])
            current_description = []
            current_edges = []

    if current_description:
        edge_infos.append(current_edges)
        output_descriptions.append([", ".join(current_description)])

    # 随机选择两个节点
    if len(H.nodes) >= 2:
        source_node, target_node = random.sample(list(H.nodes()), 2)
    else:
        raise ValueError("子图中节点数量不足，无法随机选择源节点和目标节点。")

    # 将子图信息存储到字典中
    subgraph_info = {
        "Node_List": node_list,
        "Edges": edge_infos,
        "Edge_Count": H.number_of_edges(),
        "Description": output_descriptions,
        "question": "",
        "answer": ""
    }

    # 生成每个数据集
    # 1. 检查图中是否有环
    subgraph_info["question"] = "Does the graph have a cycle?"
    subgraph_info["answer"] = has_cycle(H)
    print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    datasets["Cycle_Detection"].append(subgraph_info)

    # # 2. 获取图中边的个数
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = "What is the number of edges?"
    # subgraph_info["answer"] = number_of_edges(H)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Edge_Count"].append(subgraph_info)

    # # 3. 检查图中是否存在特定的边
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = f"Does the edge ({source_node}, {target_node}) exist?"
    # subgraph_info["answer"] = edge_exists(H, (source_node, target_node))
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Edge_Existence"].append(subgraph_info)

    # # 4. 获取特定节点的度
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = f"What is the degree of page {source_node}?"
    # subgraph_info["answer"] = node_degree(H, source_node)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Degree_Count"].append(subgraph_info)

    # # 5. 计算每个节点的三角形数量
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = "How many triangles are in the graph?"
    # subgraph_info["answer"] = count_triangles(H)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Triangle_Count"].append(subgraph_info)

    # # 6. 计算两个节点之间的最短路径
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = f"What is the shortest path from {source_node} to {target_node}?"
    # subgraph_info["answer"] = shortest_path(H, source_node, target_node)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Shortest_Path"].append(subgraph_info)

    # # 7. 检查某两个节点之间是否存在可达路径
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = f"Is there a path from {source_node} to {target_node}?"
    # subgraph_info["answer"] = is_reachable(H, source_node, target_node)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Path_Existence"].append(subgraph_info)

    # # 8. 检查某个特定节点是否存在于图中
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = f"Does page {source_node} exist in the graph?"
    # subgraph_info["answer"] = node_exists(H, source_node)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Node_Existence"].append(subgraph_info)

    # # 9. 获取图中共有多少个节点
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = "What is the number of pages in the graph?"
    # subgraph_info["answer"] = number_of_nodes(H)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Node_Count"].append(subgraph_info)

    # # 10. 计算最大团的节点数量
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = "What is the size of the maximum clique in the graph?"
    # subgraph_info["answer"] = max_clique_size(H)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Clique_Detection"].append(subgraph_info)

    # # 11. 计算图密度
    # subgraph_info = subgraph_info.copy()  # 复制以避免覆盖
    # subgraph_info["question"] = "What is the density of the graph? (rounded to 4 decimal places)"
    # subgraph_info["answer"] = graph_density(H)
    # print(subgraph_info["question"], "->", subgraph_info["answer"])  # 打印问题和答案
    # datasets["Density_Calculation"].append(subgraph_info)

# 将每个数据集保存到不同的 JSON 文件中
for task_name, data in datasets.items():
    output_file_path = f'Social/gen/representation/{task_name}_1000_50nodes_output.json'  # 替换为你想要的输出文件路径
    with open(output_file_path, 'w') as output_file:
        json.dump(data, output_file)

print("Data sets saved to JSON files.")
