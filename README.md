# Kat AI

## Overview

Kat AI is an intelligent application designed to assist users in executing tasks through natural language prompts. Utilizing OpenAI's API, it generates responses and suggestions based on user inputs, managing the operational state and interface with Docker containers.

## Features

- **User Interaction Loop**: Continuously accepts user input until 'exit' is typed.
- **AI Querying**: Sends user prompts to OpenAI for generating relevant responses.
- **Command Execution**: Executes Docker commands based on AI suggestions to perform tasks.
- **State Management**: Maintains context and completed steps for continuity in user interactions.
- **Docker Integration**: Safely executes Docker commands for managing containers.

## Directory Structure

```
$(ls -R kat-ai)
```

## Installation

To install the necessary dependencies, run:

```
apt-get update && apt-get install -y python3 git
```

## Usage

To run the application, execute:

```
python3 kat-ai/app/main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss improvements.

## License

This project is licensed under the MIT License.
