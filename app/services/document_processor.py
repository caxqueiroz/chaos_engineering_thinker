import os
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import networkx as nx
from io import BytesIO
import pytesseract
import json
from datetime import datetime

class DocumentProcessor:
    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def save_document(self, content: bytes, filename: str, doc_type: str) -> Tuple[str, Dict[str, Any]]:
        """Save document to disk and return the file path and metadata"""
        # Create directory for document type if it doesn't exist
        type_dir = os.path.join(self.upload_dir, doc_type)
        os.makedirs(type_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name, ext = os.path.splitext(filename)
        unique_filename = f"{base_name}_{timestamp}{ext}"
        file_path = os.path.join(type_dir, unique_filename)
        
        metadata = {
            "original_filename": filename,
            "file_path": file_path,
            "doc_type": doc_type,
            "upload_time": timestamp
        }
        
        # Handle network topology images specially
        if doc_type == "network_topology" and self._is_image(filename):
            # Save original image
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Process image and extract additional metadata
            graph_data = self._process_network_topology_image(content)
            if graph_data:
                metadata.update({
                    "graph_data": graph_data,
                    "is_network_graph": True
                })
                
                # Save graph data as JSON
                graph_json_path = f"{os.path.splitext(file_path)[0]}_graph.json"
                with open(graph_json_path, 'w') as f:
                    json.dump(graph_data, f, indent=2)
                metadata["graph_json_path"] = graph_json_path
        else:
            # Save regular document
            with open(file_path, 'wb') as f:
                f.write(content)
        
        return file_path, metadata
    
    def _is_image(self, filename: str) -> bool:
        """Check if file is an image based on extension"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        return os.path.splitext(filename)[1].lower() in image_extensions
    
    def _process_network_topology_image(self, image_content: bytes) -> Optional[Dict[str, Any]]:
        """Process network topology image and extract graph data"""
        try:
            # Open image
            img = Image.open(BytesIO(image_content))
            
            # Extract text using OCR
            text = pytesseract.image_to_string(img)
            
            # Create graph from detected components
            G = nx.Graph()
            
            # Process OCR text to identify nodes and connections
            lines = text.split('\n')
            nodes = set()
            edges = []
            
            # First pass: collect nodes
            for line in lines:
                if '->' in line or '--' in line:  # Connection indicators
                    parts = line.replace('->', '--').split('--')
                    for part in parts:
                        node = part.strip()
                        if node:
                            nodes.add(node)
                elif line.strip():  # Single node
                    nodes.add(line.strip())
            
            # Second pass: collect edges
            for line in lines:
                if '->' in line or '--' in line:
                    parts = line.replace('->', '--').split('--')
                    for i in range(len(parts)-1):
                        node1 = parts[i].strip()
                        node2 = parts[i+1].strip()
                        if node1 and node2:
                            edges.append((node1, node2))
            
            # Add nodes and edges to graph
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)
            
            # Extract graph properties
            graph_data = {
                "nodes": list(G.nodes()),
                "edges": list(G.edges()),
                "node_count": G.number_of_nodes(),
                "edge_count": G.number_of_edges(),
                "components": list(nx.connected_components(G)),
                "central_nodes": list(nx.degree_centrality(G).items()),
                "ocr_text": text
            }
            
            return graph_data
        except Exception as e:
            print(f"Error processing network topology image: {str(e)}")
            return None
