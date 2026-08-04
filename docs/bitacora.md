# Bitácora del proceso — Lab 1B ETL

## EDA de las fuentes de ventas

Se hizo un análisis exploratorio sobre las tres fuentes de ventas por
separado (Cali, Bogotá, Medellín), cada una en su formato y con sus propios
nombres de columna, sin renombrar ni transformar nada todavía. La idea era
confirmar con evidencia qué problemas de calidad tiene cada fuente antes de
decidir cómo limpiarlos. En cada una se revisó la forma del archivo, los
tipos de dato, los nulos, los valores inválidos en cantidad y precio, los
duplicados en el identificador de venta, los valores distintos en el medio
de pago, y la validez del formato de fecha.

En Cali (CSV, 241 filas) los campos de cantidad y precio ya vienen numéricos.
Se encontró un registro con cantidad en 0 (línea L00011), un duplicado exacto
(línea L00167, repetida dos veces con los mismos valores) y una
inconsistencia de texto en el medio de pago, con el valor `' card '` escrito
con espacios y en minúscula, distinto del valor estándar `'Card'`. No hubo
precios inválidos ni fechas mal formadas. Los 228 valores faltantes en el
código de promoción se consideran normales, ya que la mayoría de las ventas
no tiene promoción aplicada.

En Bogotá (JSON, 281 filas, columnas en español) se encontró un registro con
cantidad negativa (línea L00261, unidades = -1) y un registro con precio no
numérico (línea L00311, precio = "$220000", con el símbolo de moneda incluido
como texto). También apareció un duplicado exacto (línea L00294) y una
inconsistencia de texto en el medio de pago, con el valor `'CASH'` en
mayúsculas frente al estándar `'Cash'`. Las fechas no presentaron problemas,
y los faltantes en el código de promoción siguen el mismo patrón que en Cali.

En Medellín (XML, 241 filas) se encontró un registro con precio negativo
(línea L00551, unit_value = -86000), un duplicado exacto (línea L00602) y una
fecha inválida (línea L00601, con valor 31-04-2026, que no existe porque
abril no tiene día 31). El medio de pago no presentó inconsistencias en esta
fuente. Un detalle particular es que el código de promoción faltante no
aparece como nulo al cargar el XML, sino como texto vacío, por la forma en
que se leen las etiquetas sin contenido. Se confirmó que corresponde a la
misma cantidad de casos que en las otras fuentes (228), solo que representado
de otra forma.

Los resultados se guardaron en tablas individuales dentro de
docs/eda_outputs/tablas, y en una gráfica de barras con los totales por tipo
de problema en docs/eda_outputs/graficas. Estos hallazgos son escenciales para
continuar con el proceso de limpieza.

## Extract

Se implementaron las funciones de extracción para las tres fuentes de ventas
y las cuatro tablas de referencia. La función para CSV se reutiliza tanto
para Cali como para products, stores, promotions y monthly_targets, ya que
en todos los casos es una lectura simple sin lógica adicional. Se usa la
codificación utf-8-sig porque los archivos traen una marca invisible al
inicio que, de no manejarse, deja mal leído el nombre de la primera columna.

Las tres funciones de ventas devuelven el mismo esquema de columnas
(sale_line_id, sale_date, store_id, product_id, quantity, unit_price,
promotion_code, payment_method). El renombrado de columnas se maneja como un
cambio de nombre, no como limpieza de datos: los valores quedan intactos, con
las fechas todavía en el formato original de cada sucursal y los números tal
como vienen en la fuente.

Se verificó que las tres funciones devuelven las mismas columnas en el mismo
orden, y que los tamaños coinciden con los encontrados en el análisis
exploratorio, con 241, 281 y 241 filas respectivamente. Las funciones de
extracción se guardaron en src/extract.py.

## Profile

Se implementó el perfilado sobre las tres fuentes ya extraídas y combinadas
en un solo conjunto, agregando una columna de origen para poder rastrear de
qué sucursal viene cada fila. Al tener ya un esquema común desde la
extracción, combinar las tres fuentes no requiere renombrar nada en este
paso.

El diagnóstico calcula el número de filas y columnas, los registros sin
código de promoción, las cantidades y precios inválidos, los duplicados de
sale_line_id, los valores distintos en el medio de pago, y las fechas
inválidas, parseando cada fila según el formato correspondiente a su
sucursal de origen. Para el conteo de registros sin promoción se suman tanto
los valores nulos como los textos vacíos, ya que cada fuente representa la
ausencia de promoción de forma distinta.

