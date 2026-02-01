# WELL Performance Verification Guidebook - Resumen para Anne

> Fuente: WELL Performance Verification Guidebook Q3-2025 (IWBI Official)
> Versión: 2025-03 | Publicado: 13 Agosto 2025

## Alcance

Este documento aplica a:
- WELL v2 Certification
- WELL Core Certification
- WELL Score
- WELL Performance Rating
- WELL Health-Safety Rating

---

## AIR CONCEPT

### Features y Parámetros

| Parámetro | WELL v2 Features | Método |
|-----------|------------------|--------|
| PM2.5, PM10 | A01.1, A01.5, A05.1 | Direct-read |
| CO | A01.3, A05.3 | Lab o Direct-read |
| Formaldehído, Acetaldehído | A01.2, A05.2 | Laboratory |
| VOCs (otros) | A01.2, A05.2 | Laboratory |
| NO2 | A05.3 | Lab o Direct-read |
| O3 | A01.3 | Lab o Direct-read |

### Densidad de Muestreo (Air)

| Área del Proyecto | Cantidad de Muestras |
|-------------------|---------------------|
| 0 - 9,290 m² | 1 por cada 2,323 m² + 1 |
| 9,290 - 46,452 m² | 1 por cada 9,290 m² + 4 |
| > 46,452 m² | 1 por cada 46,452 m² + 8 |

### Condiciones de Muestreo (Air)

- Altura: 1.1 - 1.7 m sobre el suelo
- Distancia mínima de ventanas/paredes/puertas: 1 m
- Distancia mínima de puertas exteriores: 3 m
- Ventilación mecánica: ON y operando normalmente
- Ventanas operables: CERRADAS
- Purificadores de aire: ON (velocidad media)

### Umbrales con Tolerancia (Performance Testing)

| Parámetro | Tolerancia aplicada al umbral WELL |
|-----------|-----------------------------------|
| PM2.5, PM10 | 20% |
| Formaldehído, Acetaldehído | 20% |
| VOCs (otros) | 5% |
| CO | Sin tolerancia |
| O3 | 5% |
| NO2 | 20% |

---

## THERMAL COMFORT CONCEPT

### Features y Parámetros

| Parámetro | WELL v2 Features | Método |
|-----------|------------------|--------|
| Dry bulb temperature | T01.1 | Direct-read |
| Mean radiant temperature | T01.1 | Direct-read |
| Relative humidity | T01.1, T07.1 | Direct-read |

### Densidad de Muestreo (Thermal)

| Área del Proyecto | Cantidad de Muestras |
|-------------------|---------------------|
| 0 - 9,290 m² | 1 por cada 929 m² + 3 |
| 9,290 - 46,452 m² | 1 por cada 2,323 m² + 9 |
| > 46,452 m² | 1 por cada 9,290 m² + 24 |

### Compliance (Thermal)

- **PMV**: Calcular usando valores medianos de temperatura, humedad y MRT
- **Humedad Relativa**: Valor mediano debe cumplir requisito WELL con tolerancia de ±3%

---

## CONTINUOUS MONITORING REQUIREMENTS

### Densidad de Monitores

| Área Ocupable | Densidad | Mínimo |
|---------------|----------|--------|
| < 3,250 m² | 1 monitor / 325 m² | 2 |
| 3,250 - 25,000 m² | 1 monitor / 500 m² | 10 |
| > 25,000 m² | 1 monitor / 1,000 m² | 50 |
| Radon | 1 monitor / 2,300 m² | - |

### Ubicación de Monitores

- **Pared**: Altura 1.1 - 1.7 m sobre el suelo
- **Techo**: Solo si altura ≤ 3.7 m y aire mezclado uniformemente
- **Distancia mínima**: 1 m de puertas interiores, ventanas, humidificadores, impresoras
- **Evitar**: Flujo directo de HVAC o purificadores

### Especificaciones Técnicas de Sensores

