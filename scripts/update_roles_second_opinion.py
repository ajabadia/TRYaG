
import sys
import os

# Add src to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from db.repositories.roles import get_roles_repository
    print("✅ Módulos importados correctamente.")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

def update_roles():
    repo = get_roles_repository()
    
    # Roles a actualizar
    targets = {
        "superadministrador": {"view": True, "create": True},
        "administrador": {"view": True, "create": True},
        "auditor": {"view": True, "create": False},
        "usuario": {"view": True, "create": True}
    }
    
    print("\n🔄 Iniciando actualización de roles...")
    
    for role_code, perms in targets.items():
        role = repo.get_role_by_code(role_code)
        if role:
            print(f"   - Actualizando rol: {role['nombre']} ({role_code})")
            
            # Update local dict permissions
            current_perms = role.get("permissions", {})
            current_perms["segunda_opinion"] = perms
            
            # Persist to DB
            success = repo.update_role(role_code, {"permissions": current_perms})
            
            if success:
                print(f"     ✅ Permisos 'segunda_opinion' añadidos.")
            else:
                print(f"     ⚠️ No se detectaron cambios (ya estaba actualizado).")
        else:
            print(f"   ⚠️ Rol no encontrado: {role_code}")

    print("\n✅ Proceso finalizado.")

if __name__ == "__main__":
    update_roles()
