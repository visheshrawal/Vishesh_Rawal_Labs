import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict, List

class ArchitectureMapper:
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
    
    def build_architecture_graph(self, project_map: Dict):
        """HARD: Build interactive dependency graph"""
        self.dependency_graph.clear()
        
        # Add nodes (files, classes, functions)
        for file_path, file_info in project_map.items():
            self._add_file_to_graph(file_path, file_info)
        
        # Build dependencies
        self._build_dependencies(project_map)
        
        return self._generate_visualization()
    
    def _add_file_to_graph(self, file_path, file_info):
        """HARD: Add hierarchical code structure to graph"""
        # File node
        self.dependency_graph.add_node(file_path, type='file', size=50)
        
        # Class nodes
        for class_name, methods in file_info.get('classes', {}).items():
            class_node = f"{file_path}::{class_name}"
            self.dependency_graph.add_node(class_node, type='class', size=30)
            self.dependency_graph.add_edge(file_path, class_node)
            
            # Method nodes
            for method in methods:
                method_node = f"{class_node}.{method}"
                self.dependency_graph.add_node(method_node, type='method', size=10)
                self.dependency_graph.add_edge(class_node, method_node)
    
    def _build_dependencies(self, project_map):
        """HARD: Build call relationships between components"""
        # This is where it gets REALLY complex
        # We need to analyze imports and function calls
        
        for file_path, file_info in project_map.items():
            imports = file_info.get('imports', [])
            
            for imp in imports:
                # Find which local file this import corresponds to
                target_file = self._resolve_import(imp, project_map)
                if target_file and target_file in self.dependency_graph:
                    self.dependency_graph.add_edge(file_path, target_file)
    
    def _generate_visualization(self):
        """HARD: Create interactive 3D force-directed graph"""
        # Use plotly for beautiful 3D visualization
        pos = nx.spring_layout(self.dependency_graph, dim=3)
        
        # Extract node positions
        node_x, node_y, node_z, node_text = [], [], [], []
        for node, (x, y, z) in pos.items():
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            node_text.append(node)
        
        # Create 3D scatter plot
        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            marker=dict(size=10, color='lightblue'),
            text=node_text,
            textposition="middle center"
        )
        
        # Add edges
        edge_x, edge_y, edge_z = [], [], []
        for edge in self.dependency_graph.edges():
            x0, y0, z0 = pos[edge[0]]
            x1, y1, z1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])
        
        edge_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(width=2, color='gray')
        )
        
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(title='Code Architecture 3D Visualization')
        
        return fig.to_html()