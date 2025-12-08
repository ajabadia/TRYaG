import re
from typing import Dict, List, Any
from db.repositories.ui_rules_repository import get_ui_rules_repository, UIRulesRepository
from db.models_rules import UIRule, RuleCondition, RuleAction, LogicOperator, ConditionOperator, ActionType, RuleStatus

class DynamicRulesEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DynamicRulesEngine, cls).__new__(cls)
            cls._instance.repo = get_ui_rules_repository()
            cls._instance._ensure_migration()
        return cls._instance

    def _ensure_migration(self):
        """
        Migrates hardcoded rules to DB if collection is empty.
        """
        if self.repo.collection.count_documents({}) > 0:
            return

        print("🚀 Migrating Legacy Magic Cases to DB...")
        default_rules = self._get_default_rules()
        for rule in default_rules:
            self.repo.create_rule(rule)
            # Auto-publish for immediate availability in this pilot
            # We fetch it back to get the ID, or loop differently. 
            # Ideally create_rule returns ID.
            # For simplicity in this migration, let's just insert as ACTIVE.
        
        # Hack: Update all to ACTIVE directly after insertion for the migration
        self.repo.collection.update_many({}, {"$set": {"status": RuleStatus.ACTIVE.value}})
        print("✅ Migration Complete.")

        # 2. Seed Fields
        from services.field_discovery_service import get_cached_field_discovery
        from db.repositories.ui_fields_repository import get_ui_fields_repository
        
        fields_repo = get_ui_fields_repository()
        if fields_repo.collection.count_documents({}) == 0:
            print("🔍 Seeding UI Fields from Codebase...")
            count = get_cached_field_discovery()
            print(f"✅ Seeding Complete. {count} fields found.")


    def evaluate(self, patient_data: Dict[str, Any]) -> Dict[str, List[Any]]:
        """
        Evaluates active rules against patient data.
        """
        results = {
            "alerts": [],
            "highlights": [],
            "suggestions": []
        }

        active_rules = self.repo.get_active_rules()
        
        for rule in active_rules:
            if self._evaluate_condition(rule.conditions, patient_data):
                self._apply_actions(rule.actions, results)
                
        return results

    def _evaluate_condition(self, condition: RuleCondition, data: Dict[str, Any]) -> bool:
        """Recursive evaluation of conditions."""
        
        # 1. Base Case: Direct Rule (Field + Operator + Value)
        if condition.field:
            return self._check_rule(condition, data)
        
        # 2. Logic Group (AND/OR with nested rules)
        if condition.logic and condition.rules:
            results = [self._evaluate_condition(sub, data) for sub in condition.rules]
            
            if condition.logic == LogicOperator.AND:
                return all(results)
            elif condition.logic == LogicOperator.OR:
                return any(results)
                
        return False

    def _check_rule(self, condition: RuleCondition, data: Dict[str, Any]) -> bool:
        """Evaluates a single field comparison."""
        # 1. Extract value from data (supports dot notation e.g. 'vital_signs.temperature')
        current_val = data
        try:
            for part in condition.field.split('.'):
                if current_val is None: break
                current_val = current_val.get(part)
        except Exception:
            current_val = None

        if current_val is None:
            return False

        # 2. Compare using operator
        op = condition.operator
        target = condition.value
        
        # Normalize types for comparison (basic)
        try:
            if isinstance(target, (int, float)) and isinstance(current_val, (str)):
                current_val = float(current_val)
            if isinstance(current_val, (int, float)) and isinstance(target, (str)):
                target = float(target)
        except:
            pass # Keep original if conversion fails

        try:
            if op == ConditionOperator.EQUALS: return current_val == target
            if op == ConditionOperator.NOT_EQUALS: return current_val != target
            if op == ConditionOperator.GREATER_THAN: return current_val > target
            if op == ConditionOperator.LESS_THAN: return current_val < target
            if op == ConditionOperator.GREATER_EQUAL: return current_val >= target
            if op == ConditionOperator.LESS_EQUAL: return current_val <= target
            if op == ConditionOperator.CONTAINS: return str(target).lower() in str(current_val).lower()
            if op == ConditionOperator.NOT_CONTAINS: return str(target).lower() not in str(current_val).lower()
            if op == ConditionOperator.IN: return current_val in target # Target should be list
            if op == ConditionOperator.NOT_IN: return current_val not in target
        except Exception:
            return False
            
        return False

    def _apply_actions(self, actions: List[RuleAction], results: Dict):
        for action in actions:
            if action.type == ActionType.ALERT:
                results["alerts"].append({
                    "type": action.level,
                    "message": action.message
                })
            elif action.type == ActionType.HIGHLIGHT:
                if action.fields:
                    results["highlights"].extend(action.fields)
            elif action.type == ActionType.SUGGEST:
                if action.protocol:
                    results["suggestions"].append(action.protocol)

    def _get_default_rules(self) -> List[UIRule]:
        """Definitions for the initial migration."""
        rules = []

        # 1. Sepsis
        rules.append(UIRule(
            name="Protocolo Sepsis",
            description="Fiebre + Inestabilidad Hemodinámica",
            conditions=RuleCondition(
                logic=LogicOperator.AND,
                rules=[
                    RuleCondition(field="vital_signs.temperature", operator=ConditionOperator.GREATER_THAN, value=38.0),
                    RuleCondition(
                        logic=LogicOperator.OR,
                        rules=[
                            RuleCondition(field="vital_signs.heart_rate", operator=ConditionOperator.GREATER_THAN, value=100),
                            RuleCondition(field="vital_signs.systolic_bp", operator=ConditionOperator.LESS_THAN, value=90)
                        ]
                    )
                ]
            ),
            actions=[
                RuleAction(type=ActionType.ALERT, level="critical", message="🚨 ALERTA SEPSIS: Fiebre + Inestabilidad Hemodinámica."),
                RuleAction(type=ActionType.HIGHLIGHT, fields=["temperature", "heart_rate", "systolic_bp"]),
                RuleAction(type=ActionType.SUGGEST, protocol="qSOFA")
            ]
        ))

        # 2. Ictus (Simplified for migration strictness)
        # Old: any(w in motivo for w in keywords)
        stroke_keywords = ['habla', 'boca', 'fuerza', 'brazo', 'hormigueo', 'comisura']
        rules.append(UIRule(
            name="Código Ictus",
            description="Palabras clave neurológicas",
            conditions=RuleCondition(
                logic=LogicOperator.OR,
                rules=[RuleCondition(field="texto_medico", operator=ConditionOperator.CONTAINS, value=w) for w in stroke_keywords]
            ),
            actions=[
                RuleAction(type=ActionType.ALERT, level="warning", message="🧠 POSIBLE ICTUS: Síntomas neurológicos."),
                RuleAction(type=ActionType.SUGGEST, protocol="Escala Cincinnati")
            ]
        ))

        # 3. SCA (Cardio)
        sca_keywords = ['pecho', 'opresion', 'toracico', 'mandibula', 'corazon']
        rules.append(UIRule(
            name="Síndrome Coronario",
            description="Dolor torácico o síntomas cardiacos",
            conditions=RuleCondition(
                logic=LogicOperator.OR,
                rules=[RuleCondition(field="texto_medico", operator=ConditionOperator.CONTAINS, value=w) for w in sca_keywords]
            ),
            actions=[
                RuleAction(type=ActionType.HIGHLIGHT, fields=['systolic_bp', 'heart_rate']),
                RuleAction(type=ActionType.SUGGEST, protocol="Electrocardiograma (ECG)")
            ]
        ))

        # 4. Respiratorio
        resp_keywords = ['disnea', 'ahogo', 'aire', 'respirar', 'fatiga']
        # Logic: Keywords OR SpO2 < 92
        rules.append(UIRule(
            name="Insuficiencia Respiratoria",
            description="Disnea o Hipoxia",
            conditions=RuleCondition(
                logic=LogicOperator.OR,
                rules=[
                    *[RuleCondition(field="texto_medico", operator=ConditionOperator.CONTAINS, value=w) for w in resp_keywords],
                    RuleCondition(field="vital_signs.oxygen_saturation", operator=ConditionOperator.LESS_THAN, value=92)
                ]
            ),
            actions=[
                RuleAction(type=ActionType.ALERT, level="critical", message="🫁 ALERTA RESPIRATORIA / HIPOXIA."),
                RuleAction(type=ActionType.HIGHLIGHT, fields=['oxygen_saturation'])
            ]
        ))

        # 5. Pediatrico
        rules.append(UIRule(
            name="Paciente Pediátrico",
            description="Edad menor a 14 años",
            conditions=RuleCondition(field="edad", operator=ConditionOperator.LESS_THAN, value=14),
            actions=[
                RuleAction(type=ActionType.ALERT, level="info", message="👶 Protocolo Pediátrico Activo.")
            ]
        ))

        # 6. Geriátrico
        rules.append(UIRule(
            name="Paciente Geriátrico",
            description="Edad mayor a 75 años",
            conditions=RuleCondition(field="edad", operator=ConditionOperator.GREATER_THAN, value=75),
            actions=[
                RuleAction(type=ActionType.SUGGEST, protocol="Test Riesgo Caídas"),
                RuleAction(type=ActionType.ALERT, level="warning", message="👴 Valorar Fragilidad/Delirium.")
            ]
        ))

        return rules
