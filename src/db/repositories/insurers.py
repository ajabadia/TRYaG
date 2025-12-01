import os
from bson.objectid import ObjectId
from datetime import datetime
from db.connection import get_database

class InsurersRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["insurers"]

    def get_all(self, active_only=False):
        """Obtiene todas las aseguradoras."""
        query = {}
        if active_only:
            query["active"] = True
        return list(self.collection.find(query).sort("name", 1))

    def get_by_id(self, insurer_id):
        """Obtiene una aseguradora por ID."""
        try:
            return self.collection.find_one({"_id": ObjectId(insurer_id)})
        except:
            return None

    def create(self, data):
        """Crea una nueva aseguradora."""
        data["created_at"] = datetime.utcnow()
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def update(self, insurer_id, data):
        """Actualiza una aseguradora existente."""
        data["updated_at"] = datetime.utcnow()
        self.collection.update_one(
            {"_id": ObjectId(insurer_id)},
            {"$set": data}
        )
        return True

    def delete(self, insurer_id):
        """Elimina (o desactiva) una aseguradora."""
        # Por seguridad, mejor desactivar que borrar físicamente si hay referencias,
        # pero para este CRUD simple permitimos borrar.
        self.collection.delete_one({"_id": ObjectId(insurer_id)})
        return True

    def search_by_name(self, query):
        """Busca aseguradoras por nombre."""
        return list(self.collection.find(
            {"name": {"$regex": query, "$options": "i"}}
        ).sort("name", 1))

    def seed_defaults(self):
        """Inserta datos iniciales si la colección está vacía."""
        if self.collection.count_documents({}) == 0:
            import random
            
            defaults = [
                # Aseguradoras Principales
                {"name": "Mapfre", "active": True, "is_admitted": True, "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Mapfre_logo.svg/1200px-Mapfre_logo.svg.png"},
                {"name": "Sanitas", "active": True, "is_admitted": True, "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Sanitas_Logo.svg/2560px-Sanitas_Logo.svg.png"},
                {"name": "Adeslas", "active": True, "is_admitted": True, "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Logo_Adeslas.svg/1200px-Logo_Adeslas.svg.png"},
                {"name": "DKV", "active": True, "is_admitted": True, "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/DKV_Seguros_Logo.svg/1200px-DKV_Seguros_Logo.svg.png"},
                {"name": "Asisa", "active": True, "is_admitted": True, "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Asisa_logo.svg/1200px-Asisa_logo.svg.png"},
                {"name": "AXA", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/AXA_Logo.svg/1200px-AXA_Logo.svg.png"},
                {"name": "Caser", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Caser_Seguros_logo.svg/1200px-Caser_Seguros_logo.svg.png"},
                {"name": "Allianz", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Allianz_logo.svg/1200px-Allianz_logo.svg.png"},
                {"name": "Generali", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Generali_logo.svg/1200px-Generali_logo.svg.png"},
                {"name": "Fiatc", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Logo_FIATC.svg/1200px-Logo_FIATC.svg.png"},
                {"name": "Cigna", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Cigna_logo.svg/1200px-Cigna_logo.svg.png"},
                {"name": "Aegon", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": False, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Aegon_logo.svg/1200px-Aegon_logo.svg.png"},
                {"name": "Divina Pastora", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Logo_Divina_Pastora_Seguros.svg/1200px-Logo_Divina_Pastora_Seguros.svg.png"},
                {"name": "Antares", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": False, "logo_url": ""},
                {"name": "Asefa", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": True, "is_mutual": False, "logo_url": ""},
                
                # Mutuas de Accidentes
                {"name": "Asepeyo", "active": True, "is_admitted": True, "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Asepeyo_logo.svg/1200px-Asepeyo_logo.svg.png"},
                {"name": "Fremap", "active": True, "is_admitted": True, "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Logotipo_Fremap.svg/1200px-Logotipo_Fremap.svg.png"},
                {"name": "Mutua Universal", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Mutua_Universal_logo.svg/1200px-Mutua_Universal_logo.svg.png"},
                {"name": "MC Mutual", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/MC_MUTUAL_logo.svg/1200px-MC_MUTUAL_logo.svg.png"},
                {"name": "Fraternidad-Muprespa", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Fraternidad-Muprespa_logo.svg/1200px-Fraternidad-Muprespa_logo.svg.png"},
                {"name": "Solimat", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": False, "is_mutual": True, "logo_url": ""},
                {"name": "Ibermutua", "active": True, "is_admitted": random.choice([True, False]), "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Ibermutua_logo.svg/1200px-Ibermutua_logo.svg.png"},
                
                # Mutualidades Públicas/Funcionarios
                {"name": "MUFACE", "active": True, "is_admitted": True, "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Logotipo_de_MUFACE.svg/1200px-Logotipo_de_MUFACE.svg.png"},
                {"name": "ISFAS", "active": True, "is_admitted": True, "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Emblema_del_ISFAS.svg/1200px-Emblema_del_ISFAS.svg.png"},
                {"name": "MUGEJU", "active": True, "is_admitted": True, "is_insurer": False, "is_mutual": True, "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Logotipo_de_MUGEJU.svg/1200px-Logotipo_de_MUGEJU.svg.png"}
            ]
            self.collection.insert_many(defaults)

def get_insurers_repository():
    return InsurersRepository()
