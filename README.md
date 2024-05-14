# AI-Scribe

## Introduction

> This is a script that I worked on to help empower physicians to alleviate the burden of documentation by utilizing a medical scribe to create SOAP notes.  Expensive solutions could potentially share personal health information with their cloud-based operations.  It utilizes `Koboldcpp` and `Whisper` on a local server that is concurrently running the `Server.py` script.  The `Client.py` script can then be used by physicians on their device to record patient-physician conversations after a signed consent is obtained and process the result into a SOAP note.
> 
> Regards,
> 
> Braedon Hendy

## Changelog

- **2024-03-17** - updated `client.py` to allow for `OpenAI` token access when `GPT` button is selected.  A prompt will show to allow for scrubbing of any personal health information.
- **2024-03-28** - updated `client.py` to allow for `Whisper` to run locally when set to `True` in the settings.
- **2024-03-29** - added `Scrubadub` to be used to remove personal information prior to `OpenAI` token access.
- **2024-04-26** - added alternative server file to use `Faster-Whisper`
- **2024-05-03** - added alternative server file to use `WhisperX`
- **2024-05-06** - added real-time `Whisper` processing
- **2024-05-13** - added `SSL` and OHIP scrubbing
- **2024-05-14** - added 'SSL' for realtime

## Setup

Example instructions for running on a single machine:

I will preface that this will run slowly if you are not using a GPU but will demonstrate the capability.  If you have an **NVidia RTX**-based card, the below instructions can be modified using `Koboldcpp.exe` rather than `koboldcpp_nocuda.exe`.

Install `Python` `3.10.9` [HERE](https://www.python.org/downloads/release/python-3109/).  (if the hyperlink doesn't work https://www.python.org/downloads/release/python-3109/).  Make sure you click the checkbox to select "`Add Python to Path`".

Press `Windows key` + `R`, you can run the command line by typing `cmd`.  Copy/type the following, running each line by pressing `Enter`: 

```sh
pip install openai-whisper
```

Next, you need to install software to convert the audio file to be processed.  Press `Windows key` + `R`, you can run the command line by typing `powershell`.  Copy/type the following:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
scoop install ffmpeg
```

Now you need to download the AI model (it is large).  I recommend the `Mistral 7B v0.2` or `Meta Llama 3` models.  These can be found on [HuggingFace.](https://huggingface.co/)

You now need to launch the AI model with the following software that you can download [HERE](https://github.com/LostRuins/koboldcpp/releases).  It will download automatically and you will need to open it (if hyperlink doesn't work https://github.com/LostRuins/koboldcpp/releases). 

Once the `koboldcpp_nocuda.exe` is opened, click the `Browse` button and select the model downloaded.  Now click the `Launch` button.

You should see a window open and can ask it questions to test!

If this was successful, you need to download the files that I wrote [HERE](https://github.com/1984Doc/AI-Scribe).  Unzip the files (if the hyperlink doesn't work https://github.com/1984Doc/AI-Scribe).

Double-click the `server.py` file.  This will download the files to help organize the text after converting from audio.

Close the window after completing and double-click the `server.py` file.

## Usage

Run the `client.py` (it may prompt for installation of various dependencies via `pip`) and click the settings button.  For each category, remove the IP address and type "`localhost`".  Please do not include quotations and click `Save`.  Close the program and re-launch.  Please verify that `Kobold` executable and `Server.py` script are running with the AI model launched.  Everything should work!  If running the client script/executable on a separate machine, please adjust the IP addresses appropriately. 
