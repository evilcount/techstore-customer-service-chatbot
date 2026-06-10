# TechStore Plus Troubleshooting Manual

Diagnostic flows for common customer support scenarios

Audience: technical support agents.

This is original synthetic documentation generated for the TechStore Plus RAG project. It is inspired by common e-commerce support, warranty, fulfillment, and security concepts, but it is not copied from any external source and is not legal advice.

## 1.1 Laptop Power, Battery, and Thermal Issues: Agent Workflow

For technical support agents, this section defines how TechStore Plus handles customer expectations when a content creator contacts support about a 4K monitor and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a USB-C docking station and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a noise-canceling headset and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a mechanical keyboard and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| gaming notebook: router disconnects during video calls | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:1:1 |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:1:2 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:1:3 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:1:4 |

## 1.2 Laptop Power, Battery, and Thermal Issues: Edge Case

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a USB-C docking station and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a engineering student contacts support about a noise-canceling headset and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a mechanical keyboard and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a smart home hub and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:2:1 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:2:2 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:2:3 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:2:4 |

## 1.3 Laptop Power, Battery, and Thermal Issues: Escalation Rule

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a noise-canceling headset and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a mechanical keyboard and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a content creator contacts support about a smart home hub and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a ultrabook laptop and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| tablet: customer cannot locate package | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:3:1 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:3:2 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:3:3 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:3:4 |

## 1.4 Laptop Power, Battery, and Thermal Issues: Quality Check

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a mechanical keyboard and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a smart home hub and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a ultrabook laptop and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a hybrid office employee contacts support about a engineering workstation laptop and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:4:1 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:4:2 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:4:3 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:4:4 |

## 1.5 Laptop Power, Battery, and Thermal Issues: Example Dialogue

For technical support agents, this section defines how TechStore Plus handles source metadata when a small business owner contacts support about a smart home hub and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a field technician contacts support about a ultrabook laptop and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a family account manager contacts support about a engineering workstation laptop and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a engineering student contacts support about a gaming notebook and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:5:1 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:5:2 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:5:3 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:5:4 |

## 1.6 Laptop Power, Battery, and Thermal Issues: Operational Metric

For technical support agents, this section defines how TechStore Plus handles quality audit note when a competitive gamer contacts support about a ultrabook laptop and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a engineering student contacts support about a engineering workstation laptop and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a field technician contacts support about a gaming notebook and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles customer expectations when a hybrid office employee contacts support about a smartphone and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:6:1 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:6:2 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:6:3 |
| mechanical keyboard: late delivery | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:6:4 |

## 2.1 Smartphone Charging, Display, and Sync Issues: Example Dialogue

For technical support agents, this section defines how TechStore Plus handles customer expectations when a content creator contacts support about a smart home hub and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a ultrabook laptop and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a engineering workstation laptop and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a gaming notebook and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| gaming notebook: router disconnects during video calls | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:1:1 |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:1:2 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:1:3 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:1:4 |

## 2.2 Smartphone Charging, Display, and Sync Issues: Operational Metric

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a ultrabook laptop and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a engineering student contacts support about a engineering workstation laptop and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a gaming notebook and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a smartphone and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:2:1 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:2:2 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:2:3 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:2:4 |

## 2.3 Smartphone Charging, Display, and Sync Issues: Baseline Standard

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a engineering workstation laptop and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a gaming notebook and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a content creator contacts support about a smartphone and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a tablet and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| tablet: customer cannot locate package | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:3:1 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:3:2 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:3:3 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:3:4 |

## 2.4 Smartphone Charging, Display, and Sync Issues: Customer Evidence

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a gaming notebook and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a smartphone and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a tablet and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a hybrid office employee contacts support about a mesh router and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:4:1 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:4:2 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:4:3 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:4:4 |

## 2.5 Smartphone Charging, Display, and Sync Issues: Agent Workflow

For technical support agents, this section defines how TechStore Plus handles source metadata when a small business owner contacts support about a smartphone and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a field technician contacts support about a tablet and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a family account manager contacts support about a mesh router and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a engineering student contacts support about a Wi-Fi 6 router and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:5:1 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:5:2 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:5:3 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:5:4 |

## 2.6 Smartphone Charging, Display, and Sync Issues: Edge Case

