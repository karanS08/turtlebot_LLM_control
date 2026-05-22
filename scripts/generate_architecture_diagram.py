#!/usr/bin/env python3
"""Generate the turtlebot_llm_control architecture flow diagram."""

import graphviz

g = graphviz.Digraph(
    "turtlebot_llm_control",
    filename="docs/architecture",
    format="png",
    graph_attr={
        "rankdir": "TB",
        "splines": "polyline",
        "nodesep": "0.7",
        "ranksep": "0.9",
        "fontname": "Helvetica",
        "bgcolor": "#1e1e2e",
        "pad": "0.6",
        "dpi": "160",
    },
    node_attr={
        "fontname": "Helvetica",
        "fontsize": "11",
        "style": "filled",
        "penwidth": "0",
    },
    edge_attr={
        "fontname": "Helvetica",
        "fontsize": "9",
        "color": "#6c7086",
        "fontcolor": "#a6adc8",
    },
)

NODE_COLOR   = "#313244"
NODE_FONT    = "#cdd6f4"
TOPIC_COLOR  = "#45475a"
TOPIC_FONT   = "#bac2de"
EXTERN_COLOR = "#1e1e2e"
EXTERN_FONT  = "#6c7086"
EXTERN_PEN   = "1.5"

def node(name, label, color=NODE_COLOR, fontcolor=NODE_FONT, shape="box", **kw):
    g.node(name, label=label, fillcolor=color, fontcolor=fontcolor, shape=shape, **kw)

def topic(name, label):
    g.node(name, label=label, fillcolor=TOPIC_COLOR, fontcolor=TOPIC_FONT,
           shape="ellipse", fontsize="9")

def extern(name, label):
    g.node(name, label=label, fillcolor=EXTERN_COLOR, fontcolor=EXTERN_FONT,
           shape="box", style="dashed", penwidth=EXTERN_PEN, color="#585b70")

# ── External hardware / services ────────────────────────────────────────────
extern("mic",     "Microphone")
extern("speaker", "System TTS\n(spd-say/espeak)")
extern("pepper",  "Pepper Robot\n(/pepper_speech)")
extern("nav2",    "Nav2 Stack\n(NavigateToPose)")
extern("ollama",  "Ollama LLM\n(qwen2.5-coder)")
extern("db",      "tours.db\n(SQLite)")
extern("amcl",    "AMCL Pose\n(/amcl_pose)")

# ── ROS nodes ────────────────────────────────────────────────────────────────
node("stt",      "speech_to_text_node",      color="#1e3a5f", fontcolor="#89b4fa")
node("llm",      "speech_command_node",       color="#1e3a5f", fontcolor="#89b4fa")
node("bt",       "bt_orchestrator_node",      color="#2d1b4e", fontcolor="#cba6f7")
node("resp",     "speech_response_node",      color="#1e3a5f", fontcolor="#89b4fa")
node("emotion",  "emotion_node",              color="#1a3a2a", fontcolor="#a6e3a1")
node("wp_speak", "waypoint_speaker_node",     color="#3a2a1a", fontcolor="#fab387")
node("tour_rec", "tour_recording_manager",    color="#3a2a1a", fontcolor="#fab387")
node("tsp",      "tsp_gui_node",              color="#2a2a1a", fontcolor="#f9e2af")
node("bridge",   "tour_intent_bridge_node",   color="#1e3a5f", fontcolor="#89b4fa")

# ── Topics ───────────────────────────────────────────────────────────────────
topic("t_text",    "/speech/text")
topic("t_intent",  "/speech/intent")
topic("t_resp",    "/speech/response")
topic("t_emotions","/emotions")
topic("t_talk",    "/talk_command")
topic("t_done",    "/done_speaking")
topic("t_route_r", "/route/record")
topic("t_route_d", "/route/data")
topic("t_replay",  "/route/replay")
topic("t_tsp_show","/tsp_gui/show")
topic("t_tsp_cmd", "/tsp_command")
topic("t_status",  "/tour/status")
topic("t_emo_raw", "/robot/emotion")

# ── Data flow ────────────────────────────────────────────────────────────────

# Input pipeline
g.edge("mic",       "stt",        label="audio")
g.edge("stt",       "t_text",     label="STT text")
g.edge("ollama",    "llm",        label="inference", style="dashed")
g.edge("t_text",    "llm")
g.edge("llm",       "t_intent",   label="IntentToken JSON")

# Intent fans out
g.edge("t_intent",  "bt")
g.edge("t_intent",  "bridge")

# Orchestrator outputs
g.edge("bt",        "t_resp",     label="say()")
g.edge("bt",        "nav2",       label="NavigateToPose action", style="dashed")
g.edge("bt",        "t_route_r",  label="start/stop")
g.edge("bt",        "t_replay",   label="replay label")
g.edge("bt",        "t_status")

# Speech response
g.edge("t_resp",    "resp")
g.edge("resp",      "speaker",    label="TTS",  style="dashed")
g.edge("resp",      "pepper",     label="text", style="dashed")

# Emotion engine
g.edge("t_text",    "emotion")
g.edge("t_resp",    "emotion")
g.edge("emotion",   "t_emotions")

# Waypoint speaker
g.edge("t_talk",    "wp_speak")
g.edge("db",        "wp_speak",   label="description", style="dashed")
g.edge("amcl",      "wp_speak",   label="pose",        style="dashed")
g.edge("wp_speak",  "speaker",    label="TTS",         style="dashed")
g.edge("wp_speak",  "t_done")
g.edge("wp_speak",  "t_emo_raw")

# Tour recording
g.edge("bridge",    "t_route_r")
g.edge("t_route_r", "tour_rec")
g.edge("tour_rec",  "t_route_d",  label="waypoints JSON")
g.edge("t_route_d", "bt")

# TSP GUI
g.edge("t_tsp_show","tsp")
g.edge("tsp",       "t_tsp_cmd",  label="TspCommand")

# ── Rank groupings ───────────────────────────────────────────────────────────
with g.subgraph() as s:
    s.attr(rank="same")
    s.node("mic")
    s.node("ollama")
    s.node("t_tsp_show")

with g.subgraph() as s:
    s.attr(rank="same")
    s.node("stt")
    s.node("tsp")

with g.subgraph() as s:
    s.attr(rank="same")
    s.node("llm")
    s.node("bridge")

with g.subgraph() as s:
    s.attr(rank="same")
    s.node("bt")

with g.subgraph() as s:
    s.attr(rank="same")
    s.node("resp")
    s.node("emotion")
    s.node("tour_rec")

with g.subgraph() as s:
    s.attr(rank="same")
    s.node("wp_speak")
    s.node("speaker")
    s.node("pepper")
    s.node("db")
    s.node("amcl")

import os
os.makedirs("docs", exist_ok=True)
g.render(cleanup=True)
print("Saved to docs/architecture.png")
