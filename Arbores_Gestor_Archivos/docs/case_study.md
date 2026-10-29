# Caso de estudio: organización jerárquica de archivos

## Problema real

Los usuarios necesitan clasificar información digital en directorios y subdirectorios para localizarla mediante rutas y relaciones de contención.

## Evidencia documental

Microsoft Learn describe explícitamente la relación padre-hijo entre directorios y llama *directory tree* a esa estructura jerárquica. La documentación de Debian explica que, en GNU/Linux, los archivos y directorios se organizan en un árbol que parte de `/`. El Filesystem Hierarchy Standard establece pautas para ubicar archivos y directorios en sistemas tipo Unix.

## Correspondencia con el árbol n-ario

Una carpeta puede contener múltiples carpetas y archivos; por tanto, un nodo puede tener más de dos hijos. Esto hace que un árbol n-ario sea una representación didáctica más natural que un árbol binario.

## Alcance y límites

El sistema construido es una simulación. No representa todos los detalles internos de NTFS, ext4 u otros sistemas de archivos. Por ejemplo, no modela bloques físicos, permisos, enlaces duros, enlaces simbólicos ni puntos de montaje.

## Fuentes

1. Microsoft Learn, About Directory Management: https://learn.microsoft.com/en-us/windows/win32/fileio/about-directory-management
2. Debian Reference, Unix-like filesystem: https://www.debian.org/doc/manuals/debian-reference/ch01.en.html
3. FreeDesktop, Filesystem Hierarchy Standard: https://specifications.freedesktop.org/fhs/latest-single/
