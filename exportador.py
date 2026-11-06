"""
EXPORTADOR DE BIBLIOTECA DE STEAM A TXT

Toma todos los juegos de tu cuenta de Steam y los guarda, ordenados de la A a la Z,
en un archivo llamado "mi_biblioteca_steam.txt" (en la misma carpeta que este script).

Antes de usarlo necesitas:
  1) Tener instalada la librería requests:  pip install requests
  2) Una API key de Steam:  https://steamcommunity.com/dev/apikey
  3) Tu perfil y los "Detalles de los juegos" en Público.

Más detalles en el archivo README.md
"""

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Falta la librería 'requests'. Instálala escribiendo esto en la terminal:\n")
    print("    pip install requests\n")
    input("Presiona Enter para salir...")
    sys.exit(1)


# ----------------------------------------------------------------------------
# Configuración (normalmente no necesitas cambiar nada aquí)
# ----------------------------------------------------------------------------
CARPETA = Path(__file__).resolve().parent
ARCHIVO_SALIDA = CARPETA / "mi_biblioteca_steam.txt"
ARCHIVO_EXTRAS = CARPETA / "extras.txt"  # opcional: juegos que la API no entrega

URL_JUEGOS = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
URL_VANITY = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"


class ErrorSteam(Exception):
    """Error con un mensaje pensado para mostrárselo directamente al usuario."""


# ----------------------------------------------------------------------------
# Paso 1 y 2: pedir los datos al usuario
# ----------------------------------------------------------------------------
def pedir_api_key():
    print("PASO 1 - Tu API key de Steam")
    print("  Si no tienes una, créala en: https://steamcommunity.com/dev/apikey")
    while True:
        clave = input("  Pégala aquí: ").strip().strip("\"'")
        if re.fullmatch(r"[0-9A-Fa-f]{32}", clave):
            return clave
        print("  Esa clave no parece válida (son 32 letras y números). Intenta de nuevo.\n")


def resolver_nombre_personalizado(nombre, api_key):
    """Convierte un nombre de perfil personalizado (ej: 'ignacioxd') en SteamID64."""
    try:
        r = requests.get(
            URL_VANITY,
            params={"key": api_key, "vanityurl": nombre},
            timeout=15,
        )
    except requests.exceptions.RequestException:
        raise ErrorSteam("No pude conectarme a Steam. Revisa tu conexión a internet.")

    if r.status_code in (401, 403):
        raise ErrorSteam("Steam rechazó tu API key. Revisa que esté bien copiada.")

    try:
        respuesta = r.json().get("response", {})
    except ValueError:
        return None

    if respuesta.get("success") == 1:
        return respuesta.get("steamid")
    return None


def pedir_steam_id(api_key):
    print("\nPASO 2 - Tu perfil de Steam")
    print("  Puedes pegar el link de tu perfil, tu nombre de perfil personalizado")
    print("  o tu SteamID64 (17 números que empiezan con 7656).")
    while True:
        texto = input("  Perfil: ").strip().strip("\"'")
        if not texto:
            continue

        # SteamID64 directo
        if re.fullmatch(r"7656\d{13}", texto):
            return texto

        # Link del tipo steamcommunity.com/profiles/<SteamID64>
        m = re.search(r"steamcommunity\.com/profiles/(7656\d{13})", texto)
        if m:
            return m.group(1)

        # Link del tipo steamcommunity.com/id/<nombre>  o simplemente el nombre
        m = re.search(r"steamcommunity\.com/id/([^/?#\s]+)", texto)
        nombre = m.group(1) if m else texto

        steam_id = resolver_nombre_personalizado(nombre, api_key)
        if steam_id:
            return steam_id
        print("  No encontré ese perfil. Revisa el link o el nombre e intenta de nuevo.\n")


