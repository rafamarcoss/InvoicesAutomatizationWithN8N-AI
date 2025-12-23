🌸 Automated Invoicing System for a Local Florist
📌 Project Overview

This project is an automated invoicing system designed for a small neighborhood florist.
Originally, the business created invoices manually by printing paper templates, writing data by hand, and later scanning or delivering them to customers. This process was slow, error-prone, and inefficient.

The goal of this project is to automate invoice generation using modern tools while keeping the workflow simple and realistic for a small business.

The system generates PDF invoices automatically from natural language messages (e.g. WhatsApp orders), without any online sales or e-commerce.

🧠 Purpose of the Project

  This project was built as a learning-focused initiative to:

  Understand Linux server environments (Ubuntu Server)

  Learn Docker and Docker Compose for service orchestration

  Design a clean microservice architecture

  Explore automation workflows with n8n

  Take first steps into AI-assisted automation using a mock AI service

It is both an educational project and a base that could be adapted for other local businesses.

🛠️ Technologies Used

Ubuntu Server (virtualized environment)

Docker & Docker Compose

Python

Flask (HTTP microservices)

ReportLab (write text at fixed PDF coordinates)

PyPDF2 (merge dynamic content with an existing PDF template)

n8n (workflow automation)

Mock AI service (natural language → structured JSON)

No HTML, CSS, or web-based PDF generation is used.

⚙️ How the System Works

A message is received (e.g. a customer order via WhatsApp)

n8n orchestrates the workflow

A mock AI service converts text into structured invoice data (JSON)

A Python PDF service writes data directly onto a PDF template

The final invoice PDF is generated and stored automatically

🎯 Conclusion

This project represents my first practical steps into AI and automation.
Artificial intelligence is not a future concept — it is already here, and learning how to integrate it with real-world systems is essential.

This repository documents that learning journey.
