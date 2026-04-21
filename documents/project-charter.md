# FraudLens Project Charter

## Overview

FraudLens is a banking fraud analytics platform designed as a realistic, portfolio-grade data program. The project models payments, accounts, customer interactions, fraud risk, and case management using structured contracts that can later support warehouse design, dbt transformations, operational monitoring, and BI delivery.

## Problem Statement

Fraud analytics programs often suffer from fragmented payment data, inconsistent business definitions, and weak traceability between detection logic, operational case handling, and reported outcomes. FraudLens addresses that gap by defining a governed data foundation before implementation begins.

## Business Objectives

- establish a credible banking and fraud operating model
- preserve consistent definitions for payments, accounts, risk, alerts, and cases
- support analytics, controls, and auditability from the start
- enable future implementation without redesigning core entity boundaries

## Architecture Position

- Medallion data architecture remains the target implementation pattern
- Snowflake remains the intended analytical platform
- dbt remains the intended transformation framework
- Airflow remains the intended orchestration layer
- Power BI remains the intended BI endpoint

Phase 0 does not implement those components. It defines the governed contract structure that later phases will realize.

## Modeling Direction

- ISO 20022-inspired semantics for payment instructions, payment transactions, parties, accounts, amounts, and currency handling
- BIAN-inspired domain grouping for business object boundaries
- custom fraud operations entities for risk assessment, alerting, investigations, decisions, and case dispositions

## Non-Negotiable Principles

- no manual business data manipulation as a normal operating path
- all critical entities have ownership and control metadata
- auditability is designed into contracts, not added later
- business naming must remain stable across later implementation layers
