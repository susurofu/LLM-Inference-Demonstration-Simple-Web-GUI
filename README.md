# Simple Web Demonstration Interface for Local LLMs

Sometimes you need a simple way to demonstrate a fine-tuned local LLM to other people without deploying it to a full production server.

This becomes slightly more complicated when:

- the model runs on only one machine with one GPU;
- several users may send requests at the same time;
- password-protected access is needed;
- remote access requires setting up a tunnel or domain;
- you want to show users a custom instruction or prompt description.

This project provides a lightweight web interface for demonstrating locally running LLMs with minimal setup.

It includes a simple control GUI for configuring the demonstration, starting the server, creating a public tunnel, and managing access.

## Features

- Run local models through Ollama.
- Set a password for access to the demonstration page.
- Configure an instruction or message displayed to users.
- Automatically install Cloudflared.
- Automatically create a Cloudflare Tunnel and generate a public access URL.
- Queue inference requests when multiple users access the model at the same time.
- Prevent multiple simultaneous requests from overloading a single-GPU machine.
- Manage the demonstration through a simple desktop control GUI.

Support for running models directly with Hugging Face Transformers may be added later.

## Supported Platforms

Currently tested on:

- macOS
- Linux

Windows support is not currently a priority, although parts of the application may still work with additional configuration.

## Requirements

Before using the application, make sure you have:

- Python installed;
- Ollama installed and running;
- at least one Ollama model downloaded;
- an internet connection if you want to create a public Cloudflare Tunnel.

For Ollama installation instructions, see the official Ollama documentation.

## Installation

1. Download or clone the project.

```bash
git clone https://github.com/susurofu/LLM-Inference-Demonstration-Simple-Web-GUI
cd lll-demo-web-gui
```

2. Navigate to the backend directory.

```bash
cd backend
```

3. Install the required Python packages.

```bash
pip install -r requirements.txt
```

If you are using a virtual environment or Conda environment, activate it before running this command.

4. Return to the project root directory.

```bash
cd ..
```

5. Make sure Ollama is installed and running.

You should also download the model you want to demonstrate beforehand. For example:

```bash
ollama pull <model-name>
```

## How to Use

The easiest way to run the application is through the control GUI.

### 1. Start the control GUI

From the project root directory, run:

```bash
python backend/gui-control.py
```

### 2. Set the instruction

Use the **Instructions** option to configure the message that users will see on the demonstration page.

You can also edit the instruction file directly:

```text
instruction.txt
```

This can contain, for example:

- a task description;
- instructions for interacting with the model;
- information about the model;
- an example prompt.

### 3. Set the access password

Use the **Set password** button in the control GUI.

Alternatively, you can configure the password from the terminal using:

```bash
python backend/set_access_password.py
```

Users will need this password before accessing the model demonstration interface.

### 4. Install Cloudflared

If Cloudflared is not installed on your machine, use the **Cloudflared** installation button in the control GUI.

The application can install Cloudflared automatically on supported systems.

Cloudflared is used to expose the local demonstration server through a temporary public Cloudflare Tunnel.

### 5. Select the model

Use **Set model** to select the Ollama model that will handle requests.

The model must already be available locally in Ollama.

You can check your installed models with:

```bash
ollama list
```
You can download models from Ollama with this script:

```bash
ollama pull <model-name> # e.g., ollama pull gemma4:31b
```

### 6. Start the server

Click **Start server**.

The application will:

1. start the local web server;
2. start the Cloudflare Tunnel;
3. generate a public access URL.

The generated URL can then be shared with your users together with the access password.

Keep the control GUI running while the demonstration is active.

The temporary Cloudflare URL may change when the tunnel is restarted, so if you stop and restart the application you may need to share the new URL.

### 7. Open the demonstration page

Users open the generated public URL and enter the password.

After successful authentication, they are redirected to the model demonstration page.

### 8. Send a prompt

Users can enter a prompt into the text field and submit it to the model.

The generated response will appear on the same page.

### 9. Request queue

If multiple users submit prompts at approximately the same time, requests are placed in a queue.

Users waiting in the queue will see their current status while previous requests are being processed.

This allows a single local model or GPU to serve multiple demonstration users without attempting to run several inference jobs simultaneously.

10. If you run it on a machine without graphic iterface (like a remote server), first, set password with set_access_password.py, modify instruction.txt and model.txt directly, naviagte to the project folder and run:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

```

In the second terminal window, run:

```bash
cloudflared tunnel --url http://127.0.0.1:8000

```

In the output, you will get the temporary url to access the demonstration web page.


## Notes

This project is intended primarily for temporary demonstrations, workshops, research presentations, and small-scale testing.

It is not designed as a production LLM serving platform.

The Cloudflare Tunnel URL generated by the application is temporary. If the tunnel is restarted, the public URL may change.

Because inference requests are processed sequentially, response time depends on the model, available hardware, prompt length, and the number of users currently waiting in the queue.



## Intended Use

This project is useful for situations such as:

- demonstrating a fine-tuned LLM during a presentation;
- allowing colleagues to test a local research model;
- running a temporary model demo during a workshop;
- sharing a model running on a laboratory workstation;
- testing prompts with several users without deploying a full inference server.