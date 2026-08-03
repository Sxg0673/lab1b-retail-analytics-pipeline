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
de problema en docs/eda_outputs/graficas. Estos hallazgos son escenciales para continuar con el proceso de 
limpieza.