import xml.etree.ElementTree as ET
import xml.dom.minidom

def create_drawio():
    mxfile = ET.Element('mxfile', version="14.6.13")
    diagram = ET.SubElement(mxfile, 'diagram', id="sys_arch", name="System Pipeline")
    model = ET.SubElement(diagram, 'mxGraphModel', dx="1000", dy="1000", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1169", pageHeight="827")
    root = ET.SubElement(model, 'root')
    
    # Required default cells
    ET.SubElement(root, 'mxCell', id="0")
    ET.SubElement(root, 'mxCell', id="1", parent="0")

    cells = []
    cell_id = 2

    def add_node(parent_id, value, x, y, w, h, style):
        nonlocal cell_id
        cell = ET.SubElement(root, 'mxCell', id=str(cell_id), value=value, style=style, vertex="1", parent=parent_id)
        geo = ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h))
        geo.set('as', 'geometry')
        cid = str(cell_id)
        cell_id += 1
        return cid

    def add_edge(parent_id, value, source, target, style, entryX=None, entryY=None, exitX=None, exitY=None):
        nonlocal cell_id
        if entryX is not None:
            style += f"entryX={entryX};entryY={entryY};"
        if exitX is not None:
            style += f"exitX={exitX};exitY={exitY};"
            
        cell = ET.SubElement(root, 'mxCell', id=str(cell_id), value=value, style=style, edge="1", parent=parent_id, source=source, target=target)
        geo = ET.SubElement(cell, 'mxGeometry')
        geo.set('relative', '1')
        geo.set('as', 'geometry')
        cid = str(cell_id)
        cell_id += 1
        return cid

    # Define nodes
    # STAGE 1
    bg1_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffeeee;strokeColor=#aaaaaa;verticalAlign=top;align=left;spacingTop=10;spacingLeft=10;fontStyle=1;fontSize=14;fontColor=#333333;dashed=0;"
    bg1 = add_node("1", "STAGE 1: Global Mapping Layer (Mapping & Pre-processing)", 40, 40, 1080, 200, bg1_style)

    n1a_val = '<div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px;">1A. Aerial Survey &amp; Image Capture</div><div style="text-align: left; font-size: 12px; color: #444444; margin-left:10px;">&bull; UAV high-altitude top-down photography<br>&bull; Acquire global RGB images of orchard<br>&bull; Transmit to ground workstation</div>'
    n1a_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffcccc;strokeColor=#000000;verticalAlign=top;spacingTop=10;"
    n1a = add_node("1", n1a_val, 80, 100, 350, 100, n1a_style)

    n1b_val = '<div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px;">1B. HSV Color Segmentation &amp; Skeleton Extraction</div><div style="text-align: left; font-size: 12px; color: #444444; margin-left:10px;">&bull; CLAHE equalization removes glare/shadows<br>&bull; Morphological close filters weed noise<br>&bull; Extract physical centerlines of ridges &amp; trenches</div>'
    n1b_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffcc99;strokeColor=#000000;verticalAlign=top;spacingTop=10;"
    n1b = add_node("1", n1b_val, 650, 100, 420, 100, n1b_style)

    # STAGE 2
    bg2_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#eedeec;strokeColor=#aaaaaa;verticalAlign=top;align=left;spacingTop=10;spacingLeft=10;fontStyle=1;fontSize=14;fontColor=#333333;"
    bg2 = add_node("1", "STAGE 2: Navigation Strategy Layer (Planning)", 40, 280, 1080, 180, bg2_style)

    n2_val = '<div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px;">2. CCPP Full Coverage Path Planning</div><div style="text-align: left; font-size: 12px; color: #444444; margin-left:10px;">&bull; Auto-generate sequential zigzag cruise trajectories<br>&bull; Traverse each trench sequentially without skipping rows<br>&bull; CCPP planner ensures smooth obstacle avoidance &amp; transitions</div>'
    n2_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#e6ccff;strokeColor=#8b008b;strokeWidth=2;verticalAlign=top;spacingTop=10;"
    n2 = add_node("1", n2_val, 320, 330, 480, 100, n2_style)

    # STAGE 3
    bg3_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#eeffee;strokeColor=#aaaaaa;verticalAlign=top;align=left;spacingTop=10;spacingLeft=10;fontStyle=1;fontSize=14;fontColor=#333333;"
    bg3 = add_node("1", "STAGE 3: Perception & Actuation Layer", 40, 500, 1080, 200, bg3_style)

    n3a_val = '<div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px;">3A. AGV Dual-Camera Dynamic Side-view Capture</div><div style="text-align: left; font-size: 12px; color: #444444; margin-left:10px;">&bull; AGV drives along CCPP trajectory<br>&bull; Dual side cameras capture ridges simultaneously<br>&bull; Discard homography; dynamic local projection<br>&nbsp;&nbsp;based on vehicle pose and depth d</div>'
    n3a_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ccffcc;strokeColor=#000000;verticalAlign=top;spacingTop=10;"
    n3a = add_node("1", n3a_val, 60, 560, 320, 110, n3a_style)

    n3b_val = '<div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px;">3B. YOLOv11s Perception &amp; Tracking</div><div style="text-align: left; font-size: 12px; color: #444444; margin-left:10px;">&bull; Lock to lightweight S scale (cuda:0)<br>&bull; Accurate maturity recognition &amp; ID tracking<br>&bull; Tiny object detection head (P2 head)<br>&nbsp;&nbsp;with CBAM suppresses glare and noise</div>'
    n3b_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ccffcc;strokeColor=#ff0000;strokeWidth=2;verticalAlign=top;spacingTop=10;"
    n3b = add_node("1", n3b_val, 420, 560, 320, 110, n3b_style)

    n3c_val = '<div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px;">3C. Spatial Deduplication &amp; Fusion</div><div style="text-align: left; font-size: 12px; color: #444444; margin-left:10px;">&bull; 10cm Euclidean distance point cloud clustering<br>&bull; Cross-frame repeated detection deduplication<br>&bull; Dynamically update global physical coordinates<br>&nbsp;&nbsp;and average maturity of strawberries</div>'
    n3c_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ccffcc;strokeColor=#000000;verticalAlign=top;spacingTop=10;"
    n3c = add_node("1", n3c_val, 780, 560, 320, 110, n3c_style)

    # STAGE 4
    bg4_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#fffeee;strokeColor=#aaaaaa;verticalAlign=top;align=left;spacingTop=10;spacingLeft=10;fontStyle=1;fontSize=14;fontColor=#333333;"
    bg4 = add_node("1", "STAGE 4: Visualization & Decision Layer", 40, 740, 1080, 160, bg4_style)

    n4_val = '<div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 8px;">4. Interactive Digital Twin Dashboard</div><div style="text-align: left; font-size: 12px; color: #444444; margin-left:10px;">&bull; Accumulate global point cloud data of strawberry maturity<br>&bull; Generate maturity decision heatmaps (KDE)<br>&bull; Intuitively guide farmers for precise harvesting strategies</div>'
    n4_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffcc;strokeColor=#b8860b;strokeWidth=2;verticalAlign=top;spacingTop=10;"
    n4 = add_node("1", n4_val, 320, 780, 480, 90, n4_style)

    # Edges
    edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#444444;strokeWidth=2;fontStyle=1;fontSize=12;fontColor=#00008b;labelBackgroundColor=none;"
    add_edge("1", "Global RGB Image", n1a, n1b, edge_style)
    add_edge("1", "Grid Map (farm_grid_map.csv)", n1b, n2, edge_style, exitX=0.5, exitY=1, entryX=0.75, entryY=0)
    add_edge("1", "Inspection Waypoints (coverage_path)", n2, n3a, edge_style, exitX=0.25, exitY=1, entryX=0.5, entryY=0)
    add_edge("1", "Real-time Video Stream", n3a, n3b, edge_style)
    add_edge("1", "Maturity Feature Points", n3b, n3c, edge_style)
    add_edge("1", "Deduplicated Point Cloud Data", n3c, n4, edge_style, exitX=0.5, exitY=1, entryX=0.75, entryY=0)

    # Write to file
    xml_str = xml.dom.minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")
    # removing the xml declaration since drawio files usually don't strictly need it, but minidom adds it. Drawio works fine with it.
    with open('d:/銘澄專區/畢業專題工作區/System_Architecture_Pipeline.drawio', 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print("Draw.io file generated successfully!")

if __name__ == '__main__':
    create_drawio()