# ----------------------------------------------------------------------------
# Paso 3: descargar y combinar juegos
# ----------------------------------------------------------------------------
def descargar_juegos(api_key, steam_id):
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
        "include_free_sub": True,
        "skip_unvetted_apps": False,
        "format": "json",
    }

    try:
        r = requests.get(URL_JUEGOS, params=params, timeout=20)
    except requests.exceptions.RequestException:
        raise ErrorSteam("No pude conectarme a Steam. Revisa tu conexión a internet.")

    if r.status_code in (401, 403):
        raise ErrorSteam(
            "Steam rechazó tu API key. Revisa que esté bien copiada "
            "o genera una nueva en https://steamcommunity.com/dev/apikey"
        )
    if r.status_code == 429:
        raise ErrorSteam("Hiciste demasiadas consultas seguidas. Espera unos minutos e intenta de nuevo.")
    if r.status_code != 200:
        raise ErrorSteam(f"Steam respondió con el código {r.status_code}. Intenta de nuevo en unos minutos.")

    try:
        data = r.json()
    except ValueError:
        raise ErrorSteam("Steam devolvió una respuesta inesperada. Intenta de nuevo en unos minutos.")

    juegos = data.get("response", {}).get("games", [])
    if not juegos:
        raise ErrorSteam(
            "No se encontraron juegos. Revisa que tu perfil y los 'Detalles de los juegos' estén en Público:\n"
            "  Steam > tu perfil > Editar perfil > Ajustes de privacidad."
        )

    return [j.get("name") or f"Juego sin nombre (ID {j.get('appid')})" for j in juegos]


def leer_extras():
    """Lee extras.txt (si existe): un juego por línea, las líneas con # se ignoran."""
    if not ARCHIVO_EXTRAS.exists():
        return []
    extras = []
    for linea in ARCHIVO_EXTRAS.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            extras.append(linea)
    return extras


def combinar(nombres_api, extras):
    """Une la lista de Steam con los extras (sin repetir) y ordena de la A a la Z."""
    existentes = {n.lower() for n in nombres_api}
    agregados = []
    for extra in extras:
        if extra.lower() not in existentes:
            agregados.append(extra)
            existentes.add(extra.lower())
    return sorted(nombres_api + agregados, key=str.lower), len(agregados)


# ----------------------------------------------------------------------------
# Paso 4: guardar el archivo
# ----------------------------------------------------------------------------
def guardar(nombres):
    try:
        with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as archivo:
            archivo.write(f"MI BIBLIOTECA DE STEAM ({len(nombres)} juegos)\n")
            archivo.write("=" * 50 + "\n\n")
            for nombre in nombres:
                archivo.write(f"- {nombre}\n")
    except OSError as e:
        raise ErrorSteam(
            f"No pude guardar el archivo en {ARCHIVO_SALIDA}.\n"
            f"  Motivo: {e}\n"
            "  Si lo tienes abierto en otro programa, ciérralo e intenta de nuevo."
        )


def abrir_archivo():
    try:
        if sys.platform.startswith("win"):
            os.startfile(ARCHIVO_SALIDA)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(ARCHIVO_SALIDA)])
        else:
            subprocess.run(["xdg-open", str(ARCHIVO_SALIDA)])
    except Exception:
        pass  # si no se puede abrir solo, no pasa nada: el archivo ya está guardado


# ----------------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------------
def main():
    print("=" * 50)
    print("  EXPORTADOR DE BIBLIOTECA DE STEAM A TXT")
    print("=" * 50 + "\n")

    try:
        api_key = pedir_api_key()
        steam_id = pedir_steam_id(api_key)

        print("\nDescargando tu biblioteca...")
        nombres_api = descargar_juegos(api_key, steam_id)
        nombres, n_extras = combinar(nombres_api, leer_extras())
        guardar(nombres)

    except ErrorSteam as e:
        print(f"\nERROR: {e}")
    except KeyboardInterrupt:
        print("\nCancelado.")
    else:
        print(f"\nListo. Se guardaron {len(nombres)} juegos.")
        if n_extras:
            print(f"({len(nombres_api)} de Steam + {n_extras} de tu archivo extras.txt)")
        print(f"Archivo: {ARCHIVO_SALIDA}")
        abrir_archivo()

    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
