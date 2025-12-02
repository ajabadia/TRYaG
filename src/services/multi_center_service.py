# path: src/services/multi_center_service.py
"""
Servicio para la gestión y agregación de datos multi-centro.
Permite obtener métricas consolidadas de todos los centros registrados en el sistema.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from db.connection import get_database

class MultiCenterService:
    def __init__(self):
        self.db = get_database()

    def get_available_centers(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de centros activos desde la colección 'centros'.
        Si no hay centros, devuelve una lista vacía o datos de fallback si es necesario.
        """
        try:
            centros = list(self.db.centros.find({"activo": True}, {"_id": 0}))
            if not centros:
                # Fallback para desarrollo si no hay centros configurados
                return []
            return centros
        except Exception as e:
            print(f"Error obteniendo centros: {e}")
            return []

    def get_global_kpis(self, center_ids: List[str] = None) -> Dict[str, Any]:
        """
        Calcula KPIs globales agregando datos de los centros seleccionados.
        """
        match_query = {}
        if center_ids:
            match_query["centro_id"] = {"$in": center_ids}

        # 1. Total Pacientes Activos (en flujo)
        # Estados activos: EN_ADMISION, EN_ESPERA_TRIAJE, EN_TRIAJE, DERIVADO, EN_ATENCION
        active_states = ["EN_ADMISION", "EN_ESPERA_TRIAJE", "EN_TRIAJE", "DERIVADO", "EN_ATENCION"]
        
        # Construir query para patient_flow
        flow_query = {"estado": {"$in": active_states}}
        if center_ids:
            flow_query["centro_id"] = {"$in": center_ids}
            
        total_patients = self.db.patient_flow.count_documents(flow_query)

        # 2. Salas Activas
        room_query = {"activa": True}
        if center_ids:
            room_query["centro_id"] = {"$in": center_ids}
        total_rooms = self.db.salas.count_documents(room_query)

        # 3. Tiempo de Espera Promedio (últimas 24h)
        # Usamos triage_records para esto
        yesterday = datetime.now() - timedelta(hours=24)
        triage_query = {
            "timestamp": {"$gte": yesterday}
        }
        # Nota: triage_records podría no tener centro_id directo si no se migró, 
        # asumimos que se puede filtrar o que es global por ahora.
        # Si triage_records tiene centro_id:
        if center_ids:
             triage_query["centro_id"] = {"$in": center_ids}

        # Pipeline de agregación para tiempo de espera
        pipeline = [
            {"$match": triage_query},
            {"$group": {
                "_id": None,
                "avg_wait": {"$avg": "$wait_time_minutes"}
            }}
        ]
        
        try:
            result = list(self.db.triage_records.aggregate(pipeline))
            avg_wait = result[0]['avg_wait'] if result else 0
        except:
            avg_wait = 0

        # 4. Personal Activo (Usuarios con rol != admin)
        staff_query = {"role": {"$ne": "admin"}}
        if center_ids:
            staff_query["centro_id"] = {"$in": center_ids}
        total_staff = self.db.users.count_documents(staff_query)

        return {
            "total_pacientes": total_patients,
            "total_salas": total_rooms,
            "avg_wait_time": round(avg_wait, 1) if avg_wait else 0,
            "total_staff": total_staff
        }

    def get_center_metrics(self, center_id: str) -> Dict[str, Any]:
        """
        Obtiene métricas específicas para un centro.
        """
        # Pacientes activos
        active_patients = self.db.patient_flow.count_documents({
            "centro_id": center_id,
            "estado": {"$in": ["EN_ADMISION", "EN_ESPERA_TRIAJE", "EN_TRIAJE", "DERIVADO", "EN_ATENCION"]}
        })

        # Ocupación (Pacientes / Capacidad Salas)
        # Primero obtener capacidad total
        salas = list(self.db.salas.find({"centro_id": center_id, "activa": True}))
        total_capacity = sum(s.get('capacidad', 1) for s in salas)
        
        occupancy = (active_patients / total_capacity * 100) if total_capacity > 0 else 0

        # Tiempo espera promedio (simulado/calculado)
        # Aquí podríamos hacer una query real similar a get_global_kpis
        
        return {
            "pacientes_activos": active_patients,
            "ocupacion": round(occupancy, 1),
            "capacidad_total": total_capacity
        }

# Instancia global
_multi_center_service = MultiCenterService()

def get_multi_center_service():
    return _multi_center_service
