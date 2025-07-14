import os
import json
import evdev
import argparse
from evdev import InputDevice, categorize, ecodes, UInput

parser = argparse.ArgumentParser(description="Xfox Remapper Tool")
parser.add_argument('--controller-id', required=False, help="The id of the controller u remapper already (found at ~/.config/xfox)")
parser.add_argument('--device', help="The controller event path (/dev/input/eventX)")
parser.add_argument('--config', help="The config directory of the app")
args = parser.parse_args()

# Define buttons you want to support in virtual device
VIRTUAL_KEYS = [
    ecodes.BTN_A, ecodes.BTN_B, ecodes.BTN_X, ecodes.BTN_Y,
    ecodes.BTN_SELECT, ecodes.BTN_START,
    ecodes.BTN_TL, ecodes.BTN_TR, ecodes.BTN_TL2, ecodes.BTN_TR2,
    ecodes.BTN_THUMBL, ecodes.BTN_THUMBR,
]

VIRTUAL_AXES = {  # axis code → (min, max, fuzz, flat, resolution)
    ecodes.ABS_X: (0, 255, 0, 0, 0),
    ecodes.ABS_Y: (0, 255, 0, 0, 0),
    ecodes.ABS_RX: (0, 255, 0, 0, 0),
    ecodes.ABS_RY: (0, 255, 0, 0, 0),
    ecodes.ABS_Z: (0, 255, 0, 0, 0),
    ecodes.ABS_RZ: (0, 255, 0, 0, 0),
}

capabilities = {
    ecodes.EV_KEY: VIRTUAL_KEYS,
    # ecodes.EV_ABS: VIRTUAL_AXES
}

def code_name(code):
    for group in [evdev.ecodes.KEY, evdev.ecodes.BTN, evdev.ecodes.ABS]:
        if code in group:
            return group[code]
    return f"UNKNOWN({code})"


def choose_device():
    devices = [InputDevice(fn) for fn in evdev.list_devices()]
    print(devices)
    for i, dev in enumerate(devices):
        print(f"[{i}] {dev.name} ({dev.path})")
    choice = int(input("Choose device index: "))
    return devices[choice]

def capture_mapping(real_dev):
    print("Start pressing buttons. Press the remapped A to skip a mapping.")
    real_dev.grab()
    mapping = {
            "buttons": {},
            # "axes": {}
            }

    for vk in VIRTUAL_KEYS:
        print(f"Press real button for virtual {ecodes.BTN[vk]}:")
        while True:
            ev = real_dev.read_one()
            if ev and ev.type == ecodes.EV_KEY and ev.value == 1:
                btn_a = None
                for r_key, v_key in mapping.get('buttons').items():
                    if v_key == ecodes.BTN_A:
                        btn_a = r_key
                if btn_a == ev.code:
                    print("Skipped remapping this button")
                    break
                mapping.get('buttons')[ev.code] = vk
                print(f"Mapped {code_name(ev.code)} → {code_name(vk)}")
                break
    real_dev.ungrab()
    mapping['name'] = input("Enter name for the virtual device: ")
    return mapping

def get_device_id(device):
    return f"{device.info.vendor:04x}:{device.info.product:04x}"

def get_device_path(device_id):
    for fn in evdev.list_devices():
        dev = InputDevice(fn)
        if get_device_id(dev) == device_id:
            return fn

def save_mapping(mapping, path):
    with open(path, "w") as f:
        json.dump(mapping, f)

def load_mapping(path):
    with open(path, "r") as f:
        raw = json.load(f)
        return {
                "name" : raw['name'],
                "buttons": {int(k): int(v) for k, v in raw["buttons"].items()},
                # "axes": {int(k): int(v) for k, v in raw["axes"].items()}
        }

def remap_loop(real_dev, mapping):
    all_keys = [code for name, code in ecodes.ecodes.items()
            if (name.startswith("BTN_"))]
    capabilities = {
        # ecodes.EV_KEY: list(mapping["buttons"].keys()),
        ecodes.EV_KEY: all_keys,
        ecodes.EV_ABS: {
            ecodes.ABS_X: (0, 255, 0, 0, 0),
            ecodes.ABS_Y: (0, 255, 0, 0, 0),
            ecodes.ABS_RX: (0, 255, 0, 0, 0),
            ecodes.ABS_RY: (0, 255, 0, 0, 0),
        },
        # ecodes.EV_MSC: [ecodes.MSC_SCAN],
    }
    real_dev.grab()
    
    try:
        with UInput(capabilities, name=mapping['name']) as ui:
            print("Remapping started. Ctrl+C to stop.")
            for event in real_dev.read_loop():
                if event.type == ecodes.EV_KEY:
                    v_key = mapping['buttons'].get(event.code)
                    # If the key is setten use it if not forward as is
                    if v_key:
                        ui.write(ecodes.EV_KEY, v_key, event.value)
                    else:
                        ui.write(event.type, event.code, event.value)
                else:
                    ui.write(event.type, event.code, event.value)

                ui.syn()
    finally:
        real_dev.ungrab()
        print("Remapping stopped.")

if __name__ == "__main__":
    device_id = real_dev = config_dir = None
    if args.controller_id:
        device_id = args.controller_id
        real_dev = InputDevice(get_device_path(device_id))
    else:
        if args.device:
            real_dev = InputDevice(args.device)
            device_id = get_device_id(real_dev)
        else:
            real_dev = choose_device()
            device_id = get_device_id(real_dev)
    
    if args.config:
        config_dir = args.config
    else:
        config_dir = os.path.join(os.path.expanduser("~"), '.config', 'xfox') 
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir,device_id+'.json')
    if os.path.exists(config_path):
        print("Loading existing mapping.")
        mapping = load_mapping(config_path)
    else:
        mapping = capture_mapping(real_dev)
        save_mapping(mapping, config_path)

    remap_loop(real_dev, mapping)

