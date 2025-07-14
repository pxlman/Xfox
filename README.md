# Xfox Gamepad Remapper

Xfox is a gamepad remapper that fixes the problem that some games require the controller to work as a xbox controller or standard controller to work well. So that Xfox Makes ur controller work as an xbox controller or standard controller. With the name of VirtualController.

## How to use
It's simple just run the script choose the input device u want to affect then it will ask u for each button what button will make this. Like: "What button will work as A?" and u can choose any button u want. After that it will ask u for the name of the virtual controller, this is the name that will be shown in the gamepad settings of the game.


## Instructions

### Using python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the remapper
python remapper.py
```

### Using the dockerfile

```bash
# Build the Docker image
sudo docker build -t gamepad-remapper .

# Run the Docker container
sudo docker run --rm -it \
  --device /dev/uinput \
  --device /dev/input \
  --cap-add=SYS_ADMIN \
  --cap-add=NET_ADMIN \
  --name remapper \
  gamepad-remapper
```
