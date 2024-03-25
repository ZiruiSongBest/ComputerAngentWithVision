import json
import re
from typing import List, Dict, Union, Any
from vision.llm.openai import OpenAIProvider
from vision.grounding.seeclick import SeeClick
from utils.encode_image import encode_data_to_base64_path, encode_single_data_to_base64
from utils.screen_helper import ScreenHelper
from utils.logger import Logger
from vision.prompt.prompt import prompt
from PIL import Image


'''
1. 访问llm
2. 拼接图像, prompt
3. 生成task(定义task类)
'''
class VisionPlanner:
    def __init__(self, template_file_path: str = None, llm_provider: OpenAIProvider = None, seeclick: SeeClick = None, screen_helper: ScreenHelper = None, system_version: str = None, logger: Logger = None) -> None:
        # Helpers
        self.llm_provider = llm_provider
        self.seeclick = seeclick
        self.screen_helper = screen_helper
        self.logger = logger
        
        # templates
        self.templates: Dict[str, str] = {}
        self._init_templates(template_file_path)
        
        # variables
        self.messages: List[Dict[str, Any]] = []
        self.system_version = system_version
        self.vision_tasks = []

    def _init_templates(self, template_file_path) -> None:
        if template_file_path:
            with open(template_file_path, 'r') as f:
                self.templates = json.load(f)
        else:
            self.templates = prompt
    
    def init_system_messages(self, template_name: str) -> None:
        self.messages = [{
            "role": "system",
            "content": self.templates.get(template_name, "default")
        }]
    
    def plan_task(self, task: Dict[str, Any]) -> None:
        '''
            Get a task from Friday, and plan the vision task with vision planner
        
        Args:
            param1 (dict): task from Friday
        
        Returns:
            None
        '''
        response = self.task_decompose_format_message(task)
        decomposed_tasks = self.extract_decomposed_tasks(response)
        for task in decomposed_tasks:
            self.vision_tasks.append(task)
        
        pass
    
    def decompose_task(self, task: Dict[str, Any]) -> None:
        pass
    
    def update_action(self, action: Dict[str, Any]) -> None:
        pass
    
    def task_decompose_format_message(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        '''
            Send decompose task prompt to LLM and get task list.
        '''
        system_prompt = self.templates.get("plan_task", "default")
        user_prompt = self.templates.get("plan_task_user_prompt", "default")
        
        
        # add other essential information
        
        # create self.messages
        
        # return self.llm_provider.create_completion(self.messages)

    def task_replan_format_message(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass
    
    def get_pre_tasks_info(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass
    
    def seeclick_task_planner(self, image_input: Union[str, Image.Image, None] = None, template_name: str = "seeclick_preprocess"):
        self.init_system_messages(template_name)
        base64_image = []
        
        if image_input is None:
            captured = self.screen_helper.capture()
            image_input = captured[0]
            base64_image.append(encode_single_data_to_base64(image_input))
        elif isinstance(image_input, str):
            base64_image.append(encode_single_data_to_base64(image_input))
        elif isinstance(image_input, Image.Image):
            base64_image.append(encode_single_data_to_base64(image_input))
        else:
            raise ValueError("Unsupported image input type.")
        
        screenshot_text = "Current Screenshot:"
        user_prompt = "What should I click on? Please use a short, comprehend sentence to describe the target. For example, 'Click on the red button.', 'Click on the image with a panda on it.'."
        
        self.messages.append({
            "role": "user",
            "content": [{
                "type": "text",
                "text": screenshot_text
            }, {
                "type": "image_url",
                "image_url": {
                    "url": base64_image[0]
                }
            }, {
                "type": "text",
                "text": user_prompt
            }]
        })
        
        print(self.messages)
        return self.messages
        return self.llm_provider.create_completion(self.messages)
    
    def extract_decomposed_tasks(self, response) -> List[Dict[str, Any]]:
        # Improved regular expression to find JSON data within a string
        json_regex = r'```json\s*\n\{[\s\S]*?\n\}\s*```'
        
        # Search for JSON data in the text
        matches = re.findall(json_regex, response)

        # Extract and parse the JSON data if found
        if matches:
            # Removing the ```json and ``` from the match to parse it as JSON
            json_data = matches[0].replace('```json', '').replace('```', '').strip()
            try:
                # Parse the JSON data
                parsed_json = json.loads(json_data)
                return parsed_json
            except json.JSONDecodeError as e:
                return f"Error parsing JSON data: {e}"
        else:
            return "No JSON data found in the string."

    def assemble_prompt(self, template_name: str, message_prompt: str, image_path: Union[str, List[str]]) -> str:
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found.")
        template: str = self.templates[template_name]

        encoded_images: List[str] = encode_data_to_base64_path(image_path)
        prompt: str = template.replace("{{message_prompt}}", message_prompt).replace("{{image_url}}", encoded_images[0])
        return prompt

    def append_images_to_message(self, message: Dict[str, Any], image_paths: Union[str, List[str]]) -> None:
        encoded_images: List[str] = encode_data_to_base64_path(image_paths)
        for encoded_image in encoded_images:
            msg_content: Dict[str, Any] = {
                "type": "image_url",
                "image_url": {"url": encoded_image}
            }
            message["content"].append(msg_content)

    @staticmethod
    def simple_prompt_construction(system_prompt: str, image: Any, user_prompt: str) -> Dict[str, Any]:
        encoded_image: List[str] = encode_data_to_base64_path(image)
        return {
            "system": system_prompt,
            "image": encoded_image[0],
            "user_prompt": user_prompt
        }

    @staticmethod
    def prompt_construction(system_prompt: str, image_list: List[Any], user_prompt: str, include_last_screenshot: bool = False) -> List[Dict[str, Any]]:
        prompt_message: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}] if system_prompt else []

        screenshot_text: List[str] = ["Screenshot for the last step:"] if include_last_screenshot else []
        screenshot_text += ["Current Screenshots:", "Annotated Screenshot:"]

        message: List[Dict[str, Any]] = []
        for i, image in enumerate(image_list):
            encoded_image: List[str] = encode_data_to_base64_path(image)
            message.extend([
                {"type": "text", "text": screenshot_text[i]},
                {"type": "image_url", "image_url": {"url": encoded_image[0]}}
            ])
        message.append({"type": "text", "text": user_prompt})
        prompt_message.append({"role": "user", "content": message})

        return prompt_message
