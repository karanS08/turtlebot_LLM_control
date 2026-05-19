import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/karan/Development/robot_gpt/llm_ws_1/install/tour_manager'
