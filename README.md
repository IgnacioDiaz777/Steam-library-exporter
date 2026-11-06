# Exportador de biblioteca de Steam a TXT

Convierte toda tu biblioteca de Steam en una lista `.txt` ordenada de la A a la Z.
Pensado para que cualquiera pueda usarlo, incluso sin saber programar.

```
MI BIBLIOTECA DE STEAM (146 juegos)
==================================================

- A Plague Tale: Innocence
- Aeterna Noctis
- Alan Wake
- ...
```

## Requisitos

- [Python 3.8 o superior](https://www.python.org/downloads/) (en el instalador de Windows marca **"Add Python to PATH"**).
- Una **API key de Steam** (ver más abajo).
- Tu perfil de Steam y los **Detalles de los juegos** en **Público**.

## Instalación

1. Descarga este repositorio (botón verde **Code > Download ZIP**) y descomprímelo.
2. Abre una terminal dentro de la carpeta y ejecuta:

```
pip install -r requirements.txt
```

## Conseguir tu API key de Steam

1. Entra a <https://steamcommunity.com/dev/apikey> con tu cuenta.
2. En **Domain Name** escribe cualquier cosa (por ejemplo `localhost`).
3. Copia la key que te entrega Steam.

> Steam solo entrega API keys a cuentas que hayan gastado al menos 5 USD.
> La key es **personal**, como una contraseña: no la compartas ni la subas a internet.

## Poner tu perfil en público

En Steam: tu perfil > **Editar perfil** > **Ajustes de privacidad**.

- **Mi perfil:** Público
- **Detalles de los juegos:** Público

## Uso

Ejecuta el programa de cualquiera de estas formas:

- Doble clic sobre `exportador.py`.
- Desde VS Code, con el botón de "Play".
- Desde la terminal: `python exportador.py`.

El programa te pedirá dos cosas:

1. **Tu API key** (pégala con clic derecho o `Ctrl + V`).
2. **Tu perfil**: puedes pegar el link de tu perfil, tu nombre de perfil personalizado o tu SteamID64.

Al terminar crea `mi_biblioteca_steam.txt` en la **misma carpeta** que `exportador.py` y lo abre automáticamente.

## ¿Faltan juegos en la lista?

La API de Steam a veces no entrega algunos juegos gratuitos, demos o herramientas
(por ejemplo, juegos free-to-play que reclamaste pero nunca abriste). Es una limitación de Steam,
no del programa.

Para agregarlos a mano:

1. Copia `extras.example.txt` y renombra la copia como `extras.txt` (en la misma carpeta que `exportador.py`).
2. Escribe un juego por línea, tal como aparece en tu biblioteca. Las líneas que empiezan con `#` se ignoran.

```
Core Keeper (Demo)
Once Human
tModLoader
```

3. Vuelve a ejecutar el programa. Los juegos de `extras.txt` se suman a la lista (sin repetirse) y todo queda ordenado.

## Problemas comunes

| Mensaje | Qué hacer |
|---|---|
| `Steam rechazó tu API key` | La key está mal copiada o fue revocada. Genera una nueva en la página de API keys. |
| `No se encontraron juegos` | Tu perfil o los "Detalles de los juegos" siguen en privado. |
| `No encontré ese perfil` | Revisa el link o el nombre que pegaste. |
| `No pude conectarme a Steam` | Revisa tu conexión a internet. |
| `Falta la librería 'requests'` | Ejecuta `pip install -r requirements.txt`. |

## Privacidad y seguridad

- El programa **no guarda** tu API key ni tu perfil: se los pide cada vez que lo ejecutas.
- Tu API key solo se envía a la API oficial de Steam (`api.steampowered.com`).
- Si alguna vez publicas tu key por error (una captura, un commit), revócala y genera otra en la página de API keys.

## Licencia

[MIT](LICENSE): puedes usar, copiar y modificar este programa libremente.
