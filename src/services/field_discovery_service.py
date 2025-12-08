import ast
import os
import re
from typing import List, Dict, Set
import streamlit as st
from db.repositories.ui_fields_repository import get_ui_fields_repository
from db.models_rules import UIField

class FieldDiscoveryService:
    def __init__(self, root_dir: str = "src"):
        self.root_dir = root_dir
        self.repo = get_ui_fields_repository()
        self.ignored_dirs = {'__pycache__', '.git', 'venv', 'env', '.gemini'}

    def scan_and_register_fields(self):
        """
        Scans all python files in root_dir for Streamlit input calls.
        Extracts key, label, help, and persists them.
        Handles deprecation of fields no longer found.
        """
        print("🔍 Starting Field Discovery Scan...")
        
        # 1. Get existing fields to track deprecation
        existing_fields = {f.internal_name for f in self.repo.get_all_fields()}
        found_fields: Dict[str, UIField] = {}

        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            # Ignore specific dirs
            dirnames[:] = [d for d in dirnames if d not in self.ignored_dirs]

            for filename in filenames:
                if filename.endswith(".py"):
                    full_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(full_path, start=os.getcwd()) # Store relative path
                    self._process_file(full_path, rel_path, found_fields)

        # 2. Bulk upsert found fields (Active)
        count_new_updated = 0
        for internal_name, field_obj in found_fields.items():
            field_obj.status = "active" # Ensure active
            self.repo.upsert_field(field_obj)
            count_new_updated += 1
            
        # 3. Handle Deprecation
        # Fields in DB but not in Found
        missing_fields = existing_fields - set(found_fields.keys())
        count_deprecated = 0
        for missing_name in missing_fields:
            self.repo.update_field_status(missing_name, "deprecated")
            count_deprecated += 1
        
        print(f"✅ Field Discovery Complete. {count_new_updated} Active/Updated. {count_deprecated} Deprecated.")
        return count_new_updated

    def _process_file(self, filepath: str, rel_path: str, found_fields: Dict[str, UIField]):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception as e:
            print(f"⚠️ Error parsing {filepath}: {e}")
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self._analyze_call_node(node, rel_path, found_fields)

    def _analyze_call_node(self, node: ast.Call, rel_path: str, found_fields: Dict[str, UIField]):
        # Check if it's a streamlit input call (st.text_input, st.number_input, etc.)
        # Structure is usually Attribute(value=Name(id='st'), attr='text_input')
        
        func_name = self._get_func_name(node)
        if not func_name:
            return

        # Simple filter for common streamlit input widgets
        st_widgets = {
            'st.text_input', 'st.number_input', 'st.checkbox', 'st.radio', 
            'st.selectbox', 'st.multiselect', 'st.slider', 'st.date_input', 
            'st.time_input', 'st.text_area'
        }

        if func_name in st_widgets:
            # Extract arguments
            kwargs = {kw.arg: kw.value for kw in node.keywords}
            args = node.args

            # Attempt to extract 'key' (internal_name)
            key_val = self._extract_value(kwargs.get('key'))
            
            # If no explicit key, we skip (Liquid UI relies on explicit keys for state/binding)
            if not key_val or not isinstance(key_val, str):
                return 

            # Attempt to extract 'label' (display_name)
            # Label is usually the first arg or 'label' kwarg
            label_val = None
            if 'label' in kwargs:
                label_val = self._extract_value(kwargs.get('label'))
            elif len(args) > 0:
                label_val = self._extract_value(args[0])
            
            # Attempt to extract 'help'
            help_val = self._extract_value(kwargs.get('help'))

            # Infer data type from function name
            dtype = "text"
            if "number" in func_name: dtype = "number"
            elif "checkbox" in func_name: dtype = "boolean"
            elif "date" in func_name or "time" in func_name: dtype = "datetime"
            
            # Construct or Update UIField
            if key_val in found_fields:
                # Merge modules
                if rel_path not in found_fields[key_val].modules:
                    found_fields[key_val].modules.append(rel_path)
            else:
                found_fields[key_val] = UIField(
                    internal_name=key_val,
                    display_name={'es': str(label_val)} if label_val else {},
                    help_text={'es': str(help_val)} if help_val else {},
                    modules=[rel_path],
                    data_type=dtype
                )

    def _get_func_name(self, node: ast.Call) -> str:
        """Helper to get function name like 'st.text_input'."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
        return ""

    def _extract_value(self, node):
        """Extract literal value from AST node."""
        if node is None:
            return None
        if isinstance(node, ast.Constant): # Python 3.8+
            return node.value
        if isinstance(node, ast.Str): # Older Python
            return node.s
        if isinstance(node, ast.Num):
            return node.n
        # Complex types (f-strings, variables) are hard to static parse perfectly.
        # We return None or specific placeholder?
        # For now, simplistic approach: ignore dynamic labels
        return None

# Singleton with Cache
@st.cache_data(ttl=3600, show_spinner=False)
def get_cached_field_discovery():
    """Run discovery once per hour/session start."""
    service = FieldDiscoveryService()
    count = service.scan_and_register_fields()
    return count

def get_field_discovery_service():
    return FieldDiscoveryService()