For technical support agents, this section defines how TechStore Plus handles quality audit note when a competitive gamer contacts support about a tablet and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a engineering student contacts support about a mesh router and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a field technician contacts support about a Wi-Fi 6 router and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles customer expectations when a hybrid office employee contacts support about a 4K monitor and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:6:1 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:6:2 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:6:3 |
| mechanical keyboard: late delivery | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:6:4 |

## 3.1 Router Connectivity and Wi-Fi Stability: Baseline Standard

For technical support agents, this section defines how TechStore Plus handles customer expectations when a content creator contacts support about a mesh router and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a Wi-Fi 6 router and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a 4K monitor and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a USB-C docking station and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| gaming notebook: router disconnects during video calls | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:1:1 |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:1:2 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:1:3 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:1:4 |

## 3.2 Router Connectivity and Wi-Fi Stability: Customer Evidence

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a Wi-Fi 6 router and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a engineering student contacts support about a 4K monitor and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a USB-C docking station and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a noise-canceling headset and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:2:1 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:2:2 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:2:3 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:2:4 |

## 3.3 Router Connectivity and Wi-Fi Stability: Agent Workflow

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a 4K monitor and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a USB-C docking station and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a content creator contacts support about a noise-canceling headset and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a mechanical keyboard and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| tablet: customer cannot locate package | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:3:1 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:3:2 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:3:3 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:3:4 |

## 3.4 Router Connectivity and Wi-Fi Stability: Edge Case

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a USB-C docking station and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a noise-canceling headset and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a mechanical keyboard and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a hybrid office employee contacts support about a smart home hub and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:4:1 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:4:2 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:4:3 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:4:4 |

## 3.5 Router Connectivity and Wi-Fi Stability: Escalation Rule

For technical support agents, this section defines how TechStore Plus handles source metadata when a small business owner contacts support about a noise-canceling headset and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a field technician contacts support about a mechanical keyboard and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a family account manager contacts support about a smart home hub and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a engineering student contacts support about a ultrabook laptop and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:5:1 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:5:2 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:5:3 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:5:4 |

## 3.6 Router Connectivity and Wi-Fi Stability: Quality Check

For technical support agents, this section defines how TechStore Plus handles quality audit note when a competitive gamer contacts support about a mechanical keyboard and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a engineering student contacts support about a smart home hub and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a field technician contacts support about a ultrabook laptop and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles customer expectations when a hybrid office employee contacts support about a engineering workstation laptop and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:6:1 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:6:2 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:6:3 |
| mechanical keyboard: late delivery | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:6:4 |

## 4.1 Monitor, Docking, and Peripheral Problems: Agent Workflow

For technical support agents, this section defines how TechStore Plus handles customer expectations when a content creator contacts support about a 4K monitor and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a USB-C docking station and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a noise-canceling headset and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a mechanical keyboard and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| gaming notebook: router disconnects during video calls | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:1:1 |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:1:2 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:1:3 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:1:4 |

## 4.2 Monitor, Docking, and Peripheral Problems: Edge Case

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a USB-C docking station and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a engineering student contacts support about a noise-canceling headset and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a mechanical keyboard and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a smart home hub and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:2:1 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:2:2 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:2:3 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:2:4 |

## 4.3 Monitor, Docking, and Peripheral Problems: Escalation Rule

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a noise-canceling headset and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a mechanical keyboard and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a content creator contacts support about a smart home hub and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a ultrabook laptop and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| tablet: customer cannot locate package | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:3:1 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:3:2 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:3:3 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:3:4 |

## 4.4 Monitor, Docking, and Peripheral Problems: Quality Check

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a mechanical keyboard and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a smart home hub and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a ultrabook laptop and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a hybrid office employee contacts support about a engineering workstation laptop and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:4:1 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:4:2 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:4:3 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:4:4 |

## 4.5 Monitor, Docking, and Peripheral Problems: Example Dialogue

For technical support agents, this section defines how TechStore Plus handles source metadata when a small business owner contacts support about a smart home hub and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a field technician contacts support about a ultrabook laptop and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a family account manager contacts support about a engineering workstation laptop and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a engineering student contacts support about a gaming notebook and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:5:1 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:5:2 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:5:3 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:5:4 |

