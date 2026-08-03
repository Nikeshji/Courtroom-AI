from graph.graph import build_graph
from graph.state import CourtState

graph = build_graph()

initial_state: CourtState = {
    "complaint": "Someone crashed their car into my shop and ran away. I don't know who it was.",
    "is_running": True,
    "execution_times": {}
}

print("Starting simulation... This will take 5-15 minutes.")
print("=" * 50)

for node_output in graph.stream(initial_state):
    for node_name, output in node_output.items():
        print(f"\n>>> {node_name.upper()} COMPLETE <<<")
        print(f"Keys returned: {list(output.keys())}")

print("\n" + "=" * 50)
print("SIMULATION COMPLETE!")