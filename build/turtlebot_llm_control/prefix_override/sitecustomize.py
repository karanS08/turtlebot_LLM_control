import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/tom/llm_ws/turtlebot_LLM_control/install/turtlebot_llm_control'
