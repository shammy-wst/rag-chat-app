# RAG Chatbot with Google Drive Integration

A chatbot application using RAG (Retrieval Augmented Generation) with Google Drive integration.

## Setup

1. Create virtual environment: `python3 -m venv venv`
2. Activate virtual environment: `source venv/bin/activate`
3. Install dependencies: `python3 -m pip install -r requirements.txt`

## Features

- Google Drive PDF integration
- RAG implementation with Ollama
- Temperature control for LLM responses
- Simple web interface with Streamlit

## Overview

This project implements a chatbot that combines RAG (Retrieval Augmented Generation) capabilities with Google Drive integration. It allows users to interact with PDF documents stored in Google Drive through a conversational interface powered by Ollama LLM.

## Prerequisites

- Python 3.8+
- Google Cloud Platform account with OAuth 2.0 credentials
- Ollama installed locally

## Installation

## Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the Google Drive API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app"
   - Download the JSON file
   - Place it in `credentials/oauth_credentials.json`

## Ollama Setup

1. Install Ollama following instructions at [ollama.ai](https://ollama.ai)
2. Pull the required model:

   ```bash
   ollama pull mistral
   ```

## Project Structure

1. Create virtual environment:
