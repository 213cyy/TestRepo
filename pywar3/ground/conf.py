root, folder, file = __file__.rsplit('\\', 2)
ROOT = root + "/"

SUB_ROOT = ROOT+folder + "/"

WAR3_ENVIRONMENT_FILE = SUB_ROOT + "111.w3m/war3map.w3e"
GROUND_SHADER_FOLDER = SUB_ROOT + "Shaders/"

GROUND_TEXTURE_FOLDER = SUB_ROOT + "TerrainArt/LordaeronSummer/"
texter_folder = GROUND_TEXTURE_FOLDER
file_extension=".blp"
file_extension=".tga"
TILESET_ID_TO_FILENAME = {
    "Ldrt": texter_folder + "Lords_Dirt" + file_extension,
    "Ldro": texter_folder + "Lords_DirtRough" + file_extension,
    "Ldrg": texter_folder + "Lords_DirtGrass" + file_extension,
    "Lrok": texter_folder + "Lords_Rock" + file_extension,
    "Lgrs": texter_folder + "Lords_Grass" + file_extension,
    "Lgrd": texter_folder + "Lords_GrassDark" + file_extension,
}

WATER_TEXTURE_FOLDER = SUB_ROOT + "TerrainArt/Water/"


def WATER_INDEX_TO_FILENAME(
    index): return f"{WATER_TEXTURE_FOLDER}Water{index:02}.blp"

# data from UI\MiscData.txt
WATER_MINDEPTH=10
WATER_DEEPLEVEL=64
WATER_MAXDEPTH=72

# data from TerrainArt\Water.slk
WATER_ZERO_LEVEL = -0.7 * 128  # = -89.6
WATER_TEXTURES_NUM = 45
WATER_SHALLOW_COLOR_MIN = [255, 255, 255, 10]
WATER_SHALLOW_COLOR_MAX = [117, 117, 200, 219]
WATER_DEEP_COLOR_MIN = [117, 117, 200, 219]
WATER_DEEP_COLOR_MAX = [96, 96, 192, 250]

###############################################
CLIFF_TEXTURE_FOLDER = SUB_ROOT + "TerrainArt/Cliffs/"