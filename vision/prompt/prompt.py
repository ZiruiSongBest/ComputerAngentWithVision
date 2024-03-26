prompt = {
        "default": "What's in the image? Please provide a description of the image and any relevant details.",
        "seeclick_preprocess": "You are a helpful agent who helps me know what to do next to achieve my goal of the task",
        "Judge":
        """
        I'll give you two pictures, one before the operation and one after the operation,You are required to decide the status of the task after taking the current action, and return status in the response.
        if the task is finished,the return "FINISH",else return the reason why failed.
        The task is     
        """,
        
        "decompose_system": 
'''
You are a helpful assistant, who read the previous executed task information, current screenshot, and the task you would like to decompose into more executable tasks. Please help me to decompose the task, the decomposed task should be one of following types: Click, Enter, Scroll, Observe. Return in a json formatted string. Here's are some examples:

"use google to search 'Friends series', and return the rating of IMDb"

```json
{
    "click_google_search_text_box": {
        "name": "click_google_search_text_box",
        "description": "click on the google search box",
        "dependencies": [],
        "type": "Click",
        "content": "Search Google or type a URL"
    },

    "input_search_content": {
        "name": "input_search_content",
        "description": "enter the text into the search box",
        "dependencies": ["click_google_search_text_box"],
        "type": "Enter",
        "": "Friends Series"
    },

    "click_google_search_button": {
        "name": "click_google_search_button",
        "description": "click on the google search button to search",
        "dependencies": ["click_google_search_text_box", "input_search_content"],
        "type": "Click",
        "detail": "Friends Series"
    },

    "observe_screen_and_return_result": {
        "name": "observe_screen_and_return_result",
        "description": "observe the screen, and answer what's the rating of IMDb on the page",
        "dependencies": ["input_search_content"],
        "type": "Observe",
        "detail": ""
    }
}
```

A null dictionary should be returned if the task is finished already.
```json
{
    
}
```

remember, each step should be clear, and do what the task requires you to do.
'''
}