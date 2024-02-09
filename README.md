# AI-Scribe
This is a script that I worked on to help empower physicians to alleviate the burden of documentation by utilizing a medical scribe to create SOAP notes.  Expensive solutions could potentially share personal health information with their cloud-based operations.  It utilizes Koboldcpp and Whisper on a local server that is concurrently running the Server.py script.  The Client.py script or executable can then be used by physicians on their device to record patient-physician conversations after a signed consent is obtained and process the result into a SOAP note.

Regards,

Braedon Hendy

Example instructions for running on a single machine:

I will preface that this will run slowly if you are not using a GPU but will demonstrate the capability.  If you have an NVidia RTX-based card, the below instructions can be modified using Koboldcpp.exe rather than koboldcpp_nocuda.exe.

Install Python 3.10.9 HERE.  (if the hyperlink doesn't work https://www.python.org/downloads/release/python-3109/ ).  Make sure you click the checkbox to select "Add Python to Path."

Press Windows key + R, you can run the command line by typing "cmd".  Copy/type the following, running each line by pressing Enter:  

pip install openai-whisper
Next, you need to install software to convert the audio file to be processed.  Press Windows key + R, you can run the command line by typing "powershell".  Copy/type the following:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

scoop install ffmpeg

Now you need to download the AI model (it is large) from the following site.  I will link you directly to the one I trialed with my laptop HERE.  Click the download button once the window opens (if the hyperlink doesn't work https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf).

You now need to launch the AI model with the following software that you can download HERE.  It will download automatically and you will need to open it (if hyperlink doesn't workhttps://github.com/LostRuins/koboldcpp/releases). 

Once the koboldcpp_nocuda.exe is opened, click the Browse button and select the model downloaded.  Now click the Launch button.  

You should see a window open and can ask it questions to test!

If this was successful, you need to download the files that I wrote HERE.  Unzip the files (if the hyperlink doesn't work https://github.com/1984Doc/AI-Scribe).

Double-click the server.py file.  This will download the files to help organize the text after converting from audio.  

Close the window after completing and double-click the server.py file.

Open the AIScribe.exe (compiled client.py for ease of use) and click the settings button.  For each category, remove the IP address and type "localhost".  Please do not include quotations and click Save.  Close the program and re-launch.  Please verify that Kobold executable and Server.py script are running with the AI model launched.  Everything should work!  If running the client script/executable on a separate machine, please adjust the IP addresses appropriately.  