## 4.6 Monitor, Docking, and Peripheral Problems: Operational Metric

For technical support agents, this section defines how TechStore Plus handles quality audit note when a competitive gamer contacts support about a ultrabook laptop and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a engineering student contacts support about a engineering workstation laptop and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a field technician contacts support about a gaming notebook and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles customer expectations when a hybrid office employee contacts support about a smartphone and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:6:1 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:6:2 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:6:3 |
| mechanical keyboard: late delivery | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:6:4 |

## 5.1 Audio, Camera, and Conferencing Troubleshooting: Baseline Standard

For technical support agents, this section defines how TechStore Plus handles customer expectations when a content creator contacts support about a engineering workstation laptop and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a gaming notebook and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a smartphone and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a tablet and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| gaming notebook: router disconnects during video calls | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:1:1 |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:1:2 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:1:3 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:1:4 |

## 5.2 Audio, Camera, and Conferencing Troubleshooting: Customer Evidence

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a gaming notebook and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a engineering student contacts support about a smartphone and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a tablet and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a mesh router and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:2:1 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:2:2 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:2:3 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:2:4 |

## 5.3 Audio, Camera, and Conferencing Troubleshooting: Agent Workflow

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a smartphone and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a tablet and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a content creator contacts support about a mesh router and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a Wi-Fi 6 router and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| tablet: customer cannot locate package | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:3:1 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:3:2 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:3:3 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:3:4 |

## 5.4 Audio, Camera, and Conferencing Troubleshooting: Edge Case

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a tablet and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a mesh router and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a Wi-Fi 6 router and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a hybrid office employee contacts support about a 4K monitor and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:4:1 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:4:2 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:4:3 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:4:4 |

## 5.5 Audio, Camera, and Conferencing Troubleshooting: Escalation Rule

For technical support agents, this section defines how TechStore Plus handles source metadata when a small business owner contacts support about a mesh router and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a field technician contacts support about a Wi-Fi 6 router and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a family account manager contacts support about a 4K monitor and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a engineering student contacts support about a USB-C docking station and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:5:1 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:5:2 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:5:3 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:5:4 |

## 5.6 Audio, Camera, and Conferencing Troubleshooting: Quality Check

For technical support agents, this section defines how TechStore Plus handles quality audit note when a competitive gamer contacts support about a Wi-Fi 6 router and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a engineering student contacts support about a 4K monitor and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a field technician contacts support about a USB-C docking station and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles customer expectations when a hybrid office employee contacts support about a noise-canceling headset and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:6:1 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:6:2 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:6:3 |
| mechanical keyboard: late delivery | Verify order, collect evidence, route via audio, workflow | 03_techstore_troubleshooting_manual:6:4 |

## 6.1 When to Escalate to Repair or Replacement: Agent Workflow

For technical support agents, this section defines how TechStore Plus handles customer expectations when a content creator contacts support about a 4K monitor and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a USB-C docking station and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a noise-canceling headset and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a mechanical keyboard and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 1-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| gaming notebook: router disconnects during video calls | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:1:1 |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:1:2 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:1:3 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:1:4 |

## 6.2 When to Escalate to Repair or Replacement: Edge Case

For technical support agents, this section defines how TechStore Plus handles agent next action when a field technician contacts support about a USB-C docking station and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a engineering student contacts support about a noise-canceling headset and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a mechanical keyboard and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a smart home hub and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 2-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| smartphone: screen flickers after sleep mode | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:2:1 |
| tablet: customer cannot locate package | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:2:2 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:2:3 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:2:4 |

## 6.3 When to Escalate to Repair or Replacement: Escalation Rule

For technical support agents, this section defines how TechStore Plus handles escalation trigger when a remote consultant contacts support about a noise-canceling headset and reports order shows delivered but is missing. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles exception handling when a competitive gamer contacts support about a mechanical keyboard and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a content creator contacts support about a smart home hub and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a ultrabook laptop and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 3-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| tablet: customer cannot locate package | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:3:1 |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:3:2 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:3:3 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:3:4 |

## 6.4 When to Escalate to Repair or Replacement: Quality Check

