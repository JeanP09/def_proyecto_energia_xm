import subprocess

scripts = [
    "migration/d_migration_Recursos.py",
    "migration/d_migration_DemaSIN.py",
    "migration/d_migration_DR_DC_G.py",
    "migration/d_migration_CapEfecNeta.py"
]

for script in scripts:
    print(f"Ejecutando {script}...")
    subprocess.run(["python", script], check=True)

print("✅ Todos los scripts de migración se han ejecutado.")
