import os
from argparse import ArgumentParser

import ai2thor
import compress_json
from ai2thor.controller import Controller
from ai2thor.hooks.procedural_asset_hook import ProceduralAssetHookRunner

from ai2holodeck.constants import (
    HOLODECK_BASE_DATA_DIR,
    THOR_COMMIT_ID,
    OBJATHOR_ASSETS_DIR,
)

parser = ArgumentParser()
parser.add_argument(
    "--scene",
    help="the directory of the scene to be generated",
    default=os.path.join(
        HOLODECK_BASE_DATA_DIR, "/scenes/a_living_room/a_living_room.json"
    ),
)
parser.add_argument(
    "--asset_dir",
    help="the directory of the assets to be used",
    default=OBJATHOR_ASSETS_DIR,
)
args = parser.parse_args()
#args.scene = "./data/scenes/a_living_room-2024-11-22-22-58-37-890479/a_living_room.json"
args.scene = "data/scenes/a_baby_room_with_many_toys-2024-12-01-23-12-11-777673/a_baby_room_with_many_toys.json"
scene = compress_json.load(args.scene)

controller = Controller(
    commit_id=THOR_COMMIT_ID,
    start_unity=False,
    port=9050,
    scene="Procedural",
    gridSize=0.25,
    width=300,
    height=300,
    server_class=ai2thor.wsgi_server.WsgiServer,
    makeAgentsVisible=False,
    visibilityScheme="Distance",
    action_hook_runner=ProceduralAssetHookRunner(
        asset_directory=args.asset_dir,
        asset_symlink=True,
        verbose=True,
    ),
)


controller.step(action="CreateHouse", house=scene)
print("controller reset")