For technical support agents, this section defines how TechStore Plus handles exception handling when a engineering student contacts support about a mechanical keyboard and reports device will not power on. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles source metadata when a hybrid office employee contacts support about a smart home hub and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a engineering student contacts support about a ultrabook laptop and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a hybrid office employee contacts support about a engineering workstation laptop and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 4-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| mesh router: order shows delivered but is missing | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:4:1 |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:4:2 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:4:3 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:4:4 |

## 6.5 When to Escalate to Repair or Replacement: Example Dialogue

For technical support agents, this section defines how TechStore Plus handles source metadata when a small business owner contacts support about a smart home hub and reports payment authorization failed. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles quality audit note when a field technician contacts support about a ultrabook laptop and reports customer needs a replacement before travel. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a family account manager contacts support about a engineering workstation laptop and reports battery drains quickly. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a engineering student contacts support about a gaming notebook and reports screen flickers after sleep mode. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 5-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| Wi-Fi 6 router: device will not power on | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:5:1 |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:5:2 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:5:3 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:5:4 |

## 6.6 When to Escalate to Repair or Replacement: Operational Metric

For technical support agents, this section defines how TechStore Plus handles quality audit note when a competitive gamer contacts support about a ultrabook laptop and reports warranty claim lacks serial number. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-1 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles eligibility when a engineering student contacts support about a engineering workstation laptop and reports late delivery. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-2 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles documentation when a field technician contacts support about a gaming notebook and reports router disconnects during video calls. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-3 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

For technical support agents, this section defines how TechStore Plus handles customer expectations when a hybrid office employee contacts support about a smartphone and reports customer cannot locate package. The agent should collect the minimum useful facts, confirm the customer's goal, and keep the answer grounded in the relevant policy or product record. If the case includes urgency, safety risk, a high-value shipment, repeated failure, or an unresolved warranty decision, the agent should identify the correct escalation path before promising a remedy. Scenario marker 6-4 is unique for retrieval testing and helps confirm that ChromaDB can recover this passage.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| 4K monitor: payment authorization failed | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:6:1 |
| USB-C docking station: warranty claim lacks serial number | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:6:2 |
| noise-canceling headset: customer needs a replacement before travel | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:6:3 |
| mechanical keyboard: late delivery | Verify order, collect evidence, route via when workflow | 03_techstore_troubleshooting_manual:6:4 |

## Appendix 37: Laptop Power, Battery, and Thermal Issues Scenario Library

Case study: A small business owner purchased a engineering workstation laptop and contacted TechStore Plus because late delivery. The agent first verified the order context, then separated what was known from what still needed evidence. The response avoided broad promises and explained the next checkpoint in plain language. This pattern supports retrieval because the case contains product, issue, evidence, and next-action signals in one passage.

Decision note for Laptop Power, Battery, and Thermal Issues: agents should choose the narrowest reliable answer. When a document does not contain a final remedy, the correct answer is to state the known policy boundary and request the missing evidence. This is especially important for warranty exclusions, delivery disputes, account recovery, and payment-risk cases.

Agent guidance: acknowledge the customer concern, name the relevant TechStore process, ask for the order number or serial number when needed, and summarize the next action. Do not invent coverage, shipping dates, repair outcomes, discounts, or security status. Use retrieved context as the source of truth and cite the source title when available.

Quality note: a strong answer for this topic is concise, specific, and verifiable. It should contain the policy window, customer evidence, product category, ownership team, and escalation threshold when those details are present. A weak answer repeats generic reassurance without connecting the customer request to a documented rule.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| gaming notebook: warranty claim lacks serial number | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:37:1 |
| smartphone: customer needs a replacement before travel | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:37:2 |
| tablet: late delivery | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:37:3 |
| mesh router: battery drains quickly | Verify order, collect evidence, route via laptop workflow | 03_techstore_troubleshooting_manual:37:4 |

## Appendix 38: Smartphone Charging, Display, and Sync Issues Scenario Library

Case study: A competitive gamer purchased a gaming notebook and contacted TechStore Plus because battery drains quickly. The agent first verified the order context, then separated what was known from what still needed evidence. The response avoided broad promises and explained the next checkpoint in plain language. This pattern supports retrieval because the case contains product, issue, evidence, and next-action signals in one passage.

