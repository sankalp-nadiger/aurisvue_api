### 1. Track Chosen:
AI in Cyber Security
### 2. Problem Statement:
In today’s digital world, **evidence** is often collected from smartphones, CCTV footage, digital documents, and online sources. But securing and verifying this evidence is a huge **challenge**—especially when **deepfakes**, **metadata tampering**, and **file manipulation** are easier than ever. Most current systems also require constant internet access and don’t work well in field conditions. This puts justice at risk. Law enforcement teams need a secure, AI-driven solution that works even when they're offline and keeps evidence safe, verifiable, and legally admissible.

### 3. Introduction: (Team PacketNinjas)
We’re a team of developers and tech enthusiasts passionate about AI, cybersecurity, and social impact. Our project, **LawVault**, is a secure web & app based platform designed to help law enforcement officers, forensic teams, and legal professionals collect, verify, and store digital evidence safely—even in tough conditions. We’re blending AI, encryption, and blockchain to build something that’s not just technically strong, but actually useful in the real world.

### 4. Proposed Solution:
LawVault is a browser-based digital evidence platform that uses AI to verify the authenticity of files and blockchain to keep them tamper-proof. Officers can upload photos, videos, or documents—even from remote or offline locations—and the system will verify metadata, detect manipulation (like deepfakes or Photoshop), and lock it into an immutable blockchain ledger. Once they’re back online, everything syncs securely. There’s also an AI chatbot for legal support, and geo-fencing to restrict who can view certain files. It’s fast, secure, and built for people who need to trust their tools.


### 5. Solution Description:
Here’s what LawVault will do:

📁 **Evidence Upload & Decentralized Sync**: Users can upload digital evidence through the web app. Files are encrypted locally and stored on IPFS, while their hash and metadata are logged on a blockchain for a tamper-proof chain-of-custody. Offline uploads sync automatically when connectivity is restored.

🧠 **AI Verification Engine**: As soon as a file is uploaded, AI checks for tampering—whether it’s a manipulated image, altered timestamp, or deepfake video.

🛡️ **Blockchain Integrity**: Every action on a file—upload, view, update—is hashed and stored on a private blockchain to build an unbreakable chain of custody.

🔐 **Role-Based Access**: Only authorized users (like investigators or attorneys) can access specific files. Geo-fencing and time limits add an extra layer of control.

📊 **Crime Timeline**: The platform links timestamps, locations, and files to automatically build a visual crime timeline—helping investigators connect the dots faster.

📚 **Legal Chatbot (Powered by LLaMA)**: An open-source AI assistant that answers legal and procedural questions in real time. It’s privacy-friendly, customizable, and doesn’t rely on external APIs.

We've attached the Architecture Diagram below

![image](http://bit.ly/44lrO9V)

### 6. Tech Stack:
![image](https://bit.ly/4jXiSvR)

**Frontend (Web App)**:

React.js — For a fast, modern, and responsive web interface.

PWA (Progressive Web App) — Enables offline-first functionality and background syncing.

**Backend**:

Node.js + Express — A lightweight, scalable server for handling API requests and syncing with blockchain and IPFS.

SQLite (Offline Storage) + PostgreSQL (Online Database) — To handle offline and online storage of metadata and logs.

RESTful APIs — To keep services modular and interoperable.

**AI/ML**:

OpenCV + TensorFlow — For media integrity checks (image/video tampering, deepfake detection).

Tesseract OCR — For extracting text and metadata from scanned documents or images.

LLaMA API — An open-source LLM-based chatbot for answering legal and forensic questions.

**Security**:

AES-256 Encryption — To protect evidence locally on the device.

JWT (JSON Web Tokens) — For secure, stateless user authentication.

Geo-Fencing — Adds access restrictions based on user location and device.

Blockchain & Decentralized Storage:

Ethereum Testnet or Hyperledger Fabric — For storing immutable logs of evidence actions (chain of custody).

IPFS (InterPlanetary File System) — For decentralized storage of actual evidence files (photos, videos, documents).

Web3.js — To connect the frontend with blockchain-based smart contracts and verify evidence integrity.

Why this stack? 
This setup balances performance, scalability, and offline capability. React and Node.js speed up development, while IPFS + blockchain ensure that evidence is tamper-proof and independently verifiable. LLaMA gives us full control over the legal assistant chatbot without relying on closed APIs.
