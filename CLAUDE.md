# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a teaching materials repository for the "Big Data and Analytics" university course at Universidad San Sebastián. The repository contains Quarto-based presentation materials (.qmd files) that follow a specific pedagogical framework focused on decision-making supported by data.

## Course Philosophy and Pedagogical Framework

**Core Principle**: This course is not about tools first. It is about decision-making supported by data.

**Key Concept**: A database is a structured representation of organizational reality.

**Pedagogical Sequence**:
Decision → Information → Data → Information System → Data Model → Database → Analysis

All course materials must reflect this progression.

### Simulation-Based Learning Model

Students act as data analysts hired by an organization. All examples must revolve around a central business case that evolves throughout the semester.

**Preferred case types**:
- E-commerce
- Retail
- Delivery platform
- Service company

**Important**: Avoid abstract or purely technical examples. Everything must be grounded in realistic business scenarios.

## Presentation Structure (Quarto Slides)

Each class presentation must follow this structure:

1. **Motivating Business Problem** (realistic decision scenario)
2. **Conceptual Explanation**
3. **Applied Example**
4. **Guided Practice**
5. **Reflection and Connection to Decision-Making**

### Slide Requirements

- **Language**: All slides must be in Spanish
- Avoid excessive text
- Use diagrams whenever possible
- Include discussion questions
- Include at least one practical activity
- Clearly connect theory to managerial decision-making

## Students background

- This is a third year course, fifth semester.
- The students had a course about using Excel.
- Then, the students had a course about advanced Excel use, using Power Pivot.
- Before they have taken this course, they had a course about using Power Bi using Power Query, Sta and snowflacke scheme. Also, they know how to make dashboard in Power Bi.
- In all of the course they have taken they have worked on computer solving practical problems.

## Course Structure and File Organization

All the weeks should be organized according to:

- **Lecture**: Oral presentation of concepts for 1 hour and 20 minutes 
- **Practical Lab:** Practical lab using computer for 2 hours and 30 minutes

### Unit Duration (16-week semester)

- **Unit 1: 3 weeks** (W01–W03) — Sistemas de Información en el Contexto Empresarial
- **Unit 2: 5 weeks** (W04–W09) — Modelamiento y Arquitectura de Datos Relacionales
- **Unit 3: 8 weeks** (W10–W16) — Analítica de Datos y Programación con Python (54 hrs*)

### File Naming Convention

All files use the `W{NN}_` prefix to guarantee correct sort order in the file explorer.

- Class files: `W{NN}_clase.qmd` — placed in `clases/`
- Lab files: `W{NN}_lab.qmd` — placed in `labs/instrucciones/`
- Data files (CSV, SQL scripts): placed in `labs/data/`

| Class File | Lab File | Week | Unit | Topic |
|---|---|---|---|---|
| `W01_clase.qmd` | `W01_lab.qmd` | 1 | Unit 1 | SI, datos, componentes, actores |
| `W02_clase.qmd` | `W02_lab.qmd` | 2 | Unit 1 | Tipos de SI, CMI, calidad de datos, ética |
| `W03_clase.qmd` | `W03_lab.qmd` | 3 | Unit 1 | Big Data, OLTP/OLAP, ETL + **Solemne 1** |


## Quarto Commands

### Rendering Presentations

```bash
# Render a single presentation
quarto render clases/W01_clase.qmd

# Render all presentations (files sort correctly due to W0N_ prefix)
quarto render clases/

# Preview a presentation with live reload
quarto preview clases/W01_clase.qmd
```

### Typical Quarto Presentation YAML Header

```yaml
---
title: "Título de la Presentación"
subtitle: "Subtítulo"
author: "Big Data and Analytics"
format:
  revealjs:
    theme: default
    incremental: false
    slide-number: true
---
```

## Reference Materials

- `syllabus.md`: Contains course content, units, and learning outcomes
- `material/`: Contains reference PDFs and course materials

## Working with This Repository

When creating or modifying class presentations:

1. Always start with a realistic business problem
2. Ensure all content is in Spanish
3. Follow the pedagogical sequence (Decision → Information → Data → etc.)
4. Use the business case approach (students as data analysts)
5. Include practical activities and discussion questions
6. Connect all technical concepts to managerial decision-making
7. Use diagrams and visual representations over text-heavy slides
