"""Action handler for processing AI model outputs."""

import time
from dataclasses import dataclass
from typing import Any, Callable

from phone_agent.adb import (
    back,
    clear_text,
    detect_and_set_adb_keyboard,
    double_tap,
    home,
    launch_app,
    long_press,
    restore_keyboard,
    swipe,
    tap,
    type_text,
)


@dataclass
class ActionResult:
    """Result of an action execution."""

    success: bool
    should_finish: bool
    message: str | None = None
    requires_confirmation: bool = False


class ActionHandler:
    """
    Handles execution of actions from AI model output.

    Args:
        device_id: Optional ADB device ID for multi-device setups.
        confirmation_callback: Optional callback for sensitive action confirmation.
            Should return True to proceed, False to cancel.
        takeover_callback: Optional callback for takeover requests (login, captcha).
    """

    def __init__(
        self,
        device_id: str | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        self.device_id = device_id
        self.confirmation_callback = confirmation_callback or self._default_confirmation
        self.takeover_callback = takeover_callback or self._default_takeover

    def execute(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> ActionResult:
        """
        Execute an action from the AI model.

        Args:
            action: The action dictionary from the model.
            screen_width: Current screen width in pixels.
            screen_height: Current screen height in pixels.

        Returns:
            ActionResult indicating success and whether to finish.
        """
        action_type = action.get("_metadata")

        if action_type == "finish":
            return ActionResult(
                success=True, should_finish=True, message=action.get("message")
            )

        if action_type != "do":
            return ActionResult(
                success=False,
                should_finish=True,
                message=f"Unknown action type: {action_type}",
            )

        action_name = action.get("action")
        handler_method = self._get_handler(action_name)

        if handler_method is None:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Unknown action: {action_name}",
            )

        try:
            return handler_method(action, screen_width, screen_height)
        except Exception as e:
            return ActionResult(
                success=False, should_finish=False, message=f"Action failed: {e}"
            )

    def _get_handler(self, action_name: str) -> Callable | None:
        """Get the handler method for an action."""
        handlers = {
            "Launch": self._handle_launch,
            "Tap": self._handle_tap,
            "Type": self._handle_type,
            "Type_Name": self._handle_type,
            "Swipe": self._handle_swipe,
            "Back": self._handle_back,
            "Home": self._handle_home,
            "Double Tap": self._handle_double_tap,
            "Long Press": self._handle_long_press,
            "Wait": self._handle_wait,
            "Take_over": self._handle_takeover,
            "Note": self._handle_note,
            "Call_API": self._handle_call_api,
            "Interact": self._handle_interact,
        }
        return handlers.get(action_name)

    def _convert_relative_to_absolute(
        self, element: list[int] | str, screen_width: int, screen_height: int
    ) -> tuple[int, int]:
        """Convert relative coordinates (0-1000) to absolute pixels."""
        if isinstance(element, str):
            try:
                import json
                # 处理可能的字符串格式，如 "[285, 82]"
                element = json.loads(element)
            except:
                # 尝试简单的去除括号
                try:
                    cleaned = element.replace("[", "").replace("]", "")
                    parts = cleaned.split(",")
                    element = [int(p.strip()) for p in parts]
                except:
                    raise ValueError(f"Invalid element format: {element}")

        if not isinstance(element, (list, tuple)) or len(element) < 2:
             raise ValueError(f"Element must be a list of 2 integers, got {element}")
        
        # 确保坐标是数字
        try:
            x_rel = float(element[0])
            y_rel = float(element[1])
        except (ValueError, TypeError):
             raise ValueError(f"Element coordinates must be numbers, got {element}")

        x = int(x_rel / 1000 * screen_width)
        y = int(y_rel / 1000 * screen_height)
        return x, y

    def _handle_launch(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle app launch action."""
        app_name = action.get("app")
        if not app_name:
            return ActionResult(False, False, "No app name specified")

        success = launch_app(app_name, self.device_id)
        if success:
            return ActionResult(True, False)
        
        # 增强错误提示，引导模型进行手动查找
        return ActionResult(
            False, 
            False, 
            f"App not found in config: {app_name}. Please try to find it on the screen manually (Swipe/Tap)."
        )

    def _handle_tap(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle tap action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        print(f"[DEBUG] Tap action: relative={element}, absolute=({x}, {y})")

        # Check for sensitive operation
        if "message" in action:
            if not self.confirmation_callback(action["message"]):
                return ActionResult(
                    success=False,
                    should_finish=True,
                    message="User cancelled sensitive operation",
                )

        tap(x, y, self.device_id)
        
        # 容错处理：对于可能的边缘点击，尝试在周围小范围内补充点击
        # 很多时候模型给出的坐标可能正好在控件边缘，或者因为分辨率映射导致偏差
        # 尤其是顶部搜索框，很容易点偏
        if y < height * 0.15: # 针对顶部区域（通常是搜索框/导航栏）加强容错
            print(f"[DEBUG] 启用顶部区域容错点击策略...")
            offset = 20 # 像素偏移量
            # 向下偏移一点（通常顶部控件容易偏上）
            tap(x, y + offset, self.device_id, delay=0.1)
            # 左右微调
            tap(x + offset, y, self.device_id, delay=0.1)
            tap(x - offset, y, self.device_id, delay=0.1)
        
        return ActionResult(True, False)

    def _handle_type(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle text input action."""
        text = action.get("text", "")

        # Switch to ADB keyboard
        original_ime = detect_and_set_adb_keyboard(self.device_id)
        time.sleep(1.0)

        # Clear existing text and type new text
        clear_text(self.device_id)
        time.sleep(1.0)

        type_text(text, self.device_id)
        time.sleep(1.0)

        # Restore original keyboard
        restore_keyboard(original_ime, self.device_id)
        time.sleep(1.0)

        return ActionResult(True, False)

    def _handle_swipe(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle swipe action."""
        start = action.get("start")
        end = action.get("end")

        if not start or not end:
            return ActionResult(False, False, "Missing swipe coordinates")

        start_x, start_y = self._convert_relative_to_absolute(start, width, height)
        end_x, end_y = self._convert_relative_to_absolute(end, width, height)

        swipe(start_x, start_y, end_x, end_y, device_id=self.device_id)
        return ActionResult(True, False)

    def _handle_back(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle back button action."""
        back(self.device_id)
        return ActionResult(True, False)

    def _handle_home(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle home button action."""
        home(self.device_id)
        return ActionResult(True, False)

    def _handle_double_tap(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle double tap action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        double_tap(x, y, self.device_id)
        return ActionResult(True, False)

    def _handle_long_press(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle long press action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        long_press(x, y, device_id=self.device_id)
        return ActionResult(True, False)

    def _handle_wait(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle wait action."""
        duration_str = action.get("duration", "1 seconds")
        try:
            duration = float(duration_str.replace("seconds", "").strip())
        except ValueError:
            duration = 1.0

        time.sleep(duration)
        return ActionResult(True, False)

    def _handle_takeover(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle takeover request (login, captcha, etc.)."""
        message = action.get("message", "User intervention required")
        self.takeover_callback(message)
        return ActionResult(True, False)

    def _handle_note(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle note action (placeholder for content recording)."""
        # This action is typically used for recording page content
        # Implementation depends on specific requirements
        return ActionResult(True, False)

    def _handle_call_api(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle API call action (placeholder for summarization)."""
        # This action is typically used for content summarization
        # Implementation depends on specific requirements
        return ActionResult(True, False)

    def _handle_interact(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle interaction request (user choice needed)."""
        # This action signals that user input is needed
        return ActionResult(True, False, message="User interaction required")

    @staticmethod
    def _default_confirmation(message: str) -> bool:
        """Default confirmation callback using console input."""
        response = input(f"Sensitive operation: {message}\nConfirm? (Y/N): ")
        return response.upper() == "Y"

    @staticmethod
    def _default_takeover(message: str) -> None:
        """Default takeover callback using console input."""
        input(f"{message}\nPress Enter after completing manual operation...")


def parse_action(response: str) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Parse action from model response.

    Args:
        response: Raw response string from the model.

    Returns:
        Parsed action dictionary or list of action dictionaries.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    import json
    import re
    
    try:
        response = response.strip()
        # Clean up tags
        response = response.replace("<|begin_of_box|>", "").replace("<|end_of_box|>", "")
        response = response.replace("{think}", "").replace("{action}", "")
        response = response.replace("</s>", "")
        response = response.replace("<think>", "").replace("</think>", "")
        response = response.replace("<answer>", "").replace("</answer>", "")
        response = response.replace("answer>", "")
        response = response.replace("<tool_call>", "")
        
        # 预处理: 处理多行响应，提取有效的动作行
        lines = response.split('\n')
        valid_lines = []
        action_lines = []  # 专门收集动作行
        
        for line in lines:
            line = line.strip()
            # 跳过空行和明显的模板占位符
            if not line or line in ['{action}', '{think}', '<action>', '</action>', '<answer>']:
                continue
            
            # 收集所有可能的动作行
            if (line.startswith('do(') or line.startswith('finish(') or 
                line.startswith('{action=') or line.startswith('{"action"')):
                action_lines.append(line)
            
            valid_lines.append(line)
        
        # Helper function to parse a single action string
        def parse_single_action(act_str: str) -> dict[str, Any]:
            act_str = act_str.strip()
            # Method 1: eval do(...) or finish(...)
            if act_str.startswith("do(") or act_str.startswith("finish("):
                return eval(act_str)
            
            # Method 2: Regex for do(...)
            m = re.search(r'(do\([^\n\r]*\))', act_str)
            if not m:
                m = re.search(r'(finish\([^\n\r]*\))', act_str)
            if m:
                return eval(m.group(1))
            
            # Method 3: finish(message=...)
            if act_str.startswith("finish"):
                return {
                    "_metadata": "finish",
                    "message": act_str.replace("finish(message=", "").strip()[1:-2],
                }
            
            # Method 4: JSON-like
            if "{" in act_str and "}" in act_str:
                dict_match = re.search(r'\{[^}]+\}', act_str)
                if dict_match:
                    dict_str = dict_match.group(0)
                    dict_str = re.sub(r'(\w+)=(\[[^\]]+\])', r'"\1": \2', dict_str)
                    dict_str = re.sub(r'(\w+)="([^"]+)"', r'"\1": "\2"', dict_str)
                    dict_str = re.sub(r'(\w+)=([^,}\s\[]+)', r'"\1": "\2"', dict_str)
                    action = json.loads(dict_str)
                    if "_metadata" not in action:
                        if "action" in action:
                            action["_metadata"] = "do"
                        else:
                            action["_metadata"] = "finish"
                    return action
            
            # Method 5: Pure JSON
            action = json.loads(act_str)
            if "_metadata" not in action:
                action["_metadata"] = "do"
            return action

        # Parse all identified action lines
        parsed_actions = []
        if action_lines:
            for line in action_lines:
                try:
                    parsed_actions.append(parse_single_action(line))
                except:
                    pass
        elif valid_lines:
            # Fallback to checking valid lines if no explicit action lines found
            for line in valid_lines:
                if line.startswith('do(') or line.startswith('finish('):
                    try:
                        parsed_actions.append(parse_single_action(line))
                    except:
                        pass
            
            # If still empty, try parsing the first valid line
            if not parsed_actions and valid_lines:
                try:
                    parsed_actions.append(parse_single_action(valid_lines[0]))
                except:
                    pass

        # Return logic
        if not parsed_actions:
            # Try the "Wait" heuristic as a last resort on the whole response
            lower = response.lower()
            if ("wait" in lower or "等待" in response or "加载" in response or "loading" in lower or "刷新" in response):
                try:
                    dur_match = re.search(r"(\d+)\s*秒", response)
                    if not dur_match:
                         dur_match = re.search(r"(\d+)\s*seconds?", response, re.IGNORECASE)
                    
                    duration = f"{dur_match.group(1)} seconds" if dur_match else "2 seconds"
                    return {
                        "_metadata": "do",
                        "action": "Wait",
                        "duration": duration,
                    }
                except:
                    return {
                        "_metadata": "do",
                        "action": "Wait",
                        "duration": "2 seconds",
                    }
            raise ValueError(f"无法解析动作格式: {response}")

        if len(parsed_actions) == 1:
            return parsed_actions[0]
        return parsed_actions
        
    except Exception as e:
        raise ValueError(f"Failed to parse action: {e}")


def do(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'do' actions."""
    kwargs["_metadata"] = "do"
    return kwargs


def finish(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'finish' actions."""
    kwargs["_metadata"] = "finish"
    return kwargs