| Parámetro | Tipo Sensor | Rango | Precisión | Resolución |
|-----------|-------------|-------|-----------|------------|
| PM2.5/PM10 | Óptico/Láser | 1-1000 μg/m³ | ±5 μg/m³ + 20% | 1 μg/m³ |
| TVOC | Electroquímico/MOS | 10-2000 μg/m³ | ±20 μg/m³ + 15% | 10 μg/m³ |
| CO | Electroquímico/MOS | 0.1-25 ppm | ±1 ppm (<10 ppm) | 0.1 ppm |
| O3 | Electroquímico | 10-500 ppb | ±10 ppb (0-100) | 5 ppb |
| CO2 | NDIR | 400-5000 ppm | ±50 ppm + 5% | 1 ppm |
| NO2 | Electroquímico/MOS | 5-500 ppb | ±20 ppb (0-100) | 1 ppb |
| Temperatura | Cualquiera | 10-40°C | ±0.5°C | 0.5°C |
| Humedad | Cualquiera | 5-95% | ±5% (10-90%) | 1% |
| Radon | Alpha track | 0.1-500 pCi/L | ±5% | 0.1 pCi/L |
| HCHO | Electroquímico/MOS | 20-1000 ppb | ±20 ppb (0-100) | 1 ppb |

### Intervalos de Medición

- **Radon**: ≤ 1 hora
- **Otros parámetros**: ≤ 15 minutos

### Calibración

- Recalibrar o reemplazar sensores cada **3 años**
- Opciones:
  - Calibración del fabricante
  - Calibración de campo con sensor de referencia (mínimo 2 concentraciones)

### Cálculo de Compliance (Continuous Monitoring)

**Regla del 90%**: Al menos 90% de los datos de cada sensor durante horas ocupadas deben cumplir los umbrales.

Ejemplo: Ocupación 08:00-18:00 (10h), intervalos de 15 min, 30 días:
- 10 h/día × 4 mediciones/h × 30 días × 90% = **1,080 mediciones** deben cumplir

---

## WELL CORE GUIDANCE

Para proyectos WELL Core (solo A01, no A05):
- Calcular muestras usando área no arrendada O 2.5% del área total (lo que sea mayor)
- Si área no arrendada ≥ 2.5%: todas las muestras en espacio no arrendado
- Si área no arrendada < 2.5%: al menos 1 muestra en cada tipo de espacio

Para proyectos WELL Core (A01 + A05):
- Calcular total de muestras con área total del proyecto
- Calcular mínimo en espacio no arrendado con área no arrendada
- Resto de muestras en espacio arrendado

---

## RENEWAL REQUIREMENTS

Alcance de re-testing determinado por Renewal Tool:
- **Full**: Cantidad completa según tabla
- **Reduced**: 50% de la cantidad (mínimo 1)
- **None**: Exento de re-testing

**Nota**: Proyectos con monitoreo continuo NO son elegibles para muestreo reducido.

---

## NOTAS IMPORTANTES PARA ANNE

1. **Sin tolerancia en monitoreo continuo**: Las tolerancias solo aplican a Performance Testing, NO a datos de sensores continuos.

2. **Datos faltantes = excedencia**: En monitoreo continuo, datos perdidos se interpretan como excedencia del umbral.

3. **RESET Grade B+**: Monitores acreditados RESET Grade B o superior son aceptables para WELL.

4. **InBiot MICA WELL**: Los sensores InBiot cumplen con las especificaciones técnicas de la Tabla 3 del PVG.

5. **Unidades**: 
   - TVOC debe reportarse en μg/m³ para A01.2
   - 1 ppb TVOC = 4.57 μg/m³ (calibración etanol)

---

*Documento generado para el knowledge base de Anne - Virtual WELL AP & IAQ Expert*
*Fuente oficial: IWBI WELL Performance Verification Guidebook Q3-2025*