Decision note for Smartphone Charging, Display, and Sync Issues: agents should choose the narrowest reliable answer. When a document does not contain a final remedy, the correct answer is to state the known policy boundary and request the missing evidence. This is especially important for warranty exclusions, delivery disputes, account recovery, and payment-risk cases.

Agent guidance: acknowledge the customer concern, name the relevant TechStore process, ask for the order number or serial number when needed, and summarize the next action. Do not invent coverage, shipping dates, repair outcomes, discounts, or security status. Use retrieved context as the source of truth and cite the source title when available.

Quality note: a strong answer for this topic is concise, specific, and verifiable. It should contain the policy window, customer evidence, product category, ownership team, and escalation threshold when those details are present. A weak answer repeats generic reassurance without connecting the customer request to a documented rule.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| smartphone: customer needs a replacement before travel | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:38:1 |
| tablet: late delivery | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:38:2 |
| mesh router: battery drains quickly | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:38:3 |
| Wi-Fi 6 router: router disconnects during video calls | Verify order, collect evidence, route via smartphone workflow | 03_techstore_troubleshooting_manual:38:4 |

## Appendix 39: Router Connectivity and Wi-Fi Stability Scenario Library

Case study: A family account manager purchased a smartphone and contacted TechStore Plus because router disconnects during video calls. The agent first verified the order context, then separated what was known from what still needed evidence. The response avoided broad promises and explained the next checkpoint in plain language. This pattern supports retrieval because the case contains product, issue, evidence, and next-action signals in one passage.

Decision note for Router Connectivity and Wi-Fi Stability: agents should choose the narrowest reliable answer. When a document does not contain a final remedy, the correct answer is to state the known policy boundary and request the missing evidence. This is especially important for warranty exclusions, delivery disputes, account recovery, and payment-risk cases.

Agent guidance: acknowledge the customer concern, name the relevant TechStore process, ask for the order number or serial number when needed, and summarize the next action. Do not invent coverage, shipping dates, repair outcomes, discounts, or security status. Use retrieved context as the source of truth and cite the source title when available.

Quality note: a strong answer for this topic is concise, specific, and verifiable. It should contain the policy window, customer evidence, product category, ownership team, and escalation threshold when those details are present. A weak answer repeats generic reassurance without connecting the customer request to a documented rule.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| tablet: late delivery | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:39:1 |
| mesh router: battery drains quickly | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:39:2 |
| Wi-Fi 6 router: router disconnects during video calls | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:39:3 |
| 4K monitor: screen flickers after sleep mode | Verify order, collect evidence, route via router workflow | 03_techstore_troubleshooting_manual:39:4 |

## Appendix 40: Monitor, Docking, and Peripheral Problems Scenario Library

Case study: A hybrid office employee purchased a tablet and contacted TechStore Plus because screen flickers after sleep mode. The agent first verified the order context, then separated what was known from what still needed evidence. The response avoided broad promises and explained the next checkpoint in plain language. This pattern supports retrieval because the case contains product, issue, evidence, and next-action signals in one passage.

Decision note for Monitor, Docking, and Peripheral Problems: agents should choose the narrowest reliable answer. When a document does not contain a final remedy, the correct answer is to state the known policy boundary and request the missing evidence. This is especially important for warranty exclusions, delivery disputes, account recovery, and payment-risk cases.

Agent guidance: acknowledge the customer concern, name the relevant TechStore process, ask for the order number or serial number when needed, and summarize the next action. Do not invent coverage, shipping dates, repair outcomes, discounts, or security status. Use retrieved context as the source of truth and cite the source title when available.

Quality note: a strong answer for this topic is concise, specific, and verifiable. It should contain the policy window, customer evidence, product category, ownership team, and escalation threshold when those details are present. A weak answer repeats generic reassurance without connecting the customer request to a documented rule.

| Signal | Support action | RAG retrieval clue |
| --- | --- | --- |
| mesh router: battery drains quickly | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:40:1 |
| Wi-Fi 6 router: router disconnects during video calls | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:40:2 |
| 4K monitor: screen flickers after sleep mode | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:40:3 |
| USB-C docking station: customer cannot locate package | Verify order, collect evidence, route via monitor, workflow | 03_techstore_troubleshooting_manual:40:4 |
