# src/tools/hands_tool.py

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC

# Updated import: includes new helper
from src.tools.logger_tool import log_event, format_exception

class HandsTool:
    def __init__(self, driver):
        self.driver = driver

    def click_element(self, identifier: str, by: str = "xpath"):
        try:
            if by == "xpath":
                element = self.driver.find_element(By.XPATH, identifier)
            elif by == "css":
                element = self.driver.find_element(By.CSS_SELECTOR, identifier)
            elif by == "id":
                element = self.driver.find_element(By.ID, identifier)
            elif by == "name":
                element = self.driver.find_element(By.NAME, identifier)
            else:
                log_event(f"❌ Unsupported selector type: {by}")
                return False

            element.click()
            log_event(f"✅ Clicked element: {identifier} ({by})")
            time.sleep(2)
            return True
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            log_event(f"⚠️ Failed to click") 
            #log_event(f"⚠️ Failed to click: {identifier} ({by}) - {format_exception(e)}")
            return False

    def type_text(self, identifier: str, text: str, by: str = "xpath"):
        try:
            if by == "xpath":
                field = self.driver.find_element(By.XPATH, identifier)
            elif by == "css":
                field = self.driver.find_element(By.CSS_SELECTOR, identifier)
            elif by == "id":
                field = self.driver.find_element(By.ID, identifier)
            elif by == "name":
                field = self.driver.find_element(By.NAME, identifier)
            else:
                log_event(f"❌ Unsupported selector type: {by}")
                return False

            field.clear()
            field.send_keys(text)
            log_event(f"✅ Typed text in field: {identifier} ({by}) --> {text}")
            time.sleep(1)
            return True
        except NoSuchElementException as e:
            log_event(f"⚠️ Failed to type") 
            #log_event(f"⚠️ Failed to type: {identifier} ({by}) - {format_exception(e)}")
            return False

    def select_dropdown(self, identifier: str, option_text: str, by: str = "xpath"):
        try:
            if by == "xpath":
                dropdown = Select(self.driver.find_element(By.XPATH, identifier))
            elif by == "css":
                dropdown = Select(self.driver.find_element(By.CSS_SELECTOR, identifier))
            elif by == "id":
                dropdown = Select(self.driver.find_element(By.ID, identifier))
            elif by == "name":
                dropdown = Select(self.driver.find_element(By.NAME, identifier))
            else:
                log_event(f"❌ Unsupported selector type: {by}")
                return False

            dropdown.select_by_visible_text(option_text)
            log_event(f"✅ Selected dropdown option: {option_text} ({by})")
            time.sleep(1)
            return True
        except NoSuchElementException as e:
            log_event(f"⚠️ Failed to select dropdown")
            #log_event(f"⚠️ Failed to select dropdown: {identifier} ({by}) - {format_exception(e)}")
            return False

    def check_checkbox(self, identifier: str, by: str = "xpath"):
        try:
            if by == "xpath":
                checkbox = self.driver.find_element(By.XPATH, identifier)
            elif by == "css":
                checkbox = self.driver.find_element(By.CSS_SELECTOR, identifier)
            elif by == "id":
                checkbox = self.driver.find_element(By.ID, identifier)
            elif by == "name":
                checkbox = self.driver.find_element(By.NAME, identifier)
            else:
                log_event(f"❌ Unsupported selector type: {by}")
                return False

            if not checkbox.is_selected():
                checkbox.click()
                log_event(f"✅ Checked checkbox: {identifier} ({by})")
            else:
                log_event(f"ℹ️ Checkbox already checked: {identifier} ({by})")
            time.sleep(1)
            return True
        except NoSuchElementException as e:
            log_event(f"⚠️ Failed to check checkbox")
            #log_event(f"⚠️ Failed to check checkbox: {identifier} ({by}) - {format_exception(e)}")
            return False

    def upload_file(self, identifier: str, file_path: str, by: str = "xpath"):
        try:
            if by == "xpath":
                upload_input = self.driver.find_element(By.XPATH, identifier)
            elif by == "css":
                upload_input = self.driver.find_element(By.CSS_SELECTOR, identifier)
            elif by == "id":
                upload_input = self.driver.find_element(By.ID, identifier)
            elif by == "name":
                upload_input = self.driver.find_element(By.NAME, identifier)
            else:
                log_event(f"❌ Unsupported selector type: {by}")
                return False

            file_path = os.path.abspath(file_path)
            upload_input.send_keys(file_path)
            log_event(f"✅ Uploaded file: {file_path} into {identifier} ({by})")
            time.sleep(2)
            return True
        except NoSuchElementException as e:
            log_event(f"⚠️ Failed to upload file")
            #log_event(f"⚠️ Failed to upload file: {identifier} ({by}) - {format_exception(e)}")
            return False

    def click(self, selector: str):
        """Direct click with JavaScript scrolling into view."""
        try:
            log_event(f"🖱️ Attempting click: {selector} (xpath)")
            element = self.driver.find_element(By.XPATH, selector)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.driver.execute_script("arguments[0].click();", element)
            log_event(f"✅ Clicked element: {selector} (xpath)")
        except Exception as e:
            log_event(f"⚠️ Failed to click element: {selector} (xpath) - {format_exception(e)}")
            try:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                log_event("🔍 Modal overlay detected, sent ESC key.")
            except:
                pass

    def perform(self, actions):
        """Performs list of actions received from Gemini."""
        # First try dismissing cookie modals if they exist
        try:
            modal = self.driver.find_element(By.XPATH, "//dialog[contains(@class, 'cookie')]")
            if modal.is_displayed():
                log_event("🍪 Cookie modal detected. Dismissing...")
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(1)
                buttons = modal.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "reject" in btn.text.lower() or "decline" in btn.text.lower():
                        btn.click()
                        log_event("✅ Cookie modal dismissed via Reject/Decline button.")
                        time.sleep(1)
                        break
        except Exception:
            log_event("ℹ️ No cookie modal or nothing to dismiss.")

        for action in actions:
            if self.detect_success_message():
                log_event("🎯 Application success detected mid-actions. Stopping further steps.")
                break

            action_type = action.get("type")
            selector = action.get("selector")
            text = action.get("text", None)
            option_text = action.get("option_text", None)
            file_path = action.get("file_path", None)

            if action_type == "click":
                self.click_element(selector)
            elif action_type == "type":
                if text:
                    self.type_text(selector, text)
            elif action_type == "select":
                if option_text:
                    self.select_dropdown(selector, option_text)
            elif action_type == "dynamic_select":
                if option_text:
                    self.select_dynamic_dropdown(selector, option_text)
            elif action_type == "check":
                self.check_checkbox(selector)
            elif action_type == "upload":
                if file_path:
                    self.upload_file(selector, file_path)
            else:
                log_event(f"⚠️ Unknown action type: {action_type}")

    def select_dynamic_dropdown(self, selector: str, option_text: str):
        """Handles dynamic dropdowns that need typing before selecting."""
        try:
            log_event(f"🔽 Attempting dynamic select: {selector} -> {option_text}")
            wait = WebDriverWait(self.driver, 10)
            input_field = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))

            self.driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
            input_field.click()
            input_field.clear()
            input_field.send_keys(option_text)
            time.sleep(1.5)

            if self.detect_success_message():
                log_event("✅ Success detected after typing in dynamic dropdown. Skipping Enter.")
                return True

            ActionChains(self.driver)\
                .move_to_element(input_field)\
                .pause(0.5)\
                .send_keys(Keys.ARROW_DOWN)\
                .pause(0.2)\
                .send_keys(Keys.ENTER)\
                .perform()

            log_event(f"✅ Selected dynamic dropdown option: {option_text}")
            time.sleep(1)
            return True
        except Exception as e:
            log_event(f"⚠️ Failed dynamic select: {selector} -> {option_text} - {format_exception(e)}")
            return False

    def detect_success_message(self):
        """Detects success message on the page after application submit."""
        try:
            success_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Thank you for applying')]")
            if success_element.is_displayed():
                log_event("🎯 Detected successful application!")
                return True
        except Exception:
            return False