Los resultados del diagnóstico combinado coinciden con los encontrados por
separado en el análisis exploratorio: 763 filas en total, 717 ventas sin
promoción, 2 cantidades inválidas, 2 precios inválidos, 3 duplicados, 5
valores distintos en el medio de pago y 1 fecha inválida. La tabla resumen
se guardó en docs/profile_outputs/profile_resumen.csv, y el código en
src/profile.py.

## Profile de las tablas de referencia

Se perfilaron también las cuatro tablas de referencia (products, stores,
promotions y monthly_targets) antes de construir los cruces de la
transformación. Se hizo de manera preventiva, para tener un panorama
completo de los datos antes de cruzarlos: si alguna de estas tablas tuviera
un problema sin detectar, dañaría el cruce en la siguiente etapa sin que
apareciera ningún error visible, solo columnas con valores nulos.

Las cuatro tablas resultaron limpias, sin filas duplicadas, sin celdas
vacías, y con las columnas de identificador de longitud consistente en todos
sus valores, sin espacios ni inconsistencias de mayúsculas. Los resultados
se guardaron en docs/profile_outputs/profile_tablas_referencia.csv, y el
detalle columna por columna en docs/eda_outputs/perfiles.

## Clean y armonización

Antes de definir las reglas se revisó si los identificadores tenían alguna
inconsistencia de formato, algo que no se había mirado en el análisis
exploratorio inicial. Se encontró un store_id en minúscula ('s02', línea
L00301) y un product_id con espacios (' P005 ', línea L00056), que de no
corregirse quedarían sin nombre de producto o de tienda al momento de
cruzar con las tablas de referencia.

Las reglas aplicadas fueron: estandarizar los valores de identificador a
mayúsculas y sin espacios, recortar espacios y unificar el formato de texto
en el medio de pago, parsear las fechas al formato correspondiente de cada
sucursal usando la columna de origen como referencia, convertir cantidad y
precio a valores numéricos, eliminar los registros duplicados de
sale_line_id conservando la primera ocurrencia, rechazar los registros con
fecha inválida o con cantidad o precio menor o igual a cero, y unificar la
representación de las promociones faltantes a un solo valor nulo. Esta
última regla cubre tanto los textos vacíos como marcadores literales del
tipo "N/A", que también aparecen en los datos y de otra forma quedarían
tratados como si fueran un código de promoción real.

La conversión de precio a numérico se hace antes de evaluar su validez. Por
ese orden, el registro de Bogotá con precio "$220000" se recupera como un
valor válido de 220000 en lugar de descartarse, ya que el problema era de
formato y no un valor negativo o en cero.

Después de aplicar las reglas el conjunto pasó de 763 a 756 filas. Se
rechazaron 4 registros por invalidez real (L00011 y L00261 por cantidad
inválida, L00551 por precio negativo, L00601 por fecha inexistente) y se
eliminaron 3 duplicados exactos (L00167, L00294, L00602), quedando cada uno
con una sola ocurrencia. El código se guardó en src/clean.py.

## Transform e integración

Antes de programar este bloque se definió cómo cruzar las ventas con la
tabla de promociones, ya que esta incluye no solo el código de promoción
sino también el producto al que aplica y su rango de fechas de vigencia. Se
decidió que la transformación hace el cruce simple por código de promoción,
sin verificar si el producto o la fecha de venta coinciden con la promoción.
Esa verificación se dejó para el bloque de validación, que es el que revisa
consistencia e integridad referencial y el que decide si un desajuste
amerita detener el proceso. Antes de tomar esta decisión se comprobó con los
datos reales que no existe ningún caso de promoción aplicada a un producto
distinto o fuera de su rango de vigencia.

El bloque cruza las ventas limpias con las cuatro tablas de referencia.
Products y stores se cruzan por su identificador directo, promotions por el
código de promoción, y monthly_targets por la combinación de tienda y mes.
Para que este último cruce funcione, el mes derivado de la fecha de venta se
construye con el mismo formato de texto que ya usa la tabla de metas
(año-mes), ya que la comparación es entre textos y cualquier diferencia de
formato dejaría todas las filas sin meta asociada.

Las ventas sin promoción quedan con un porcentaje de descuento de cero en
lugar de un valor nulo, porque el descuento participa en el cálculo del
monto descontado y de la venta neta, y dejarlo nulo habría dejado esas dos
columnas vacías en la mayoría de los registros.

