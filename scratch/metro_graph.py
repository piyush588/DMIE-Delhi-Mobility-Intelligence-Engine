import json
import heapq
import math

with open("data/metro.json") as f:
    stations = json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Build graph: node = station name, edges to all other stations on the same line
graph = {}
for s in stations:
    name = s["name"]
    graph[name] = {"coords": (s["details"]["latitude"], s["details"]["longitude"]), "lines": set(s["details"]["line"])}

edges = {}
for name1, data1 in graph.items():
    edges[name1] = []
    for name2, data2 in graph.items():
        if name1 == name2: continue
        shared_lines = data1["lines"].intersection(data2["lines"])
        if shared_lines:
            dist = haversine(data1["coords"][0], data1["coords"][1], data2["coords"][0], data2["coords"][1])
            # add penalty for interchange later if needed, but here we just connect stations on same line
            edges[name1].append((name2, dist, list(shared_lines)[0]))

def find_path(src, dest):
    # Dijkstra
    q = [(0, src, [src], [])] # dist, current, path, lines_used
    visited = set()
    
    while q:
        dist, curr, path, lines_used = heapq.heappop(q)
        if curr == dest:
            return dist, path, lines_used
            
        if curr in visited:
            continue
        visited.add(curr)
        
        for nxt, d, line in edges[curr]:
            if nxt not in visited:
                # small penalty for changing lines
                penalty = 0
                if lines_used and lines_used[-1] != line:
                    penalty = 5.0 # 5km penalty for changing lines to minimize interchanges
                heapq.heappush(q, (dist + d + penalty, nxt, path + [nxt], lines_used + [line]))
                
    return None

dist, path, lines = find_path("Adarsh Nagar", "Akshardham")
print(dist)
# Extract segments
segments = []
curr_line = lines[0]
curr_start = path[0]
for i in range(1, len(path)):
    if lines[i-1] != curr_line:
        segments.append((curr_start, path[i-1], curr_line))
        curr_line = lines[i-1]
        curr_start = path[i-1]
segments.append((curr_start, path[-1], curr_line))
print(segments)
