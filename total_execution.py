import os
import time
import subprocess

def run_command(command):
    """Ejecuta un comando en el shell."""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error al ejecutar el comando: {command}")
            print(stderr.decode())
        else:
            print(stdout.decode())
    except Exception as e:
        print(f"Hubo un error al ejecutar el comando: {str(e)}")

def main():
    #Ejecuta comando para iniciar el proyecto
    print("Ejecutando 'docker-compose up -d'...")
    run_command("docker-compose up -d")

    #Tiempo de espera 10s
    print("Esperando 10 segundos...")
    time.sleep(10)

    #Instala las dependencias del archivo requirements.txt
    print("Instalando las dependencias de requirements.txt...")
    run_command("python -m pip install -r requirements.txt")

if __name__ == "__main__":
    main()