También se traen las fechas de inicio y fin de la promoción, aunque este
bloque no las usa, para tenerlas disponibles en la validación posterior sin
repetir el cruce contra la misma tabla.

El resultado tiene 756 filas y 25 columnas, sin ningún valor nulo en nombre
de producto, nombre de tienda ni meta de ventas. El código se guardó en
src/transform.py.

## Validate

Este bloque compara con la lógica del bloque anterior: en lugar de descartar
registros puntuales inválidos y continuar con el resto, evalúa el conjunto
completo y determina si el pipeline puede avanzar hacia la carga o debe
detenerse. Un problema detectado aquí no significa que una venta puntual
esté mal, sino que alguna etapa anterior no cumplió su función, y en ese
caso conviene revisar el conjunto completo antes de seguir.

La función no detiene nada por sí misma. Devuelve un resultado que indica si
todas las reglas pasaron, junto con una tabla del detalle de cada regla y
cuántas filas la incumplieron. La decisión de continuar o detener el
proceso, y de registrarlo en el log, queda a cargo de la orquestación
en main.py.

Se implementaron seis reglas: unicidad de sale_line_id, ausencia de nulos en
identificadores y fecha, positividad de cantidad, precio unitario, venta
bruta y venta neta, existencia de cada producto y cada tienda en su tabla
maestra, y consistencia entre la venta neta y la diferencia de la venta
bruta menos el descuento. Se agregó una séptima regla propia del equipo, que
verifica que la fecha de venta caiga dentro del periodo de vigencia de la
promoción aplicada, retomando la verificación que se había dejado pendiente
durante la transformación. Se trata como crítica porque una promoción
aplicada fuera de su vigencia dejaría mal calculada la venta neta de esa
fila.

Para comparar la venta neta contra la diferencia entre venta bruta y
descuento se usa una tolerancia mínima en lugar de igualdad exacta, porque
las operaciones con decimales pueden producir diferencias diminutas por la
forma en que se almacenan los números en memoria. Se prefirió esta
tolerancia sobre redondear los valores antes de comparar, porque redondear
podría ocultar diferencias que sí sean errores reales.

Las siete reglas pasaron sin ninguna falla sobre los datos ya limpios e
integrados. El código se guardó en src/validate.py.

## Load

Se implementaron dos funciones separadas: una que guarda el conjunto
procesado como archivo CSV en data/processed/integrated_sales.csv, y otra
que lo carga en la base de datos SQLite database/retail_analytics.db, en una
tabla llamada sales_analytics. Ninguna de las dos valida nada; ambas asumen
que quien las invoca ya confirmó que los datos son válidos.

Para la carga en la base de datos se reemplaza la tabla completa en cada
corrida en lugar de agregar registros de forma incremental. Se implementó
así porque el pipeline siempre reprocesa el conjunto completo de datos
disponible, pero queda la puerta abierta a escalar esto en caso de que la
base de datos deba actualizarse con la llegada de nuevos registros en el
futuro. No se implementó esa version incremental porque requiere de otras
decisiones de negocio y diseño que no se han definido, como una marca de
tiempo de carga o una confirmación de si cada archivo entrante representa el
total de los datos o solo un incremento.

El pipeline completo se ejecutó de punta a punta sobre los datos reales sin
errores, generando un archivo con 756 filas y 25 columnas, tanto en el CSV
procesado como en la tabla de la base de datos. El código se guardó en
src/load.py.

## Query

Se implementaron las seis consultas correspondientes a los requisitos
priorizados, leyendo únicamente desde la tabla de la base de datos y nunca
desde los archivos crudos. Cada consulta guarda su resultado como tabla en
docs/query_outputs/tablas, y las que comunican un hallazgo mas visual
(productos con menor venta, tendencia mensual, cumplimiento de metas)
generan además una gráfica de apoyo en docs/query_outputs/graficas.

Para la comparación contra el mes anterior se usó una función de ventana de
SQL, lo que permite calcular la variación directamente en la consulta en
lugar de traer los datos y procesarlos despues con codigo adicional en
pandas.

Los resultados muestran una tendencia de ventas netas a la baja mes a mes,
pasando de 62.9 millones en febrero a 57.2 millones en abril, y que solo dos
de las nueve combinaciones de tienda y mes lograron cumplir su meta de
ventas. Sobre el total del periodo se registran 756 transacciones, con 182.6
millones en ventas brutas y 181.0 millones en ventas netas después de
descuentos. El código se guardó en src/queries.py.

