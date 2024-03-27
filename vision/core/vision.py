from typing import List, Dict, Union, Any
from friday.action.get_os_version import get_os_name
from vision.llm.openai import OpenAIProvider
from vision.core.vision_planner import VisionPlanner
from vision.core.vision_executor import VisionExecutor
from vision.grounding.seeclick import SeeClick
from utils.screen_helper import ScreenHelper
from utils.KEY_TOOL import IOEnvironment
from utils.logger import Logger


'''
综合planner和executor
1. 接受来自Friday的task，通过vision planner规划，生成vision task
2. 通过vision executor执行vision task
3. 返回结果
'''

'''
Vision Task Categories:
Click, Enter, Scroll, Observe
# 4. keyboard
# 5. observation
'''
class Vision:
    def __init__(self, llm_provider_config_path: str = "./vision/config/openai_config.json", logger: Logger = None) -> None:
        # Helpers
        self.logger = Logger() if logger is None else logger
        self.llm_provider: OpenAIProvider = OpenAIProvider()
        self.llm_provider.init_provider(llm_provider_config_path)
        self.screen_helper = ScreenHelper()
        self.key_tool = IOEnvironment()
        self.seeclick = SeeClick(screen_helper=self.screen_helper)
        
        # variables
        self.system_version = get_os_name()
        
        # submodules
        self.vision_planner = VisionPlanner(llm_provider=self.llm_provider, seeclick=self.seeclick, screen_helper=self.screen_helper, logger=self.logger)
        self.vision_executor = VisionExecutor(llm_provider=self.llm_provider, seeclick=self.seeclick, screen_helper=self.screen_helper, key_tool=self.key_tool, system_version=self.system_version, logger=self.logger)
        
    
    def global_execute(self, task, action, action_node, pre_tasks_info):
        next_action = action_node.next_action
        description = action_node.description

        self.logger.log(f"VISION Global task: {action}")
        self.vision_planner.plan_task(pre_tasks_info, action, description)
        
        result = ''
        relevant_code = {}

        # Execute task
        for task_name in self.vision_planner.vision_tasks:
            vision_type = self.vision_planner.vision_nodes[task_name].type
            pre_tasks_info = self.vision_planner.get_pre_tasks_info(task_name)
            # self.logger.info(pre_tasks_info, title='Pre-tasks Information', color='grey')
            current_result = self.execute_task(task_name)
            self.vision_planner.update_action(task_name, current_result, True, vision_type)

        is_success = self.vision_executor.observe(f"Is current task completed? Task is {task_name}: {description}. If the task seems correctly executed, please click 'Yes' to continue, otherwise click 'No'." + "\nthe current execution result is: " + result)
        
        if 'yes' in is_success:
            status = 'success'
        else:
            status = 'fail'
        # elif: status cannot be down with vision:
        #   is_success = 'replan'
        
        result = self.vision_planner.get_pre_tasks_info('end', True)
        self.logger.info(result, title='Vision Task Result', color='green')

        return [status, result, relevant_code]

    def execute_task(self, task_name) -> dict:
        # Extract task details
        vision_node = self.vision_planner.vision_nodes.get(task_name)
        type = vision_node.type
        next_action = vision_node.next_action
        description = vision_node.description
        content = vision_node.detail
        
        self.logger.info(f"Current VISION Executing tas isk: {task_name}")
        current_result = ''
        if (type == 'Enter'):
            current_result = self.vision_executor.enter(content)
        elif (type == 'Click'):
            current_result = self.vision_executor.click(content)
        elif (type == 'Observe'):
            current_result = self.vision_executor.observe(content)
        
        return current_result