from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from ..connection import get_database
from ..models_rules import UIRule, RuleStatus

class UIRulesRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.ui_rules

    def get_all_rules(self, status: Optional[str] = None) -> List[UIRule]:
        """Recupera reglas, opcionalmente filtradas por estado."""
        query = {}
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query)
        return [UIRule(**doc) for doc in cursor]

    def get_active_rules(self) -> List[UIRule]:
        """Helper para obtener solo reglas activas (para el motor)."""
        return self.get_all_rules(status=RuleStatus.ACTIVE.value)

    def get_rule_by_id(self, rule_id: str) -> Optional[UIRule]:
        try:
            oid = ObjectId(rule_id)
        except Exception:
            return None
            
        doc = self.collection.find_one({"_id": oid})
        return UIRule(**doc) if doc else None
    
    def create_rule(self, rule: UIRule) -> str:
        """Crea una nueva regla (normalmente en DRAFT)."""
        rule_dict = rule.model_dump(by_alias=True, exclude={"id"})
        rule_dict["created_at"] = datetime.utcnow()
        rule_dict["updated_at"] = datetime.utcnow()
        result = self.collection.insert_one(rule_dict)
        return str(result.inserted_id)

    def update_rule(self, rule_id: str, updates: Dict) -> bool:
        """Actualiza campos de una regla."""
        try:
            oid = ObjectId(rule_id)
        except Exception:
            return False

        updates["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": oid},
            {"$set": updates}
        )
        return result.modified_count > 0

    def publish_version(self, rule_id: str) -> bool:
        """
        Activa una versión de regla. 
        Nota: Si hubiera versiones anteriores de la MISMA regla conceptual, 
        deberíamos archivarlas. Por ahora asumimos reglas independientes.
        """
        return self.update_rule(rule_id, {"status": RuleStatus.ACTIVE.value})

    def archive_rule(self, rule_id: str) -> bool:
        return self.update_rule(rule_id, {"status": RuleStatus.ARCHIVED.value})

    def get_rules_stats(self) -> Dict:
        """Retorna conteo de reglas por estado."""
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        stats = list(self.collection.aggregate(pipeline))
        return {item["_id"]: item["count"] for item in stats}

# Singleton
_repo = None
def get_ui_rules_repository():
    global _repo
    if not _repo:
        _repo = UIRulesRepository()
    return _repo
