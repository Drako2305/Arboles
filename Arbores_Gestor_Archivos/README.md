# Arboles — Gestor jerárquico de archivos

Proyecto académico de Estructuras de Datos. Simula un explorador de archivos mediante un árbol n-ario implementado manualmente en Python.

## 1. Caso de estudio

Los sistemas de archivos organizan directorios y archivos jerárquicamente. Microsoft documenta la relación padre-hijo entre directorios y denomina a esta organización *directory tree*. Debian describe la jerarquía de archivos y directorios de GNU/Linux partiendo de una raíz `/`.

Esta aplicación es una **simulación educativa**: no accede, modifica ni elimina archivos reales del computador.

Fuentes:
- Microsoft Learn: https://learn.microsoft.com/en-us/windows/win32/fileio/about-directory-management
- Debian Reference: https://www.debian.org/doc/manuals/debian-reference/ch01.en.html
- Filesystem Hierarchy Standard: https://specifications.freedesktop.org/fhs/latest-single/

## 2. Tecnologías

- Python 3.10 o superior
- Flask
- HTML5, CSS3 y JavaScript
- JSON para persistencia
- unittest para pruebas

## 3. Instalación en Windows y Visual Studio Code

Abre la carpeta del proyecto en Visual Studio Code y ejecuta en la terminal:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Abre en el navegador:

http://127.0.0.1:5000

Para detener el servidor, vuelve a la terminal y presiona `Ctrl + C`.

## 4. Ejecutar pruebas

Con el entorno virtual activado:

```powershell
python -m unittest discover -s tests -v
```

## 5. Estructura

- `app.py`: crea la aplicación Flask y define los endpoints.
- `src/models/tree_node.py`: representa cada nodo.
- `src/structures/nary_tree.py`: implementa el árbol n-ario y sus algoritmos.
- `src/services/file_service.py`: coordina operaciones, datos de ejemplo y persistencia.
- `templates/index.html`: estructura de la interfaz.
- `static/css/style.css`: estilos.
- `static/js/api.js`: comunicación HTTP con Flask.
- `static/js/app.js`: interacción y renderizado del explorador.
- `tests/`: pruebas unitarias y de API.
- `data/tree.json`: persistencia local.

## 6. Estructura de datos

Cada nodo contiene identificador, nombre, tipo, referencia al padre y lista de hijos. Las carpetas pueden tener cero o más hijos. Los archivos no pueden tener hijos.

El árbol tiene una raíz única. El sistema impide mover un nodo dentro de sí mismo o de uno de sus descendientes para evitar ciclos.

## 7. Conceptos académicos

- **Raíz:** nodo inicial `Mi unidad`.
- **Padre:** carpeta que contiene directamente otro nodo.
- **Hijo:** elemento contenido directamente en una carpeta.
- **Hermanos:** nodos que comparten el mismo padre.
- **Hoja:** nodo sin hijos. En el modelo, todo archivo es hoja; una carpeta vacía también es hoja.
- **Rama:** nodo que tiene uno o más hijos y no es la raíz.
- **Nivel:** distancia desde la raíz, contando la raíz como nivel 1.
- **Altura:** cantidad de niveles del camino más largo desde la raíz hasta una hoja. Una raíz sin hijos tiene altura 1.
- **Peso:** cantidad total de nodos, incluyendo raíz y hojas.
- **Grado de un nodo:** número de hijos directos.
- **Grado máximo:** mayor grado entre todos los nodos.
- **Orden:** para este árbol n-ario, el máximo número de hijos permitido por nodo. La implementación no fija un límite, por lo que se considera no acotado por una constante de diseño.

## 8. Algoritmos y complejidad

Sea `n` el número de nodos y `h` la altura del árbol:

| Operación | Complejidad | Motivo |
|---|---:|---|
| DFS | O(n) | Puede visitar todos los nodos |
| BFS | O(n) | Visita cada nodo una vez |
| Búsqueda por ID | O(n) | Recorre los nodos en el peor caso |
| Peso | O(n) | Cuenta todos los nodos |
| Altura | O(n) | Procesa cada nodo una vez |
| Nivel de nodo | O(h) | Sigue referencias hacia los padres |
| Grado de nodo | O(1) | Consulta la longitud de su lista de hijos |
| Grado máximo | O(n) | Examina todos los nodos |
| Insertar | O(n) | La búsqueda del padre es lineal |
| Eliminar | O(n) | Busca el nodo; quitarlo de la lista depende del número de hermanos |

DFS utiliza una pila explícita. BFS utiliza una cola (`deque`).

## 9. API principal

- `GET /api/tree`: estructura completa.
- `GET /api/stats`: estadísticas.
- `GET /api/node/<id>`: detalle de un nodo.
- `POST /api/nodes`: crear carpeta o archivo.
- `PATCH /api/nodes/<id>`: renombrar.
- `DELETE /api/nodes/<id>`: eliminar un nodo y su subárbol.
- `POST /api/nodes/<id>/move`: mover.
- `GET /api/search?q=texto`: buscar.
- `GET /api/traversal/dfs`: recorrido en profundidad.
- `GET /api/traversal/bfs`: recorrido en anchura.
- `POST /api/reset`: restaurar datos de demostración.

## 10. Persistencia

El árbol se serializa recursivamente a JSON. Cada objeto contiene sus datos y una lista `children`. Al iniciar, el servicio reconstruye los objetos `TreeNode` y restablece las referencias a sus padres.

## 11. Limitaciones

Esta es una simulación en memoria persistida en JSON, no implementa permisos, enlaces simbólicos, montaje de volúmenes, bloques de disco ni concurrencia de un sistema operativo real. La visualización web presenta el árbol como una jerarquía expandible.

## 12. Git

```bash
git init
git add .
git commit -m "Initial commit: N-ary tree file manager"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

Reemplaza la URL de ejemplo por la dirección de tu repositorio.

## 13. Guion breve para explicar el proyecto

1. El problema: organizar elementos en una jerarquía.
2. La solución: representar carpetas y archivos con un árbol n-ario.
3. La implementación: cada nodo mantiene su padre y sus hijos.
4. Las operaciones: insertar, buscar, mover, renombrar y eliminar.
5. Los recorridos: DFS usa una pila; BFS usa una cola.
6. Las métricas: altura, peso, nivel y grado se calculan recorriendo o consultando nodos.
7. La interfaz: permite operar sobre la estructura mediante solicitudes a Flask.
