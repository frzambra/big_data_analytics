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

### Unit 1 Structure
- **Total duration**: 36 teaching hours (40 minutes each)
- **Organization**: 3 modules per teaching day, 2 hours (80 minutes) per module
- **Teaching days**: 6 days total
- **Content mix**: Each teaching day should mix concept and applied concept with examples

### File Naming Convention

Class files should be named as:
- `class_week_1.qmd`
- `class_week_2.qmd`
- `class_week_3.qmd`
- `class_week_4.qmd`
- `class_week_5.qmd`
- `class_week_6.qmd`

All class files should be placed in the `clases/` directory.

## Quarto Commands

### Rendering Presentations

```bash
# Render a single presentation
quarto render clases/class_week_1.qmd

# Render all presentations
quarto render clases/

# Preview a presentation with live reload
quarto preview clases/class_week_1.qmd
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
